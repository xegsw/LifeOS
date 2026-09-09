//! Fixed authorized one-shot importer. No Tauri, model, provider or credential startup.
use crate::{apple_health, artifact_io::{Dir,OwnedFile}, repository::{self,Error}};
use rusqlite::{Connection,OpenFlags};
use serde_json::{Value,json};
use std::{path::Path,io::Write,os::fd::{FromRawFd}};
type R<T> = Result<T,Error>;
struct Target { dir:Dir, file:OwnedFile, db:Connection }
impl Target {
    fn create(parent:&Path, leaf:&str)->R<Self> {
        let path=parent.join(leaf).join("health-import.sqlite");
        let parent=Dir::absolute(parent,false,false)?;
        let dir=parent.new_child(leaf)?; // EEXIST always fails; never adopts existing contents.
        let file=dir.create("health-import.sqlite")?;

        let db=Connection::open_with_flags(path,OpenFlags::SQLITE_OPEN_READ_WRITE|OpenFlags::SQLITE_OPEN_NO_MUTEX|OpenFlags::SQLITE_OPEN_NOFOLLOW)?;
        dir.validate()?;file.validate_unique()?;
        db.execute_batch("PRAGMA journal_mode=DELETE; PRAGMA temp_store=MEMORY; PRAGMA foreign_keys=ON; CREATE TABLE meta(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL); INSERT INTO meta VALUES(1,0); CREATE TABLE requests(id TEXT PRIMARY KEY,operation TEXT NOT NULL,payload TEXT NOT NULL,result TEXT NOT NULL); CREATE TABLE audit(id INTEGER PRIMARY KEY,event TEXT NOT NULL,ref TEXT NOT NULL,at INTEGER NOT NULL);")?;
        for t in repository::TABLES {db.execute_batch(&format!("CREATE TABLE {t}(id TEXT PRIMARY KEY,body TEXT NOT NULL CHECK(json_valid(body)));") )?;}
        Ok(Self{dir,file,db})
    }
    fn resume(parent:&Path, leaf:&str, origin:&Value)->R<Self> {
        let parent_dir=Dir::absolute(parent,false,false)?;
        let dir=parent_dir.child(leaf,false)?;
        let mut entries=dir.entries()?;entries.sort();
        let allowed=["health-import.sqlite",".s3-closure-2-attempt.json",".s3-closure-3-attempt-1.json",".s3-closure-3-attempt-2.json",".s3-closure-3-attempt-3.json"];
        if !entries.iter().all(|e|allowed.contains(&e.as_str())) || !entries.iter().any(|e|e=="health-import.sqlite") {return Err(Error::new("controlled_target_not_pristine"));}
        for name in entries.iter().filter(|e|e.as_str()!="health-import.sqlite") {
            let mut marker=dir.open(name)?;marker.validate_unique()?;
            let m:Value=serde_json::from_slice(&marker.read_limit(1024)?).map_err(|_|Error::new("controlled_origin_rejected"))?;
            let auth=if name==".s3-closure-2-attempt.json"{"P3-149-S3-closure-2-user-allowed"}else{"P3-149-S3-closure-3-user-complete"};
            if m["authorization"]!=auth || m["prior_empty_target_verified"]!=true{return Err(Error::new("controlled_origin_rejected"));}
        }
        let attempt=(1..=3).find(|i|!entries.contains(&format!(".s3-closure-3-attempt-{i}.json"))).ok_or_else(||Error::new("controlled_retry_limit"))?;
        if (attempt+1..=3).any(|i|entries.contains(&format!(".s3-closure-3-attempt-{i}.json"))){return Err(Error::new("controlled_origin_rejected"));}
        let file=dir.open("health-import.sqlite")?;
        file.validate_unique()?;
        for path in [parent.join(leaf),parent.join(leaf).join("health-import.sqlite")] {
            let m=std::fs::symlink_metadata(path).map_err(|_|Error::new("controlled_origin_rejected"))?;
            let created=m.created().map_err(|_|Error::new("controlled_origin_rejected"))?.duration_since(std::time::UNIX_EPOCH).map_err(|_|Error::new("controlled_origin_rejected"))?.as_millis() as u64;
            if created<origin["earliest_ms"].as_u64().unwrap_or(u64::MAX) || created>origin["latest_ms"].as_u64().unwrap_or(0) {return Err(Error::new("controlled_origin_rejected"));}
        }
        let db=Connection::open_with_flags(parent.join(leaf).join("health-import.sqlite"),OpenFlags::SQLITE_OPEN_READ_WRITE|OpenFlags::SQLITE_OPEN_NO_MUTEX|OpenFlags::SQLITE_OPEN_NOFOLLOW)?;
        dir.validate()?;file.validate_unique()?;
        // Inspect only schema/counts, never return any stored body to an external channel.
        let mut names=Vec::new();
        {let mut q=db.prepare("SELECT name,type FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY name")?;
        let rows=q.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?)))?;
        for row in rows {let (name,typ)=row?;if typ!="table"{return Err(Error::new("controlled_target_not_pristine"));}names.push(name);}}
        let mut expected=repository::TABLES.iter().map(|s|s.to_string()).collect::<Vec<_>>();expected.extend(["meta".into(),"requests".into(),"audit".into()]);expected.sort();
        if names!=expected{return Err(Error::new("controlled_target_not_pristine"));}
        for table in expected.iter().filter(|s|s.as_str()!="meta") {
            let n:i64=db.query_row(&format!("SELECT count(*) FROM {table}"),[],|r|r.get(0))?;
            if n!=0{return Err(Error::new("controlled_target_not_pristine"));}
        }
        let meta:i64=db.query_row("SELECT count(*) FROM meta WHERE id=1 AND revision=0",[],|r|r.get(0))?;
        let all:i64=db.query_row("SELECT count(*) FROM meta",[],|r|r.get(0))?;
        if meta!=1 || all!=1{return Err(Error::new("controlled_target_not_pristine"));}
        db.execute_batch("PRAGMA journal_mode=DELETE; PRAGMA temp_store=MEMORY; PRAGMA foreign_keys=ON;")?;
        dir.validate()?;file.validate_unique()?;
        let mut marker=dir.create(&format!(".s3-closure-3-attempt-{attempt}.json"))?;
        marker.write_all(b"{\"authorization\":\"P3-149-S3-closure-3-user-complete\",\"prior_empty_target_verified\":true,\"automatic_retry\":false}")?;marker.sync()?;dir.sync()?;
        Ok(Self{dir,file,db})
    }
    fn import(&mut self, source:apple_health_input::Source, interrupt:Option<u64>)->R<Value> {
        let dir=&self.dir;let file=&self.file;
        let limits:Value=serde_json::from_str(include_str!("../apple_health_limits.json")).map_err(|_|Error::new("health_limits_rejected"))?;
        apple_health::import_bound(&mut self.db,"authorized-export.zip",apple_health::now(),&limits,|_|{},interrupt,source.0,true,||{dir.validate()?;file.validate_unique()})
    }
}
mod apple_health_input {
    use super::*;
    pub(super) struct Source(pub(crate) crate::artifact_io::ReadInput);
    pub(super) fn open(parent:&Path,name:&str)->R<Source>{Ok(Source(Dir::absolute(parent,false,false)?.read_input(name)?))}
}
fn receipt(r:Result<Value,Error>, target_created:bool)->Value {
    match r {
        Ok(v)=>json!({"status":v["status"],"target_verified":target_created,"supported":v["inserted"].as_u64().unwrap_or(0)+v["duplicates"].as_u64().unwrap_or(0),"inserted":v["inserted"],"duplicates":v["duplicates"],"unsupported":v["unsupported"],"skipped":v["skipped"].as_u64().unwrap_or(0),"unprojected":v["unprojected"].as_u64().unwrap_or(0),"attachments_unprocessed":v["attachments"],"failed":0,"retained":true,"network":false,"model":false}),
        Err(e)=>json!({"status":"failed","code":safe_code(&e.code),"supported":null,"inserted":0,"duplicates":null,"unsupported":null,"attachments_unprocessed":null,"failed":1,"target_verified":if target_created{json!(true)}else{Value::Null},"retained":true,"network":false,"model":false}),
    }
}
fn safe_code(s:&str)->&str {
    match s {"artifact_boundary_rejected"|"controlled_retry_limit"|"controlled_origin_rejected"|"controlled_target_not_pristine"|"controlled_arguments_rejected"|"database_unavailable"|"health_date_rejected"|"health_document_corrupt"|"health_file_changed"|"health_file_limit"|"health_interval_rejected"|"health_limits_rejected"|"health_parser_failed"|"health_parser_incomplete"|"health_parser_unavailable"|"health_projection_limit"|"health_records_limit"|"health_row_rejected"|"health_source_count_limit"|"health_source_rejected"|"health_test_interrupted"|"health_time_limit"|"health_unit_rejected"|"health_value_rejected"|"health_xml_entity_rejected"|"health_xml_external_dtd_rejected"|"health_xml_incomplete"|"health_xml_limit"|"health_xml_root_rejected"|"health_xml_structure_limit"|"health_xml_token_limit"|"health_zip64_unsupported"|"health_zip_compression_rejected"|"health_zip_corrupt"|"health_zip_encrypted"|"health_zip_entries_limit"|"health_zip_expansion_limit"|"health_zip_path_rejected"|"health_zip_special_rejected"|"health_zip_xml_ambiguous"=>s,_=>"controlled_import_failed"}
}
pub fn entry() {
    std::panic::set_hook(Box::new(|_|{}));
    unsafe {libc::umask(0o077);let lim=libc::rlimit{rlim_cur:0,rlim_max:0};libc::setrlimit(libc::RLIMIT_CORE,&lim);}
    let out=unsafe{libc::dup(1)};
    if out>=0{unsafe{libc::fcntl(out,libc::F_SETFD,libc::FD_CLOEXEC);}}
    unsafe{let fd=libc::open(c"/dev/null".as_ptr(),libc::O_RDWR);if fd>=0{libc::dup2(fd,0);libc::dup2(fd,1);libc::dup2(fd,2);if fd>2{libc::close(fd);}}}
    let mut created=false;
    let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||->R<Value>{
        if std::env::args().count()!=2{return Err(Error::new("controlled_arguments_rejected"));}
        let source=apple_health_input::open(Path::new("/Users/xxe/Downloads"),"导出.zip")?;
        let origin:Value=serde_json::from_str(include_str!("../controlled_origin.json")).map_err(|_|Error::new("controlled_origin_rejected"))?;
        let mut target=Target::resume(Path::new("/Users/xxe/Documents"),"LifeOS-Health-Import-Pilot-1",&origin)?;created=true;
        target.import(source,None)
    })).unwrap_or_else(|_|Err(Error::new("controlled_import_failed")));
    let value=receipt(result,created);
    if out>=0{let mut out=unsafe{std::fs::File::from_raw_fd(out)};let _=writeln!(out,"{}",value);}
    if value["status"]=="failed" {std::process::exit(2);}
}
#[cfg(test)]
mod tests;
