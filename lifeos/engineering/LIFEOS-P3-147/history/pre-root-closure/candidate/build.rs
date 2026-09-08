fn main() {
    for key in [
        "LIFEOS_P3_147_PROFILE",
        "LIFEOS_RUNTIME_ROOT",
        "LIFEOS_P3_145_ROOT_PROFILE",
    ] {
        println!("cargo:rerun-if-env-changed={key}");
        if let Ok(value) = std::env::var(key) {
            assert!(
                key == "LIFEOS_P3_147_PROFILE" && value == "synthetic",
                "only fixed P3-146 synthetic profile allowed"
            );
        }
    }
    tauri_build::build();
}
