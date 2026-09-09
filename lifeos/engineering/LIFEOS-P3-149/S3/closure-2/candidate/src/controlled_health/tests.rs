use super::*;
use std::{fs,os::unix::fs::{PermissionsExt,symlink},path::PathBuf};
fn root()->PathBuf {
    let p=PathBuf::from(crate::runtime_root::ROOT).join(format!("controlled-test-{}-{}",std::process::id(),apple_health::now()));
    fs::create_dir(&p).unwrap();fs::set_permissions(&p,fs::Permissions::from_mode(0o700)).unwrap();p
}
fn fixture(root:&Path,name:&str,good:bool){fs::write(root.join(name),if good{include_bytes!("../../../fixtures/02-synthetic-export.zip").as_slice()}else{b"broken"}).unwrap();}
#[test]
fn controlled_health_same_pipeline_private_counts_repeat_rollback_and_permissions(){
    let p=root();fixture(&p,"input.zip",true);
    let mut t=Target::create(&p,"new").unwrap();
    assert_eq!(fs::metadata(p.join("new")).unwrap().permissions().mode()&0o777,0o700);
    assert_eq!(fs::metadata(p.join("new/health-import.sqlite")).unwrap().permissions().mode()&0o777,0o600);
    let r=t.import(apple_health_input::open(&p,"input.zip").unwrap(),Some(2));assert!(r.is_err());
    assert_eq!(t.db.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0)).unwrap(),0);
    let v=t.import(apple_health_input::open(&p,"input.zip").unwrap(),None).unwrap();assert_eq!(v["inserted"],3);
    let encoded=receipt(Ok(v),true).to_string();for forbidden in ["Synthetic","2026","digest","types","file","120","HeartRate"]{assert!(!encoded.contains(forbidden));}
    let bad:i64=t.db.query_row("SELECT count(*) FROM records WHERE body LIKE '%HeartRate%' OR body LIKE '%synthetic_health%'",[],|r|r.get(0)).unwrap();assert_eq!(bad,0);
    assert_eq!(t.import(apple_health_input::open(&p,"input.zip").unwrap(),None).unwrap()["status"],"duplicate");
    assert!(Target::create(&p,"new").is_err());
    fixture(&p,"bad.zip",false);let before:i64=t.db.query_row("SELECT count(*) FROM records",[],|r|r.get(0)).unwrap();assert!(t.import(apple_health_input::open(&p,"bad.zip").unwrap(),None).is_err());assert_eq!(t.db.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0)).unwrap(),before);
}
#[test]
fn controlled_health_links_replacement_and_redaction_fail_closed(){
    let p=root();fixture(&p,"input.zip",true);symlink(p.join("input.zip"),p.join("link.zip")).unwrap();assert!(apple_health_input::open(&p,"link.zip").is_err());
    fs::hard_link(p.join("input.zip"),p.join("hard.zip")).unwrap();assert!(apple_health_input::open(&p,"input.zip").is_err());
    fixture(&p,"fresh.zip",true);let input=apple_health_input::open(&p,"fresh.zip").unwrap();fs::rename(p.join("fresh.zip"),p.join("retained.zip")).unwrap();symlink(p.join("retained.zip"),p.join("fresh.zip")).unwrap();let mut t=Target::create(&p,"new").unwrap();assert!(t.import(input,None).is_err());
    fs::rename(p.join("new/health-import.sqlite"),p.join("new/retained.sqlite")).unwrap();fs::write(p.join("new/health-import.sqlite"),b"").unwrap();assert!(t.file.validate().is_err());
    let text=receipt(Err(Error::new("private SECRET 987654321")),true).to_string();assert!(!text.contains("SECRET"));assert!(!text.contains("987654321"));assert!(text.contains("controlled_import_failed"));
}
#[test]
fn controlled_health_target_replaced_before_commit_rolls_back(){
    let p=root();fixture(&p,"input.zip",true);let mut t=Target::create(&p,"new").unwrap();
    let source=apple_health_input::open(&p,"input.zip").unwrap();let calls=std::cell::Cell::new(0);
    let result=apple_health::import_bound(&mut t.db,"authorized-export.zip",apple_health::now(),&serde_json::from_str(include_str!("../../apple_health_limits.json")).unwrap(),|_|{},None,source.0,true,||{
        calls.set(calls.get()+1);
        if calls.get()==3 {fs::rename(p.join("new/health-import.sqlite"),p.join("new/retained.sqlite")).unwrap();fs::write(p.join("new/health-import.sqlite"),b"").unwrap();}
        t.dir.validate()?;t.file.validate_unique()
    });
    assert!(result.is_err());assert_eq!(t.db.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0)).unwrap(),0);
}
fn origin()->Value {json!({"earliest_ms":apple_health::now()-3000,"latest_ms":apple_health::now()+3000})}
#[test]
fn controlled_health_resume_proves_empty_target_marker_and_idempotency(){
    let p=root();fixture(&p,"input.zip",true);let t=Target::create(&p,"new").unwrap();drop(t);
    let mut t=Target::resume(&p,"new",&origin()).unwrap();
    assert!(p.join("new/.s3-closure-2-attempt.json").is_file());
    assert_eq!(t.import(apple_health_input::open(&p,"input.zip").unwrap(),None).unwrap()["inserted"],3);
    assert_eq!(t.import(apple_health_input::open(&p,"input.zip").unwrap(),None).unwrap()["status"],"duplicate");
    drop(t);assert!(Target::resume(&p,"new",&origin()).is_err());
}
#[test]
fn controlled_health_resume_rejects_foreign_data_wrong_origin_and_retains_failed_attempt(){
    let p=root();let t=Target::create(&p,"foreign").unwrap();t.db.execute("INSERT INTO records VALUES('synthetic-foreign','{}')",[]).unwrap();drop(t);
    assert!(Target::resume(&p,"foreign",&origin()).is_err());
    let t=Target::create(&p,"old").unwrap();drop(t);assert!(Target::resume(&p,"old",&json!({"earliest_ms":1,"latest_ms":2})).is_err());
    let t=Target::create(&p,"new").unwrap();drop(t);fixture(&p,"bad.zip",false);
    let mut t=Target::resume(&p,"new",&origin()).unwrap();assert!(t.import(apple_health_input::open(&p,"bad.zip").unwrap(),None).is_err());
    assert_eq!(t.db.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0)).unwrap(),0);
    assert!(p.join("new/.s3-closure-2-attempt.json").exists());
}
#[test]
fn controlled_health_encoded_zip_scoped_budget_pipeline_and_rollback(){
    let p=root();fs::write(p.join("encoded.zip"),include_bytes!("../../../fixtures/08-encoded-export.zip")).unwrap();
    let t=Target::create(&p,"new").unwrap();drop(t);let mut t=Target::resume(&p,"new",&origin()).unwrap();
    let source=apple_health_input::open(&p,"encoded.zip").unwrap();
    let v=apple_health::import_bound(&mut t.db,"authorized-export.zip",apple_health::now(),&json!({"xmlBytes":2048}),|_|{},None,source.0,true,||{t.dir.validate()?;t.file.validate_unique()}).unwrap();
    assert_eq!(v["inserted"],1);assert_eq!(v["attachments"],1);
    let before:i64=t.db.query_row("SELECT count(*) FROM records",[],|r|r.get(0)).unwrap();
    let source=apple_health_input::open(&p,"encoded.zip").unwrap();
    assert!(apple_health::import_bound(&mut t.db,"authorized-export.zip",apple_health::now(),&json!({"xmlBytes":64}),|_|{},None,source.0,true,||{t.dir.validate()?;t.file.validate_unique()}).is_err());
    assert_eq!(t.db.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0)).unwrap(),before);
}
