fn main(){
 println!("cargo:rerun-if-env-changed=LIFEOS_P3_158_MODE");
 let real=std::env::var_os("CARGO_FEATURE_CONTROLLED_REAL").is_some();
 let online=std::env::var_os("CARGO_FEATURE_ONLINE_SYNTHETIC").is_some();
 let driver=std::env::var_os("CARGO_FEATURE_SYNTHETIC_DRIVER").is_some();
 assert!(!(real&&online),"mixed runtime modes forbidden");
 assert!(!((real||online)&&driver),"network driver forbidden");
 assert_eq!(std::env::var("LIFEOS_P3_158_MODE").as_deref(),Ok(if real{"real"}else if online{"online-synthetic"}else{"synthetic"}),"build mode rejected");
 tauri_build::build();
}
