//! Private cumulative SourcePort. Only explicit host calls expose these operations.
mod repository;mod runtime_root;mod artifact_io;mod apple_health;mod apple_health_api;
mod health_domain;mod health_snapshot;mod health_ingestion;mod source_api;mod source_file;
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
pub fn imported_health_path(fixture:&str)->Result<Option<std::path::PathBuf>>{let root=runtime_root::verify()?;if fixture.is_empty()||fixture.len()>60||!fixture.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-'){return Err(Error::new("fixture_rejected"))}let path=root.join(format!("{fixture}.sqlite"));if !path.try_exists().map_err(|_|Error::new("source_unavailable"))?{return Ok(None)}let m=std::fs::symlink_metadata(&path).map_err(|_|Error::new("source_unavailable"))?;use std::os::unix::fs::MetadataExt;if !m.is_file()||m.file_type().is_symlink()||m.nlink()!=1||m.mode()&0o777!=0o600{return Err(Error::new("source_unavailable"))}let c=rusqlite::Connection::open_with_flags(&path,rusqlite::OpenFlags::SQLITE_OPEN_READ_ONLY|rusqlite::OpenFlags::SQLITE_OPEN_NOFOLLOW)?;let found:bool=c.query_row("SELECT EXISTS(SELECT 1 FROM records WHERE json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_batch')",[],|r|r.get(0))?;Ok(if found{Some(path)}else{None})}
