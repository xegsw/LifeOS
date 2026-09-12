#[cfg(all(feature="boundary-tests",feature="controlled-real"))]
compile_error!("real boundary tests forbidden");
// Private cumulative SourcePort. Only explicit host calls expose these operations.
mod repository;mod runtime_root;mod artifact_io;mod apple_health;mod apple_health_api;
mod health_target;mod health_domain;mod health_snapshot;mod health_ingestion;mod source_api;mod source_file;
mod source_store;mod source_targets;mod source_worker;mod strict_json;
use serde_json::{Value,json};use std::sync::{Mutex,MutexGuard};use rusqlite::OptionalExtension;
pub use repository::Error;pub type Result<T>=std::result::Result<T,Error>;
static GATE:Mutex<()>=Mutex::new(());
fn gate()->Result<MutexGuard<'static,()>>{GATE.lock().map_err(|_|Error::new("source_busy"))}
pub const COMMANDS:[&str;6]=["connect_source_directory","control_source_job","get_source_status","authorize_source_target","get_source_evidence","import_apple_health_file"];
pub fn dispatch(command:&str,bytes:&[u8],fixture:&str)->Result<Value>{
 if bytes.len()>4096{return Err(Error::new("source_request_limit"))}let raw=std::str::from_utf8(bytes).map_err(|_|Error::new("source_contract_rejected"))?;let v=strict_json::parse(raw)?;
 if command=="import_apple_health_file"{let r=apple_health_api::parse(raw)?;return apple_health_api::dispatch(r,fixture)}
 if !source_api::COMMANDS.contains(&command){return Err(Error::new("operation_rejected"))}
 let r:source_api::Request=serde_json::from_value(v).map_err(|_|Error::new("source_contract_rejected"))?;let _g=gate()?;source_api::dispatch(command,r,fixture)
}
pub fn imported_health_path(fixture:&str)->Result<Option<std::path::PathBuf>>{let root=runtime_root::verify()?;if fixture.is_empty()||fixture.len()>60||!fixture.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-'){return Err(Error::new("fixture_rejected"))}let path=runtime_root::store_path(fixture)?;if !path.try_exists().map_err(|_|Error::new("source_unavailable"))?{return Ok(None)}let m=std::fs::symlink_metadata(&path).map_err(|_|Error::new("source_unavailable"))?;use std::os::unix::fs::MetadataExt;if !m.is_file()||m.file_type().is_symlink()||m.nlink()!=1||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o600{return Err(Error::new("source_unavailable"))}let c=rusqlite::Connection::open_with_flags(&path,rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY|rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW)?;c.busy_timeout(std::time::Duration::from_millis(150))?;let found:bool=c.query_row("SELECT EXISTS(SELECT 1 FROM records WHERE json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_batch')",[],|r|r.get(0))?;Ok(if found{Some(path)}else{None})}
fn reference(c:&rusqlite::Connection,fixture:&str,row:&Value)->Result<Value>{let owner=row["sourceId"].as_str().ok_or_else(||Error::new("source_corrupt"))?;let lease=source_api::lease(c,owner)?;let len=row["text"].as_str().ok_or_else(||Error::new("source_corrupt"))?.chars().count().min(800);Ok(json!({"store":fixture,"rootIdentity":source_api::hex(runtime_root::ROOT),"connectorId":owner,"sourceRef":row["sourceFile"],"recordId":row["id"],"segmentId":row["id"],"version":row["version"],"authorizationGeneration":lease.generation,"scanEpoch":lease.epoch,"locator":row["locator"],"startScalar":0,"endScalar":len,"contentHash":row["contentHash"]}))}
fn validate_inner(c:&rusqlite::Connection,fixture:&str,r:&Value)->Result<()>{if r["store"]!=fixture||r["rootIdentity"]!=source_api::hex(runtime_root::ROOT){return Err(Error::new("source_identity_rejected"))}source_store::validate_reference(c,r)?;
 if r["connectorId"]=="directory" {
  let grant=source_file::FileGrant::for_source(&runtime_root::source_path())?;let root=grant.root_identity()?;
  let bound:String=c.query_row("SELECT target_ref FROM connector_grants WHERE id='root:directory' AND state='active'",[],|v|v.get(0))?;
  if serde_json::from_str::<Value>(&bound).ok()!=Some(json!([root.dev,root.ino])){return Err(Error::new("source_identity_rejected"))}
  let (path,identity):(String,String)=c.query_row("SELECT external_ref,identity FROM source_files WHERE id=?1",[r["sourceRef"].as_str()],|v|Ok((v.get(0)?,v.get(1)?)))?;
  if serde_json::to_value(grant.identity(&path)?).ok()!=serde_json::from_str::<Value>(&identity).ok(){return Err(Error::new("source_context_stale"))}
 }
let hash:String=c.query_row("SELECT json_extract(body,'$.contentHash') FROM records WHERE id=?1",[r["recordId"].as_str()],|v|v.get(0))?;if r["contentHash"]!=hash{return Err(Error::new("context_stale"))}Ok(())}
pub fn context(fixture:&str,question:&str)->Result<Vec<Value>>{if !runtime_root::active(){return Ok(vec![])}let _g=gate()?;let root=runtime_root::verify()?;let path=runtime_root::store_path(fixture)?;if !path.try_exists().map_err(|_|Error::new("source_unavailable"))?{return Ok(vec![])}let c=repository::open(fixture)?;source_store::init(&c)?;let lease=match source_api::lease(&c,"directory"){Ok(v)=>v,Err(_)=>return Ok(vec![])};if source_store::check(&c,&lease).is_err(){return Ok(vec![])}let rows=source_store::search(&c,&lease,question)?;rows.into_iter().filter(|r|r["text"].as_str().is_some_and(|v|!v.is_empty())).map(|mut r|{let sr=reference(&c,fixture,&r)?;validate_inner(&c,fixture,&sr)?;r["engineRef"]=sr;r["text"]=json!(r["text"].as_str().unwrap().chars().take(800).collect::<String>());Ok(r)}).collect()}
pub fn valid(fixture:&str,r:&Value)->bool{if !runtime_root::active(){return false}let Ok(_g)=gate()else{return false};let Ok(c)=repository::open(fixture)else{return false};validate_inner(&c,fixture,r).is_ok()}
pub struct SendFence{_gate:MutexGuard<'static,()>}
pub fn send_fence(fixture:&str,refs:&[Value])->Result<Option<SendFence>>{if refs.is_empty(){return Ok(None)}let g=gate()?;let c=repository::open(fixture)?;for r in refs{validate_inner(&c,fixture,r)?;}Ok(Some(SendFence{_gate:g}))}

pub fn import_running()->bool{apple_health_api::running()}

#[cfg(feature="boundary-tests")]pub use health_target::synthetic_boundary_check;
