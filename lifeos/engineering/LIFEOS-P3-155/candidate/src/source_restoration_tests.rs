//! Synthetic integration of the private SourcePort, including the confirmation race.
use serde_json::json;
#[test]
fn source_identity_mutations_and_send_fence() {
    let fixture=format!("bridge-{}",std::process::id());
    let dispatch=|command:&str,payload:serde_json::Value|lifeos_source_engine::dispatch(command,json!({"version":1,"payload":payload}).to_string().as_bytes(),&fixture);
    dispatch("connect_source_directory",json!({"requestId":format!("connect-{}",std::process::id())})).unwrap();
    let mut ready=false;
    for _ in 0..150 {
        let s=dispatch("get_source_status",json!({})).unwrap();
        if s["connectors"][0]["scanComplete"]==true && s["connectors"][0]["pending"]==0 {ready=true;break}
        std::thread::sleep(std::time::Duration::from_millis(100));
    }
    assert!(ready,"source scan deadline");
    let rows=lifeos_source_engine::context(&fixture,"项目星舟").unwrap();
    assert!(!rows.is_empty());let reference=rows[0]["engineRef"].clone();
    assert!(lifeos_source_engine::valid(&fixture,&reference));
    for (key,value) in [("store",json!("other-store")),("rootIdentity",json!("foreign-root")),("connectorId",json!("foreign-source")),("sourceRef",json!("foreign-file")),("version",json!(999)),("authorizationGeneration",json!(999)),("scanEpoch",json!(999)),("contentHash",json!("forged")),("endScalar",json!(999999))] {
        let mut forged=reference.clone();forged[key]=value;
        assert!(!lifeos_source_engine::valid(&fixture,&forged),"{key}");
    }
    let fence=lifeos_source_engine::send_fence(&fixture,&[reference.clone()]).unwrap().unwrap();
    let (sent,received)=std::sync::mpsc::channel();let other=fixture.clone();
    let worker=std::thread::spawn(move|| {
        let result=lifeos_source_engine::dispatch("control_source_job",json!({"version":1,"payload":{"requestId":"race-disconnect","connectorId":"directory","expectedGeneration":1,"action":"disconnect"}}).to_string().as_bytes(),&other);
        sent.send(result.is_ok()).unwrap();
    });
    assert!(received.recv_timeout(std::time::Duration::from_millis(100)).is_err(),"mutation crossed protected dispatch boundary");
    drop(fence);
    assert!(received.recv_timeout(std::time::Duration::from_secs(3)).unwrap());worker.join().unwrap();
    assert!(!lifeos_source_engine::valid(&fixture,&reference));
    assert!(lifeos_source_engine::context(&fixture,"项目星舟").unwrap().is_empty());
}

#[cfg(feature="synthetic-driver")]
#[test]
fn fixed_health_target_append_rollback_locks_and_schema(){lifeos_source_engine::synthetic_boundary_check().unwrap();}
#[test]
fn raw_file_edit_invalidates_reference_without_refresh(){
 use std::{fs,os::unix::fs::OpenOptionsExt,io::Write};
 let root=std::path::Path::new("/private/tmp/lifeos-p3-155-source-update-v1/source-engine/fixtures/app-source");
 let path=root.join(format!("edit-check-{}.txt",std::process::id()));let mut f=fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(&path).unwrap();f.write_all(b"uniqueeditcheck private synthetic original").unwrap();drop(f);
 let fixture=format!("edit-{}",std::process::id());lifeos_source_engine::dispatch("connect_source_directory",json!({"version":1,"payload":{"requestId":"edit-connect"}}).to_string().as_bytes(),&fixture).unwrap();
 let mut reference=None;
 for _ in 0..150{let rows=lifeos_source_engine::context(&fixture,"uniqueeditcheck").unwrap_or_default();if let Some(row)=rows.first(){reference=Some(row["engineRef"].clone());break}std::thread::sleep(std::time::Duration::from_millis(100));}
 let r=reference.expect("source scan deadline");assert!(lifeos_source_engine::valid(&fixture,&r));fs::write(&path,b"uniqueeditcheck modified synthetic source").unwrap();assert!(!lifeos_source_engine::valid(&fixture,&r));fs::remove_file(path).unwrap();
}
