//! Fixed-target append adapter. Never creates or migrates a health database.
use crate::{artifact_io::{Dir,OwnedFile},repository::Error,apple_health,runtime_root};
use rusqlite::{Connection,OpenFlags};use serde_json::Value;use std::path::Path;
type R<T>=Result<T,Error>;
fn moved(c:*mut rusqlite::ffi::sqlite3)->R<()>{let mut changed:i32=0;let rc=unsafe{rusqlite::ffi::sqlite3_file_control(c,c"main".as_ptr(),rusqlite::ffi::SQLITE_FCNTL_HAS_MOVED,(&mut changed as *mut i32).cast())};if rc!=rusqlite::ffi::SQLITE_OK||changed!=0{return Err(Error::new("health_target_changed"))}Ok(())}
fn schema(c:&Connection)->R<()>{for (table,columns) in [("records",vec!["id","body"]),("sources",vec!["id","body"]),("states",vec!["id","body"]),("meta",vec!["id","revision"])]{let mut q=c.prepare(&format!("PRAGMA table_info({table})"))?;let got=q.query_map([],|r|r.get::<_,String>(1))?.collect::<std::result::Result<Vec<_>,_>>()?;if !columns.iter().all(|n|got.iter().any(|v|v==n)){return Err(Error::new("health_schema_rejected"))}}let n:i64=c.query_row("SELECT count(*) FROM meta WHERE id=1",[],|r|r.get(0))?;if n!=1{return Err(Error::new("health_schema_rejected"))}Ok(())}
fn open_target(path:&Path)->R<(Connection,OwnedFile)>{let d=Dir::absolute(path.parent().ok_or_else(||Error::new("health_target_rejected"))?,false,false)?;let name=path.file_name().and_then(|n|n.to_str()).ok_or_else(||Error::new("health_target_rejected"))?;let anchor=d.open(name)?;anchor.validate_unique()?;for suffix in ["-wal","-shm","-journal"]{let n=format!("{name}{suffix}");if d.exists(&n)?{d.open(&n)?.validate_unique()?;}}
 let c=Connection::open_with_flags(path,OpenFlags::SQLITE_OPEN_READ_WRITE|OpenFlags::SQLITE_OPEN_NOFOLLOW)?;c.busy_timeout(std::time::Duration::ZERO)?;moved(unsafe{c.handle()})?;anchor.validate_unique()?;schema(&c)?;Ok((c,anchor))}
pub fn import_fixed(name:&str,limits:&Value,progress:impl FnMut(u64))->R<Value>{if !runtime_root::is_real()||name!="导出.zip"{return Err(Error::new("health_filename_rejected"))}let root=runtime_root::verify()?;let _lease=runtime_root::lock_file(&root.join(".runtime/health-import.lock"))?;
 let zip=Path::new(runtime_root::HEALTH_ZIP);let input=Dir::absolute(zip.parent().unwrap(),false,false)?.read_input("导出.zip")?;
 let (mut c,anchor)=open_target(Path::new(runtime_root::HEALTH_DB))?;let raw=unsafe{c.handle()};
 apple_health::import_bound(&mut c,name,apple_health::now(),limits,progress,None,input,true,||{anchor.validate_unique()?;moved(raw)})
}

#[cfg(feature="boundary-tests")]
pub fn synthetic_boundary_check()->R<()> {
 use std::{fs,os::unix::fs::{OpenOptionsExt,symlink}};use serde_json::json;
 if runtime_root::is_real(){return Err(Error::new("real_tests_forbidden"))}
 let root=runtime_root::verify()?;let case=root.join(format!("target-boundary-{}",std::process::id()));fs::create_dir(&case).map_err(|_|Error::new("fixture_conflict"))?;use std::os::unix::fs::PermissionsExt;fs::set_permissions(&case,fs::Permissions::from_mode(0o700)).unwrap();
 let parent=Dir::absolute(&case,false,true)?;let foreign=parent.child_new("foreign")?;let mut note=foreign.create("keep")?;note.write_all(b"preserve synthetic foreign content")?;assert!(parent.child_new("foreign").is_err());assert_eq!(foreign.open("keep")?.read_limit(100)?,b"preserve synthetic foreign content");
 let path=case.join("health.sqlite");drop(fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(&path).unwrap());
 let c=Connection::open(&path)?;c.execute_batch("CREATE TABLE records(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE states(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE meta(id INTEGER PRIMARY KEY,revision INTEGER);INSERT INTO meta VALUES(1,0)")?;drop(c);
 let limits:Value=serde_json::from_str(include_str!("../apple_health_limits.json")).unwrap();
 let run=|name:&str|->R<Value>{let input=Dir::absolute(&root.join("inputs"),false,true)?.read_input(name)?;let(mut c,anchor)=open_target(&path)?;let raw=unsafe{c.handle()};apple_health::import_bound(&mut c,name,apple_health::now(),&limits,|_|{},None,input,true,||{anchor.validate_unique()?;moved(raw)})};
 assert_eq!(run("health-demo.zip")?["inserted"],json!(3));assert_eq!(run("health-demo.zip")?["status"],json!("duplicate"));
 let count=||->i64{Connection::open(&path).unwrap().query_row("SELECT count(*) FROM records",[],|r|r.get(0)).unwrap()};let before=count();assert!(run("broken.xml").is_err());assert_eq!(count(),before);
 let blocker=Connection::open(&path)?;blocker.execute_batch("BEGIN IMMEDIATE")?;assert!(run("health-demo.zip").is_err());blocker.execute_batch("ROLLBACK")?;assert_eq!(count(),before);
 assert!(open_target(&case.join("missing.sqlite")).is_err());assert!(!case.join("missing.sqlite").exists());
 let alias=case.join("alias.sqlite");symlink(&path,&alias).unwrap();assert!(open_target(&alias).is_err());
 let wrong=case.join("wrong.sqlite");drop(fs::OpenOptions::new().write(true).create_new(true).mode(0o600).open(&wrong).unwrap());Connection::open(&wrong)?.execute_batch("CREATE TABLE unchanged(id INTEGER)")?;assert!(open_target(&wrong).is_err());
 let lock=runtime_root::lock_file(&case.join("write.lock"))?;assert!(runtime_root::lock_file(&case.join("write.lock")).is_err());drop(lock);assert!(runtime_root::lock_file(&case.join("write.lock")).is_ok());
 Ok(())
}
