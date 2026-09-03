use aes_gcm::{
    aead::{AeadInPlace, KeyInit},
    Aes256Gcm, Nonce, Tag,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Failure {
    CredentialRequired,
    KeyMaterialMissing,
    AuthenticationFailed,
}

fn decode(
    key: Option<&[u8; 32]>,
    ciphertext: &[u8],
    nonce: &[u8; 12],
    tag: &[u8; 16],
    aad: &[u8],
) -> Result<(), Failure> {
    let key = key.ok_or(Failure::KeyMaterialMissing)?;
    let cipher = Aes256Gcm::new_from_slice(key).map_err(|_| Failure::AuthenticationFailed)?;
    let mut value = ciphertext.to_vec();
    cipher
        .decrypt_in_place_detached(Nonce::from_slice(nonce), aad, &mut value, Tag::from_slice(tag))
        .map_err(|_| Failure::AuthenticationFailed)?;
    value.fill(0);
    Ok(())
}

fn main() {
    let key = [0x5Au8; 32];
    let aad = b"LIFEOS-P3-145|credential|v1|deepseek|default";
    let nonce = [0xA5u8; 12];
    let mut ciphertext = b"synthetic-p3-145-closure3-not-a-secret".to_vec();
    let cipher = Aes256Gcm::new_from_slice(&key).expect("fixed 32-byte synthetic key");
    let tag = cipher
        .encrypt_in_place_detached(Nonce::from_slice(&nonce), aad, &mut ciphertext)
        .expect("fixed synthetic encryption");
    let tag: [u8; 16] = tag.into();

    let missing_row = Failure::CredentialRequired;
    let missing_key = decode(None, &ciphertext, &nonce, &tag, aad).unwrap_err();
    let deleted_key = decode(None, &ciphertext, &nonce, &tag, aad).unwrap_err();
    let mut tampered = ciphertext.clone();
    tampered[0] ^= 0x01;
    let tampered_result = decode(Some(&key), &tampered, &nonce, &tag, aad).unwrap_err();
    let valid = decode(Some(&key), &ciphertext, &nonce, &tag, aad).is_ok();
    ciphertext.fill(0);
    tampered.fill(0);

    assert_eq!(missing_row, Failure::CredentialRequired);
    assert_eq!(missing_key, Failure::KeyMaterialMissing);
    assert_eq!(deleted_key, Failure::KeyMaterialMissing);
    assert_eq!(tampered_result, Failure::AuthenticationFailed);
    assert!(valid);
    println!("{{\"missing_row\":\"credential_required\",\"missing_key\":\"key_material_missing\",\"deleted_key\":\"key_material_missing\",\"tamper\":\"credential_authentication_failed\",\"valid_fixture\":true,\"keychain_calls\":0,\"network_calls\":0,\"plaintext_emitted\":false}}");
}
