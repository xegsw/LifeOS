fn main(){
 println!("cargo:rerun-if-env-changed=LIFEOS_P3_159_MODE");
 let real=std::env::var_os("CARGO_FEATURE_CONTROLLED_REAL").is_some();
 let online=std::env::var_os("CARGO_FEATURE_ONLINE_SYNTHETIC").is_some();
 let driver=std::env::var_os("CARGO_FEATURE_SYNTHETIC_DRIVER").is_some();
 assert!(!(real&&online),"mixed runtime modes forbidden");
 assert!(!((real||online)&&driver),"network driver forbidden");
 assert_eq!(std::env::var("LIFEOS_P3_159_MODE").as_deref(),Ok(if real{"real"}else if online{"online-synthetic"}else{"synthetic"}),"build mode rejected");
 // Always compile the hard-disabled A native implementation. Real Rust mode
 // does not grant audio/network capability and never adds LIFEOS_VOICE_REAL.
 let out=std::path::PathBuf::from(std::env::var_os("OUT_DIR").unwrap());
 let sources=["src/voice/native/PlaybackLedger.swift","src/voice/native/AudioEngine.swift","src/voice/native/MiMoHTTP.swift"];
 for source in sources {println!("cargo:rerun-if-changed={source}");}
 let status=std::process::Command::new("/usr/bin/xcrun").args(["swiftc","-emit-library","-static","-module-name","LifeOSVoice","-o"]).arg(out.join("libLifeOSVoice.a")).args(sources).status().expect("Swift A compiler unavailable");assert!(status.success(),"Swift A native library failed");
 let info=std::process::Command::new("/usr/bin/xcrun").args(["swiftc","-print-target-info"]).output().expect("Swift target unavailable");assert!(info.status.success());let info:serde_json::Value=serde_json::from_slice(&info.stdout).unwrap();
 for path in info["paths"]["runtimeLibraryPaths"].as_array().unwrap(){println!("cargo:rustc-link-search=native={}",path.as_str().unwrap());}
 println!("cargo:rustc-link-search=native={}",out.display());println!("cargo:rustc-link-lib=static=LifeOSVoice");println!("cargo:rustc-link-arg=-Wl,-rpath,/usr/lib/swift");
 println!("cargo:rerun-if-changed=src/secure_credentials/metadata.c");
 let status=std::process::Command::new("/usr/bin/xcrun").args(["clang","-Werror","-Wno-deprecated-declarations","-c","src/secure_credentials/metadata.c","-o"]).arg(out.join("metadata.o")).status().unwrap();assert!(status.success());
 println!("cargo:rerun-if-changed=src/secure_credentials/metadata_fake.c");
 let status=std::process::Command::new("/usr/bin/xcrun").args(["clang","-Werror","-Wno-deprecated-declarations","-c","src/secure_credentials/metadata_fake.c","-o"]).arg(out.join("metadata_fake.o")).status().unwrap();assert!(status.success());
 let status=std::process::Command::new("/usr/bin/ar").arg("rcs").arg(out.join("libLifeOSMetadata.a")).arg(out.join("metadata.o")).arg(out.join("metadata_fake.o")).status().unwrap();assert!(status.success());
 println!("cargo:rustc-link-lib=static=LifeOSMetadata");
 tauri_build::build();
}
