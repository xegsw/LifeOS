mod root_profile;
fn main() {
    for key in [
        "LIFEOS_P3_148_BUILD_PROFILE",
        "LIFEOS_P3_148_PROFILE",
        "LIFEOS_RUNTIME_ROOT",
        "LIFEOS_P3_145_ROOT_PROFILE",
        "LIFEOS_P3_148_ROOT",
        "LIFEOS_P3_148_ROOT_PROFILE",
    ] {
        println!("cargo:rerun-if-env-changed={key}");
    }
    println!("cargo:rerun-if-changed=root_profiles.json");
    println!("cargo:rerun-if-changed=root_profile.rs");
    let name =
        std::env::var("LIFEOS_P3_148_BUILD_PROFILE").expect("explicit build profile required");
    root_profile::validate_environment(&name).expect("profile_rejected");
    let spec = root_profile::select(&name).expect("profile_rejected");
    // Pure configuration: do not probe either runtime root at build time.
    println!("cargo:rustc-env=P3_148_COMPILED_PROFILE={name}");
    println!(
        "cargo:rustc-env=P3_148_COMPILED_ROOT={}",
        spec["root"].as_str().unwrap()
    );
    println!(
        "cargo:rustc-env=P3_148_COMPILED_SOURCE={}",
        spec["source"].as_str().unwrap_or("")
    );
    tauri_build::build();
}
