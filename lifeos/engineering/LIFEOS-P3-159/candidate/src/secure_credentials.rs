use aes_gcm::{
    aead::{AeadInPlace, KeyInit},
    Aes256Gcm, Nonce, Tag,
};
use rand::{rngs::OsRng, RngCore};
use security_framework::os::macos::keychain::SecKeychain;
#[cfg(test)]
use std::collections::BTreeMap;
use zeroize::Zeroize;

pub const KEYCHAIN_SERVICE: &str = "com.lifeos.p3-152.aead-key.v1";
pub const LEGACY_P3_144_KEYCHAIN_SERVICE: &str = "com.lifeos.p3-144.aead-key.v1";
pub const ALGORITHM: &str = "AES-256-GCM";
pub const VERSION: u8 = 1;

const P3_144_REFERENCE_PREFIX: &str = "p3-144-key-";
const P3_145_REFERENCE_PREFIX: &str = "p3-152-key-";
const REFERENCE_RANDOM_HEX_LENGTH: usize = 32;
const ERR_SEC_ITEM_NOT_FOUND: i32 = -25300;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CredentialFailure {
    InvalidInput,
    KeyReferenceRejected,
    KeychainUnavailable,
    KeychainInteractionRequired,
    KeychainMissing,
    EncryptionFailed,
    AuthenticationFailed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CredentialLineage {
    P3_144,
    P3_145,
}

impl CredentialLineage {
    pub const fn keychain_service(self) -> &'static str {
        match self {
            Self::P3_144 => LEGACY_P3_144_KEYCHAIN_SERVICE,
            Self::P3_145 => KEYCHAIN_SERVICE,
        }
    }
}

#[derive(Clone, Debug)]
pub struct EncryptedCredential {
    pub ciphertext: Vec<u8>,
    pub nonce: Vec<u8>,
    pub tag: Vec<u8>,
    pub key_reference: String,
    pub algorithm: &'static str,
    pub version: u8,
}

pub trait CredentialPort {
    fn add_generic_password(
        &mut self,
        service: &str,
        reference: &str,
        material: &[u8],
    ) -> Result<(), CredentialFailure>;

    fn find_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<Vec<u8>, CredentialFailure>;

    fn delete_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<(), CredentialFailure>;
}

struct MacosCredentialPort;
// Serialize this process's legacy Keychain policy and operations; never change item ACLs.
static KEYCHAIN_OPERATION:std::sync::Mutex<()>=std::sync::Mutex::new(());
// Fixed stage and numeric OSStatus only. Thread-local and cleared for each check;
// no account, service, reference, material or OS error description is retained.
thread_local!{static READ_DIAGNOSTIC:std::cell::Cell<(&'static str,Option<i32>)>=const{std::cell::Cell::new(("configuration_binding",None))};}
pub(crate) fn read_diagnostic()->(&'static str,Option<i32>){READ_DIAGNOSTIC.with(|v|v.get())}
pub(crate) fn read_stage(stage:&'static str,status:Option<i32>){READ_DIAGNOSTIC.with(|v|v.set((stage,status)));}

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub(crate) struct ReadDiagnostic { stage: &'static str, os_status: Option<i32> }
impl ReadDiagnostic {
 pub(crate) fn new(stage:&str,status:Option<i32>)->Self {
  let stage=match stage { "configuration_binding"=>"configuration_binding","concurrent_busy"=>"concurrent_busy","process_policy"=>"process_policy","default_keychain"=>"default_keychain","single_item_read"=>"single_item_read","complete"=>"complete","worker_busy"=>"worker_busy","worker_timeout"=>"worker_timeout","worker_disconnected"=>"worker_disconnected","worker_unavailable"=>"worker_unavailable",_=>"diagnostic_unavailable"};
  let os_status=if matches!(stage,"process_policy"|"default_keychain"|"single_item_read"){status}else{None};Self{stage,os_status}
 }
 pub(crate) fn capture()->Self {let(s,n)=read_diagnostic();Self::new(s,n)}
 pub(crate) fn value(self)->serde_json::Value {serde_json::json!({"stage":self.stage,"osStatus":self.os_status})}
}
fn noninteractive_lookup_failure(status:i32)->CredentialFailure {
 read_stage("single_item_read",Some(status));
 if status == -25308 {CredentialFailure::KeychainInteractionRequired}else{lookup_failure_from_status(status)}
}

/// Purpose-specific read-only access. A skipped authentication requirement pauses
/// the engine; it never falls back to an interactive lookup or changes any ACL.
pub(crate) struct NonInteractiveCredentialPort;
impl CredentialPort for NonInteractiveCredentialPort {
 fn add_generic_password(&mut self,_:&str,_:&str,_:&[u8])->Result<(),CredentialFailure>{Err(CredentialFailure::KeychainUnavailable)}
 fn delete_generic_password(&mut self,_:&str,_:&str)->Result<(),CredentialFailure>{Err(CredentialFailure::KeychainUnavailable)}
 fn find_generic_password(&mut self,service:&str,reference:&str)->Result<Vec<u8>,CredentialFailure>{
  with_noninteractive_policy(&MacosInteractionPolicy,||{
   let chain=keychain()?;read_stage("single_item_read",None);
   let (password,_)=chain.find_generic_password(service,reference).map_err(|e|noninteractive_lookup_failure(e.code()))?;
   read_stage("single_item_read",Some(0));
   Ok(password.as_ref().to_vec())
  })
 }
}

trait InteractionPolicy{type Guard;fn allowed(&self)->Result<bool,CredentialFailure>;fn disable(&self)->Result<Self::Guard,CredentialFailure>;}
struct MacosInteractionPolicy;
impl InteractionPolicy for MacosInteractionPolicy{
 type Guard=security_framework::os::macos::keychain::KeychainUserInteractionLock;
 fn allowed(&self)->Result<bool,CredentialFailure>{read_stage("process_policy",None);SecKeychain::user_interaction_allowed().map_err(|e|{read_stage("process_policy",Some(e.code()));CredentialFailure::KeychainUnavailable})}
 fn disable(&self)->Result<Self::Guard,CredentialFailure>{SecKeychain::disable_user_interaction().map_err(|e|{read_stage("process_policy",Some(e.code()));CredentialFailure::KeychainUnavailable})}
}
fn with_noninteractive_policy<I:InteractionPolicy,T>(policy:&I,lookup:impl FnOnce()->Result<T,CredentialFailure>)->Result<T,CredentialFailure>{
 read_stage("concurrent_busy",None);
 let _operation=KEYCHAIN_OPERATION.try_lock().map_err(|_|CredentialFailure::KeychainUnavailable)?;
 // The OS library guard restores true on Drop; only create it if true was
 // the previous state. Previously disabled state is never enabled here.
 let _no_ui=if policy.allowed()?{Some(policy.disable()?)}else{None};
 lookup()
}
fn with_manual_read_policy<I:InteractionPolicy,T>(policy:&I,lookup:impl FnOnce()->Result<T,CredentialFailure>)->Result<T,CredentialFailure>{
 read_stage("concurrent_busy",None);
 let _operation=KEYCHAIN_OPERATION.try_lock().map_err(|_|CredentialFailure::KeychainUnavailable)?;
 let _allowed=policy.allowed()?; // Observe only. Never enable a disabled policy.
 lookup()
}
#[cfg(test)]mod noninteractive_policy_tests{
 use super::*;use std::sync::{Arc,atomic::{AtomicBool,Ordering}};
 struct Fake(Arc<AtomicBool>);struct Restore(Arc<AtomicBool>);impl Drop for Restore{fn drop(&mut self){self.0.store(true,Ordering::Release);}}
 impl InteractionPolicy for Fake{type Guard=Restore;fn allowed(&self)->Result<bool,CredentialFailure>{Ok(self.0.load(Ordering::Acquire))}fn disable(&self)->Result<Restore,CredentialFailure>{self.0.store(false,Ordering::Release);Ok(Restore(self.0.clone()))}}
 #[test]fn noninteractive_restores_prior_policy_after_success_error_and_unwind(){let state=Arc::new(AtomicBool::new(true));let f=Fake(state.clone());with_noninteractive_policy(&f,||{assert!(!state.load(Ordering::Acquire));Ok(())}).unwrap();assert!(state.load(Ordering::Acquire));assert!(with_noninteractive_policy(&f,||Err::<(),_>(CredentialFailure::KeychainUnavailable)).is_err());assert!(state.load(Ordering::Acquire));let _=std::panic::catch_unwind(||{let _=with_noninteractive_policy(&f,||{panic!("A cancelled callback");#[allow(unreachable_code)]Ok(())});});assert!(state.load(Ordering::Acquire));KEYCHAIN_OPERATION.clear_poison();state.store(false,Ordering::Release);with_noninteractive_policy(&f,||Ok(())).unwrap();assert!(!state.load(Ordering::Acquire));}
 #[test]fn noninteractive_and_manual_operations_are_serialized_without_policy_leak(){let state=Arc::new(AtomicBool::new(true));let f=Fake(state.clone());let manual=KEYCHAIN_OPERATION.lock().unwrap();assert!(with_noninteractive_policy(&f,|| -> Result<(),CredentialFailure>{panic!("must not enter lookup")}).is_err());assert!(state.load(Ordering::Acquire));drop(manual);with_noninteractive_policy(&f,||{assert!(KEYCHAIN_OPERATION.try_lock().is_err());Ok(())}).unwrap();assert!(state.load(Ordering::Acquire));assert!(KEYCHAIN_OPERATION.try_lock().is_ok());}
 #[test]fn credential_check_manual_read_never_enables_prior_disabled_policy(){let state=Arc::new(AtomicBool::new(false));let f=Fake(state.clone());with_manual_read_policy(&f,||{assert!(!state.load(Ordering::Acquire));assert!(with_noninteractive_policy(&f,||Ok(())).is_err());Ok(())}).unwrap();assert!(!state.load(Ordering::Acquire));}
}

fn keychain() -> Result<SecKeychain, CredentialFailure> {
    read_stage("default_keychain",None);
    SecKeychain::default().map_err(|e| {read_stage("default_keychain",Some(e.code()));CredentialFailure::KeychainUnavailable})
}

fn lookup_failure_from_status(status: i32) -> CredentialFailure {
    read_stage("single_item_read",Some(status));
    if status == ERR_SEC_ITEM_NOT_FOUND {
        CredentialFailure::KeychainMissing
    } else {
        CredentialFailure::KeychainUnavailable
    }
}

impl CredentialPort for MacosCredentialPort {
    fn add_generic_password(
        &mut self,
        service: &str,
        reference: &str,
        material: &[u8],
    ) -> Result<(), CredentialFailure> {
        let _operation=KEYCHAIN_OPERATION.try_lock().map_err(|_|CredentialFailure::KeychainUnavailable)?;
        keychain()?
            .add_generic_password(service, reference, material)
            .map_err(|_| CredentialFailure::KeychainUnavailable)
    }

    fn find_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<Vec<u8>, CredentialFailure> {
        with_manual_read_policy(&MacosInteractionPolicy,||{
        let (password, _) = keychain()?
            .find_generic_password(service, reference)
            .map_err(|error| lookup_failure_from_status(error.code()))?;
        read_stage("single_item_read",Some(0));
        Ok(password.as_ref().to_vec())
        })
    }

    fn delete_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<(), CredentialFailure> {
        let _operation=KEYCHAIN_OPERATION.try_lock().map_err(|_|CredentialFailure::KeychainUnavailable)?;
        let (_, item) = keychain()?
            .find_generic_password(service, reference)
            .map_err(|error| lookup_failure_from_status(error.code()))?;
        item.delete();
        match keychain()?.find_generic_password(service, reference) {
            Ok(_) => Err(CredentialFailure::KeychainUnavailable),
            Err(error) => match lookup_failure_from_status(error.code()) {
                CredentialFailure::KeychainMissing => Ok(()),
                failure => Err(failure),
            },
        }
    }
}

fn reference_has_exact_generated_suffix(reference: &str, prefix: &str) -> bool {
    reference.strip_prefix(prefix).is_some_and(|suffix| {
        suffix.len() == REFERENCE_RANDOM_HEX_LENGTH
            && suffix
                .bytes()
                .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
    })
}

pub fn reference_lineage(reference: &str) -> Result<CredentialLineage, CredentialFailure> {
    if reference_has_exact_generated_suffix(reference, P3_145_REFERENCE_PREFIX) {
        Ok(CredentialLineage::P3_145)
    } else {
        Err(CredentialFailure::KeyReferenceRejected)
    }
}

pub fn new_key_reference() -> String {
    let mut value = [0u8; 16];
    OsRng.fill_bytes(&mut value);
    let reference = value
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<String>();
    value.zeroize();
    format!("{P3_145_REFERENCE_PREFIX}{reference}")
}

fn create_key_material_with_port<P: CredentialPort>(
    port: &mut P,
    reference: &str,
) -> Result<(), CredentialFailure> {
    if reference_lineage(reference)? != CredentialLineage::P3_145 {
        return Err(CredentialFailure::KeyReferenceRejected);
    }
    let mut key = [0u8; 32];
    OsRng.fill_bytes(&mut key);
    let result = port.add_generic_password(KEYCHAIN_SERVICE, reference, &key);
    key.zeroize();
    result
}

fn load_key_material_with_port<P: CredentialPort>(
    port: &mut P,
    reference: &str,
) -> Result<Vec<u8>, CredentialFailure> {
    let lineage = reference_lineage(reference)?;
    let mut value = port.find_generic_password(lineage.keychain_service(), reference)?;
    if value.len() != 32 {
        value.zeroize();
        return Err(CredentialFailure::AuthenticationFailed);
    }
    Ok(value)
}

pub fn delete_key_material_with_port<P: CredentialPort>(
    port: &mut P,
    reference: &str,
) -> Result<(), CredentialFailure> {
    let lineage = reference_lineage(reference)?;
    port.delete_generic_password(lineage.keychain_service(), reference)
}

pub fn delete_key_material(reference: &str) -> Result<(), CredentialFailure> {
    delete_key_material_with_port(&mut MacosCredentialPort, reference)
}

fn validate_api_key(api_key: &str) -> Result<(), CredentialFailure> {
    if api_key.len() < 8
        || api_key.len() > 512
        || !api_key
            .bytes()
            .all(|byte| byte.is_ascii_graphic() && byte != b'"' && byte != b'\\')
    {
        return Err(CredentialFailure::InvalidInput);
    }
    Ok(())
}

fn encrypt_with_existing_material<P: CredentialPort>(
    port: &mut P,
    api_key: &str,
    aad: &[u8],
    key_reference: String,
) -> Result<EncryptedCredential, CredentialFailure> {
    let mut key = load_key_material_with_port(port, &key_reference)?;
    let cipher = match Aes256Gcm::new_from_slice(&key) {
        Ok(value) => value,
        Err(_) => {
            key.zeroize();
            return Err(CredentialFailure::EncryptionFailed);
        }
    };
    let mut nonce = [0u8; 12];
    OsRng.fill_bytes(&mut nonce);
    let mut ciphertext = api_key.as_bytes().to_vec();
    let tag =
        match cipher.encrypt_in_place_detached(Nonce::from_slice(&nonce), aad, &mut ciphertext) {
            Ok(value) => value,
            Err(_) => {
                key.zeroize();
                ciphertext.zeroize();
                return Err(CredentialFailure::EncryptionFailed);
            }
        };
    key.zeroize();
    Ok(EncryptedCredential {
        ciphertext,
        nonce: nonce.to_vec(),
        tag: tag.to_vec(),
        key_reference,
        algorithm: ALGORITHM,
        version: VERSION,
    })
}

pub fn encrypt_with_port<P: CredentialPort>(
    port: &mut P,
    api_key: &str,
    aad: &[u8],
) -> Result<EncryptedCredential, CredentialFailure> {
    validate_api_key(api_key)?;
    let key_reference = new_key_reference();
    create_key_material_with_port(port, &key_reference)?;
    match encrypt_with_existing_material(port, api_key, aad, key_reference.clone()) {
        Ok(encrypted) => Ok(encrypted),
        Err(error) => {
            let _ = delete_key_material_with_port(port, &key_reference);
            Err(error)
        }
    }
}

pub fn encrypt_new_reference<P: CredentialPort>(
    port: &mut P,
    api_key: &str,
    aad: &[u8],
    reference: String,
) -> Result<EncryptedCredential, CredentialFailure> {
    validate_api_key(api_key)?;
    create_key_material_with_port(port, &reference)?;
    encrypt_with_existing_material(port, api_key, aad, reference)
}
pub fn encrypt_new_reference_real(
    api_key: &str,
    aad: &[u8],
    reference: String,
) -> Result<EncryptedCredential, CredentialFailure> {
    encrypt_new_reference(&mut MacosCredentialPort, api_key, aad, reference)
}

pub fn encrypt(api_key: &str, aad: &[u8]) -> Result<EncryptedCredential, CredentialFailure> {
    encrypt_with_port(&mut MacosCredentialPort, api_key, aad)
}

pub fn decrypt_with_port<P: CredentialPort>(
    port: &mut P,
    ciphertext: &[u8],
    nonce: &[u8],
    tag: &[u8],
    reference: &str,
    algorithm: &str,
    version: u8,
    aad: &[u8],
) -> Result<Vec<u8>, CredentialFailure> {
    if algorithm != ALGORITHM || version != VERSION || nonce.len() != 12 || tag.len() != 16 {
        return Err(CredentialFailure::AuthenticationFailed);
    }
    let mut key = load_key_material_with_port(port, reference)?;
    let cipher =
        Aes256Gcm::new_from_slice(&key).map_err(|_| CredentialFailure::EncryptionFailed)?;
    let mut plaintext = ciphertext.to_vec();
    let result = cipher.decrypt_in_place_detached(
        Nonce::from_slice(nonce),
        aad,
        &mut plaintext,
        Tag::from_slice(tag),
    );
    key.zeroize();
    if result.is_err() {
        plaintext.zeroize();
        return Err(CredentialFailure::AuthenticationFailed);
    }
    Ok(plaintext)
}

pub fn decrypt(
    ciphertext: &[u8],
    nonce: &[u8],
    tag: &[u8],
    reference: &str,
    algorithm: &str,
    version: u8,
    aad: &[u8],
) -> Result<Vec<u8>, CredentialFailure> {
    decrypt_with_port(
        &mut MacosCredentialPort,
        ciphertext,
        nonce,
        tag,
        reference,
        algorithm,
        version,
        aad,
    )
}

#[cfg(test)]
#[derive(Default)]
pub struct MemoryCredentialPort {
    materials: BTreeMap<(String, String), Vec<u8>>,
    next_find_failure: Option<CredentialFailure>,
    calls: usize,
}

#[cfg(test)]
impl MemoryCredentialPort {
    pub fn seed(&mut self, reference: &str, material: &[u8]) -> Result<(), CredentialFailure> {
        let lineage = reference_lineage(reference)?;
        self.materials.insert(
            (lineage.keychain_service().into(), reference.into()),
            material.to_vec(),
        );
        Ok(())
    }

    pub fn fail_next_find(&mut self, failure: CredentialFailure) {
        self.next_find_failure = Some(failure);
    }

    pub fn calls(&self) -> usize {
        self.calls
    }
}

#[cfg(test)]
impl CredentialPort for MemoryCredentialPort {
    fn add_generic_password(
        &mut self,
        service: &str,
        reference: &str,
        material: &[u8],
    ) -> Result<(), CredentialFailure> {
        self.calls += 1;
        let key = (service.into(), reference.into());
        if self.materials.contains_key(&key) {
            return Err(CredentialFailure::KeychainUnavailable);
        }
        self.materials.insert(key, material.to_vec());
        Ok(())
    }

    fn find_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<Vec<u8>, CredentialFailure> {
        self.calls += 1;
        if let Some(failure) = self.next_find_failure.take() {
            return Err(failure);
        }
        self.materials
            .get(&(service.into(), reference.into()))
            .cloned()
            .ok_or(CredentialFailure::KeychainMissing)
    }

    fn delete_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<(), CredentialFailure> {
        self.calls += 1;
        self.materials
            .remove(&(service.into(), reference.into()))
            .map(|_| ())
            .ok_or(CredentialFailure::KeychainMissing)
    }
}

#[cfg(test)]
pub fn encrypt_existing_reference_for_test<P: CredentialPort>(
    port: &mut P,
    api_key: &str,
    aad: &[u8],
    reference: &str,
) -> Result<EncryptedCredential, CredentialFailure> {
    validate_api_key(api_key)?;
    encrypt_with_existing_material(port, api_key, aad, reference.into())
}


#[cfg(test)]mod continuity_guards {
 use super::*;
 #[derive(Default)]struct Missing{finds:usize,adds:usize,deletes:usize}
 impl CredentialPort for Missing{
 fn find_generic_password(&mut self,s:&str,r:&str)->Result<Vec<u8>,CredentialFailure>{assert_eq!(s,KEYCHAIN_SERVICE);assert!(r.starts_with("p3-152-key-"));self.finds+=1;Err(CredentialFailure::KeychainMissing)}
 fn add_generic_password(&mut self,_:&str,_:&str,_:&[u8])->Result<(),CredentialFailure>{self.adds+=1;panic!("must not replace missing material")}
 fn delete_generic_password(&mut self,_:&str,_:&str)->Result<(),CredentialFailure>{self.deletes+=1;panic!("must not delete")}}
 #[test]fn missing_key_never_adds_deletes_or_falls_back(){let mut p=Missing::default();let r="p3-152-key-0123456789abcdef0123456789abcdef";assert_eq!(decrypt_with_port(&mut p,&[1;16],&[2;12],&[3;16],r,ALGORITHM,VERSION,b"old-aad").unwrap_err(),CredentialFailure::KeychainMissing);assert_eq!((p.finds,p.adds,p.deletes),(1,0,0));}
 #[test]fn legacy_and_malformed_accounts_never_reach_keychain(){let mut p=Missing::default();for r in ["p3-144-key-0123456789abcdef0123456789abcdef","p3-152-key-0123456789ABCDEF0123456789ABCDEF","p3-152-key-short"]{assert_eq!(load_key_material_with_port(&mut p,r).unwrap_err(),CredentialFailure::KeyReferenceRejected);}assert_eq!((p.finds,p.adds,p.deletes),(0,0,0));}
 #[test]fn old_ciphertext_aad_survives_port_reopen_without_rotation(){let mut p=MemoryCredentialPort::default();let r="p3-152-key-0123456789abcdef0123456789abcdef";p.seed(r,&[7;32]).unwrap();let aad=format!("LIFEOS-P3-152|credential|v1|deepseek-default|1|{r}");let e=encrypt_existing_reference_for_test(&mut p,"fictional-154-secret",aad.as_bytes(),r).unwrap();let mut reopened=MemoryCredentialPort::default();reopened.seed(r,&[7;32]).unwrap();assert_eq!(decrypt_with_port(&mut reopened,&e.ciphertext,&e.nonce,&e.tag,r,e.algorithm,e.version,aad.as_bytes()).unwrap(),b"fictional-154-secret");assert_eq!(reopened.calls(),1);}
}

#[cfg(test)]mod diagnostic_tests {
 use super::*;
 #[test]fn credential_diagnostic_records_interaction_and_other_os_failures(){
  for (status,expected) in [(-25308,CredentialFailure::KeychainInteractionRequired),(-25300,CredentialFailure::KeychainMissing),(-25293,CredentialFailure::KeychainUnavailable)]{assert_eq!(noninteractive_lookup_failure(status),expected);assert_eq!(ReadDiagnostic::capture().value(),serde_json::json!({"stage":"single_item_read","osStatus":status}));}
  assert_eq!(ReadDiagnostic::new("account/service/ref/secret",Some(-99)).value(),serde_json::json!({"stage":"diagnostic_unavailable","osStatus":null}));
  let _lock=KEYCHAIN_OPERATION.lock().unwrap();let r=with_noninteractive_policy(&MacosInteractionPolicy,||->Result<(),CredentialFailure>{panic!("no OS access")});assert!(r.is_err());assert_eq!(ReadDiagnostic::capture().value()["stage"],"concurrent_busy");
 }
}

#[path="secure_credentials/metadata.rs"]pub(crate) mod metadata;
