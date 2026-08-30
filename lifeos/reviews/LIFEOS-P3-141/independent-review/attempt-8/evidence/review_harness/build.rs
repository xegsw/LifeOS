use std::{env, fs, path::PathBuf};

fn main() {
    println!("cargo:rustc-env=LIFEOS_RUNTIME_ROOT=/private/tmp/lifeos-p3-141-controlled-pilot-v1/review-harness-runtime");
    println!("cargo:rustc-env=LIFEOS_INPUT_MODE=synthetic");
    let output = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR"));
    fs::write(output.join("phase_b_receipt_binding.rs"), "const VALIDATED_PHASE_B_RECEIPT_SHA256: Option<&str> = None;\nconst COMPILED_BUILD_MODE: &str = \"synthetic_review\";\n").expect("review-owned generated binding");
}
