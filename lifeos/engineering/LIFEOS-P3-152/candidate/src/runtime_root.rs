//! P3-152 synthetic stage: a compile-time false network/Keychain gate.
pub fn is_real()->bool{false}
pub fn verify()->Result<std::path::PathBuf,crate::repository::Error>{crate::health_conversation_host::verify_root()?;Ok(std::path::PathBuf::from(crate::health_conversation_host::ROOT).join("synthetic"))}
