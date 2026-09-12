//! P3-157 existing-only contract check. No content read, CREATE, ALTER or repair.
use super::*;
impl Store {
 pub(super) fn prepare_database_file(path:&Path,existing_only:bool)->R<bool>{
  let fresh=match fs::symlink_metadata(path){Ok(_)=>false,Err(e) if e.kind()==std::io::ErrorKind::NotFound=>true,Err(_)=>return Err(error("store_rejected"))};
  if fresh&&existing_only{return Err(error("store_contract_rejected"))}
  if fresh{fs::OpenOptions::new().create_new(true).write(true).mode(0o600).open(path).map_err(|_|error("store_rejected"))?;}
  Ok(fresh)
 }

 pub(super) fn validate_existing_schema(c:&Connection)->R<()> {
  for table in TABLES.into_iter().chain(["meta","requests","audit"]) {
   let is_table:bool=c.query_row("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name=?1)",[table],|r|r.get(0))?;
   if !is_table{return Err(error("store_contract_rejected"))}
   let mut stmt=c.prepare(&format!("PRAGMA table_info({table})"))?;
   let columns=stmt.query_map([],|r|Ok((r.get::<_,String>(1)?,r.get::<_,String>(2)?,r.get::<_,i64>(5)?)))?.collect::<Result<Vec<_>,_>>()?;
   let expected:Vec<(&str,&str,i64)>=match table {
    "meta"=>vec![("id","INTEGER",1),("revision","INTEGER",0)],
    "requests"=>vec![("id","TEXT",1),("operation","TEXT",0),("payload","TEXT",0),("result","TEXT",0)],
    "audit"=>vec![("id","INTEGER",1),("event","TEXT",0),("ref","TEXT",0),("at","INTEGER",0)],
    _=>vec![("id","TEXT",1),("body","TEXT",0)]};
   if columns.len()!=expected.len()||columns.iter().zip(expected).any(|((name,ty,pk),(en,et,ep))|name!=en||ty.to_ascii_uppercase()!=et||*pk!=ep){return Err(error("store_contract_rejected"))}
  }Ok(())
 }
}
#[cfg(test)]mod tests {
 use super::*;
 #[test]fn existing_only_missing_file_is_never_created(){let p=PathBuf::from(ROOT).join("synthetic").join(crate::conversation_store::uid("existing-only-missing"));assert_eq!(Store::prepare_database_file(&p,true).unwrap_err().code,"store_contract_rejected");assert!(!p.exists());}
 #[test]fn existing_only_existing_file_is_not_changed(){let p=PathBuf::from(ROOT).join("synthetic").join(crate::conversation_store::uid("existing-only-kept"));fs::OpenOptions::new().create_new(true).write(true).mode(0o600).open(&p).unwrap();fs::write(&p,b"synthetic-existing-file").unwrap();assert!(!Store::prepare_database_file(&p,true).unwrap());assert_eq!(fs::read(&p).unwrap(),b"synthetic-existing-file");}
 fn schema()->Connection{let c=Connection::open_in_memory().unwrap();c.execute_batch("CREATE TABLE meta(id INTEGER PRIMARY KEY,revision INTEGER);CREATE TABLE requests(id TEXT PRIMARY KEY,operation TEXT,payload TEXT,result TEXT);CREATE TABLE audit(id INTEGER PRIMARY KEY,event TEXT,ref TEXT,at INTEGER);").unwrap();for t in TABLES{c.execute_batch(&format!("CREATE TABLE {t}(id TEXT PRIMARY KEY,body TEXT);" )).unwrap();}c}
 #[test]fn every_required_table_missing_fails_before_any_write(){for t in TABLES.into_iter().chain(["meta","requests","audit"]){let c=schema();c.execute_batch(&format!("DROP TABLE {t}")).unwrap();let changes=c.total_changes();assert_eq!(Store::validate_existing_schema(&c).unwrap_err().code,"store_contract_rejected","{t}");assert_eq!(c.total_changes(),changes);assert!(!c.query_row("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE name=?1)",[t],|r|r.get::<_,bool>(0)).unwrap());}}
 #[test]fn existing_complete_schema_is_readonly(){let c=schema();c.execute("INSERT INTO records VALUES('kept','synthetic original')",[]).unwrap();let n=c.total_changes();Store::validate_existing_schema(&c).unwrap();Store::validate_existing_schema(&c).unwrap();assert_eq!(n,c.total_changes());assert_eq!(c.query_row("SELECT body FROM records WHERE id='kept'",[],|r|r.get::<_,String>(0)).unwrap(),"synthetic original");}
 #[test]fn view_wrong_column_type_or_key_is_not_repaired(){for ddl in ["CREATE VIEW feedback AS SELECT 'x' AS id,'{}' AS body","CREATE TABLE feedback(id TEXT PRIMARY KEY,wrong TEXT)","CREATE TABLE feedback(id INTEGER PRIMARY KEY,body TEXT)","CREATE TABLE feedback(id TEXT,body TEXT)"]{let c=schema();c.execute_batch("DROP TABLE feedback").unwrap();c.execute_batch(ddl).unwrap();let n=c.total_changes();assert_eq!(Store::validate_existing_schema(&c).unwrap_err().code,"store_contract_rejected");assert_eq!(n,c.total_changes());}}
}
