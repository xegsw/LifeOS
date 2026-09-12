//! Synthetic-only contract tests; never built into controlled-real.
use crate::*;
use std::{fs,path::Path,os::unix::fs::PermissionsExt};
use rusqlite::params;
pub fn lifecycle()->Result<()> {
 assert!(!runtime_root::is_real());let root=runtime_root::verify()?;
 let name=format!("update-{}-{}",std::process::id(),std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
 let path=root.join("fixtures").join(&name);fs::create_dir(&path).unwrap();fs::set_permissions(&path,fs::Permissions::from_mode(0o700)).unwrap();
 fs::write(path.join("a.md"),b"synthetic alpha source").unwrap();fs::write(path.join("b.bin"),b"synthetic opaque").unwrap();
 let mut c=repository::open(&name)?;source_store::init(&c)?;
 let mut l=source_store::connect(&mut c,"connect","connector",&name)?;
 let drive=|c:&mut rusqlite::Connection,l:&source_store::Lease|->Result<()>{source_worker::begin(c,l)?;while source_worker::scan_page(c,l)?{}while source_worker::import_one(c,l)?{}source_worker::finalize_scan(c,l)?;Ok(())};
 drive(&mut c,&l)?;
 let file:String=c.query_row("SELECT id FROM source_files WHERE external_ref='a.md'",[],|r|r.get(0))?;
 let identity=|c:&rusqlite::Connection|->Result<(i64,String,i64)>{Ok(c.query_row("SELECT version,artifact_ref,(SELECT count(*) FROM source_segments WHERE file_id=?1) FROM source_files WHERE id=?1",[&file],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?)))?)};
 let first=identity(&c)?;assert_eq!(first.0,1);assert!(first.2>0);
 l=source_store::control(&mut c,&l,"unchanged","refresh")?;drive(&mut c,&l)?;assert_eq!(identity(&c)?,first);
 // Force a new metadata identity while retaining bytes; parsed artifact/version must survive.
 let new=path.join("replacement");fs::write(&new,b"synthetic alpha source").unwrap();fs::rename(new,path.join("a.md")).unwrap();
 l=source_store::control(&mut c,&l,"metadata","refresh")?;drive(&mut c,&l)?;assert_eq!(identity(&c)?,first);
 assert_eq!(c.query_row("SELECT json_extract(counters,'$.outcome') FROM import_jobs WHERE id=?",[&file],|r|r.get::<_,String>(0))?,"unchanged");
 fs::write(path.join("a.md"),b"synthetic alpha changed content").unwrap();let old=l.clone();l=source_store::control(&mut c,&l,"changed","refresh")?;assert!(source_worker::import_one(&mut c,&old).is_err());drive(&mut c,&l)?;assert_eq!(identity(&c)?.0,2);
 let count:i64=c.query_row("SELECT count(*) FROM records",[],|r|r.get(0))?;
 let paused=source_store::control(&mut c,&l,"pause","pause")?;assert!(source_worker::import_one(&mut c,&paused).is_err());
 drop(c);let mut c=repository::open(&name)?;assert_eq!(c.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0))?,count);
 l=source_store::control(&mut c,&paused,"resume","resume")?;let twice=source_store::control(&mut c,&paused,"resume","resume")?;assert_eq!(twice.epoch,l.epoch);
 // Missing originals invalidate references without deleting historical records.
 fs::rename(path.join("a.md"),path.join("retained-original.bin")).unwrap();l=source_store::control(&mut c,&l,"missing","refresh")?;drive(&mut c,&l)?;
 assert_eq!(c.query_row("SELECT parse_state FROM source_files WHERE id=?",[&file],|r|r.get::<_,String>(0))?,"missing");
 assert!(c.query_row("SELECT count(*) FROM records",[],|r|r.get::<_,i64>(0))?>=count);
 fs::rename(path.join("retained-original.bin"),path.join("a.md")).unwrap();l=source_store::control(&mut c,&l,"returned","refresh")?;drive(&mut c,&l)?;
 assert_eq!(c.query_row("SELECT parse_state FROM source_files WHERE id=?",[&file],|r|r.get::<_,String>(0))?,"parsed");assert!(identity(&c)?.0>2);
 let revoked=source_store::control(&mut c,&l,"disconnect","disconnect")?;assert!(source_store::search(&c,&revoked,"alpha").is_err());
 Ok(())
}
