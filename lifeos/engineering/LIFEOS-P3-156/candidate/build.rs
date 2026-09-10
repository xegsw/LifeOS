fn main(){
 println!("cargo:rerun-if-env-changed=LIFEOS_P3_156_MODE");
 assert!(std::env::var_os("CARGO_FEATURE_CONTROLLED_REAL").is_none(),"P3-156 permits synthetic builds only");
 let real=std::env::var_os("CARGO_FEATURE_CONTROLLED_REAL").is_some();
 assert_eq!(std::env::var("LIFEOS_P3_156_MODE").as_deref(),Ok(if real{"real"}else{"synthetic"}),"build mode rejected");
 assert!(!(real&&std::env::var_os("CARGO_FEATURE_SYNTHETIC_DRIVER").is_some()),"real driver forbidden");
 tauri_build::build();
}
