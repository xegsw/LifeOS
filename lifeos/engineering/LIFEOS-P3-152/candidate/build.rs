fn main(){println!("cargo:rerun-if-env-changed=LIFEOS_P3_152_MODE");assert_eq!(std::env::var("LIFEOS_P3_152_MODE").as_deref(),Ok("synthetic"),"151 only builds synthetic");tauri_build::build();}
