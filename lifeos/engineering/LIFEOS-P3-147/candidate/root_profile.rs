//! Build-time selection only. This immutable file and JSON are part of the candidate.
use serde_json::Value;
pub const PROFILES: &str = include_str!("root_profiles.json");
pub fn select(name: &str) -> Result<Value, &'static str> {
    if !matches!(
        name,
        "engineering" | "independent-review" | "source-pilot-1"
    ) {
        return Err("profile_rejected");
    }
    let profiles: Value = serde_json::from_str(PROFILES).map_err(|_| "profile_rejected")?;
    Ok(profiles[name].clone())
}
pub fn validate_environment(compiled: &str) -> Result<(), &'static str> {
    select(compiled)?;
    for key in [
        "LIFEOS_RUNTIME_ROOT",
        "LIFEOS_P3_145_ROOT_PROFILE",
        "LIFEOS_P3_147_ROOT",
        "LIFEOS_P3_147_ROOT_PROFILE",
    ] {
        if std::env::var_os(key).is_some() {
            return Err("profile_rejected");
        }
    }
    if std::env::var_os("LIFEOS_P3_147_PROFILE").is_some_and(|s| s != "synthetic") {
        return Err("profile_rejected");
    }
    if std::env::var_os("LIFEOS_P3_147_BUILD_PROFILE").is_some_and(|s| s != compiled) {
        return Err("profile_rejected");
    }
    Ok(())
}
