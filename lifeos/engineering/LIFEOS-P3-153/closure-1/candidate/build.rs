fn main(){
 println!("cargo:rerun-if-env-changed=LIFEOS_P3_153_MODE");
 assert!(std::env::var_os("CARGO_FEATURE_CONTROLLED_REAL").is_none(),"P3-153 is synthetic-only; real activation requires separate authorization");
 assert_eq!(std::env::var("LIFEOS_P3_153_MODE").as_deref(),Ok("synthetic"),"build mode rejected");
 tauri_build::build();
}
