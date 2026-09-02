use aes_gcm::{
    aead::{AeadInPlace, KeyInit},
    Aes256Gcm, Nonce, Tag,
};
use rand::{rngs::OsRng, RngCore};
use security_framework::os::macos::keychain::SecKeychain;
use zeroize::Zeroize;

pub const KEYCHAIN_SERVICE: &str = "com.lifeos.p3-143.aead-key.v1";
pub const ALGORITHM: &str = "AES-256-GCM";
pub const VERSION: u8 = 1;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CredentialFailure {
    InvalidInput,
    KeychainUnavailable,
    KeychainMissing,
    EncryptionFailed,
    AuthenticationFailed,
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

fn keychain() -> Result<SecKeychain, CredentialFailure> {
    SecKeychain::default().map_err(|_| CredentialFailure::KeychainUnavailable)
}

pub fn new_key_reference() -> String {
    let mut value = [0u8; 16];
    OsRng.fill_bytes(&mut value);
    let reference = value
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<String>();
    value.zeroize();
    format!("p3-143-key-{reference}")
}

pub fn create_key_material(reference: &str) -> Result<(), CredentialFailure> {
    let mut key = [0u8; 32];
    OsRng.fill_bytes(&mut key);
    let result = keychain()?
        .add_generic_password(KEYCHAIN_SERVICE, reference, &key)
        .map_err(|_| CredentialFailure::KeychainUnavailable);
    key.zeroize();
    result
}

fn load_key_material(reference: &str) -> Result<Vec<u8>, CredentialFailure> {
    let (password, _) = keychain()?
        .find_generic_password(KEYCHAIN_SERVICE, reference)
        .map_err(|_| CredentialFailure::KeychainMissing)?;
    let value = password.as_ref().to_vec();
    if value.len() != 32 {
        return Err(CredentialFailure::KeychainMissing);
    }
    Ok(value)
}

pub fn delete_key_material(reference: &str) -> Result<(), CredentialFailure> {
    let (_, item) = keychain()?
        .find_generic_password(KEYCHAIN_SERVICE, reference)
        .map_err(|_| CredentialFailure::KeychainMissing)?;
    item.delete();
    match keychain()?.find_generic_password(KEYCHAIN_SERVICE, reference) {
        Ok(_) => Err(CredentialFailure::KeychainUnavailable),
        Err(_) => Ok(()),
    }
}

pub fn encrypt(api_key: &str, aad: &[u8]) -> Result<EncryptedCredential, CredentialFailure> {
    if api_key.len() < 8
        || api_key.len() > 512
        || !api_key
            .bytes()
            .all(|byte| byte.is_ascii_graphic() && byte != b'"' && byte != b'\\')
    {
        return Err(CredentialFailure::InvalidInput);
    }
    let key_reference = new_key_reference();
    create_key_material(&key_reference)?;
    let mut key = match load_key_material(&key_reference) {
        Ok(value) => value,
        Err(error) => {
            let _ = delete_key_material(&key_reference);
            return Err(error);
        }
    };
    let cipher = match Aes256Gcm::new_from_slice(&key) {
        Ok(value) => value,
        Err(_) => {
            key.zeroize();
            let _ = delete_key_material(&key_reference);
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
                let _ = delete_key_material(&key_reference);
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

pub fn decrypt(
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
    let mut key = load_key_material(reference)?;
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
    result.map_err(|_| CredentialFailure::AuthenticationFailed)?;
    Ok(plaintext)
}
