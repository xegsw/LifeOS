use aes_gcm::{
    aead::{AeadInPlace, KeyInit},
    Aes256Gcm, Nonce, Tag,
};
use rand::{rngs::OsRng, RngCore};
use security_framework::os::macos::keychain::SecKeychain;
#[cfg(test)]
use std::collections::BTreeMap;
use zeroize::Zeroize;

pub const KEYCHAIN_SERVICE: &str = "com.lifeos.p3-149.aead-key.v1";
pub const LEGACY_P3_144_KEYCHAIN_SERVICE: &str = "com.lifeos.p3-144.aead-key.v1";
pub const ALGORITHM: &str = "AES-256-GCM";
pub const VERSION: u8 = 1;

const P3_144_REFERENCE_PREFIX: &str = "p3-144-key-";
const P3_145_REFERENCE_PREFIX: &str = "p3-149-key-";
const REFERENCE_RANDOM_HEX_LENGTH: usize = 32;
const ERR_SEC_ITEM_NOT_FOUND: i32 = -25300;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CredentialFailure {
    InvalidInput,
    KeyReferenceRejected,
    KeychainUnavailable,
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

fn keychain() -> Result<SecKeychain, CredentialFailure> {
    SecKeychain::default().map_err(|_| CredentialFailure::KeychainUnavailable)
}

fn lookup_failure_from_status(status: i32) -> CredentialFailure {
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
        keychain()?
            .add_generic_password(service, reference, material)
            .map_err(|_| CredentialFailure::KeychainUnavailable)
    }

    fn find_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<Vec<u8>, CredentialFailure> {
        let (password, _) = keychain()?
            .find_generic_password(service, reference)
            .map_err(|error| lookup_failure_from_status(error.code()))?;
        Ok(password.as_ref().to_vec())
    }

    fn delete_generic_password(
        &mut self,
        service: &str,
        reference: &str,
    ) -> Result<(), CredentialFailure> {
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
    let value = port.find_generic_password(lineage.keychain_service(), reference)?;
    if value.len() != 32 {
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

#[cfg(test)]
mod tests {
    use super::*;

    const P3_144_REFERENCE: &str = "p3-144-key-0123456789abcdef0123456789abcdef";
    const P3_145_REFERENCE: &str = "p3-149-key-fedcba9876543210fedcba9876543210";

    #[test]
    fn reference_lineage_is_exact_and_does_not_probe_unknown_services() {
        assert_eq!(
            reference_lineage(P3_144_REFERENCE),
            Err(CredentialFailure::KeyReferenceRejected)
        );
        assert_eq!(
            reference_lineage(P3_145_REFERENCE),
            Ok(CredentialLineage::P3_145)
        );
        assert_eq!(
            reference_lineage("p3-144-key-ABCDEF0123456789abcdef0123456789"),
            Err(CredentialFailure::KeyReferenceRejected)
        );
        assert_eq!(
            reference_lineage("p3-146-key-0123456789abcdef0123456789abcdef"),
            Err(CredentialFailure::KeyReferenceRejected)
        );
    }

    #[test]
    fn lookup_error_classification_distinguishes_missing_from_unavailable() {
        assert_eq!(
            lookup_failure_from_status(ERR_SEC_ITEM_NOT_FOUND),
            CredentialFailure::KeychainMissing
        );
        assert_eq!(
            lookup_failure_from_status(-25293),
            CredentialFailure::KeychainUnavailable
        );
    }

    #[test]
    fn synthetic_port_rejects_legacy_and_routes_current_credentials_exactly() {
        let mut port = MemoryCredentialPort::default();
        let current_aad = b"LIFEOS-P3-145|credential|v1|deepseek|default";
        assert_eq!(port.seed(P3_144_REFERENCE, &[7; 32]), Err(CredentialFailure::KeyReferenceRejected));
        port.seed(P3_145_REFERENCE, &[9; 32]).unwrap();
        let current = encrypt_existing_reference_for_test(
            &mut port,
            "current-canary-key",
            current_aad,
            P3_145_REFERENCE,
        )
        .unwrap();
        assert_eq!(
            decrypt_with_port(
                &mut port,
                &current.ciphertext,
                &current.nonce,
                &current.tag,
                &current.key_reference,
                current.algorithm,
                current.version,
                current_aad,
            )
            .unwrap(),
            b"current-canary-key"
        );
        let calls_before = port.calls();
        assert_eq!(
            delete_key_material_with_port(&mut port, "p3-146-key-0123456789abcdef0123456789abcdef"),
            Err(CredentialFailure::KeyReferenceRejected)
        );
        assert_eq!(port.calls(), calls_before);
    }
}

#[cfg(test)]
mod p149_memory_port_checks {
    use super::*;
    #[test]
    fn p149_memory_os_port_crypto_failures_do_not_fallback() {
        let mut p = MemoryCredentialPort::default();
        let e = encrypt_new_reference(
            &mut p,
            "fictional-key-only",
            b"148-aad",
            new_key_reference(),
        )
        .unwrap();
        let decrypt = |p: &mut MemoryCredentialPort, nonce: &[u8], aad: &[u8]| {
            decrypt_with_port(
                p,
                &e.ciphertext,
                nonce,
                &e.tag,
                &e.key_reference,
                e.algorithm,
                e.version,
                aad,
            )
        };
        assert_eq!(
            decrypt(&mut p, &e.nonce, b"148-aad").unwrap(),
            b"fictional-key-only"
        );
        assert!(decrypt(&mut p, &[0; 12], b"148-aad").is_err());
        assert!(decrypt(&mut p, &e.nonce, b"wrong-aad").is_err());
        for failure in [
            CredentialFailure::KeychainUnavailable,
            CredentialFailure::KeychainMissing,
        ] {
            p.fail_next_find(failure);
            assert_eq!(decrypt(&mut p, &e.nonce, b"148-aad").unwrap_err(), failure);
        }
        assert_eq!(KEYCHAIN_SERVICE, "com.lifeos.p3-149.aead-key.v1");
    }
}
