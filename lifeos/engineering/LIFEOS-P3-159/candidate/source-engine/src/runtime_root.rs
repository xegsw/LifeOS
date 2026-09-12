//! Fixed targets authorized by the P3-152 real activation delta. No runtime path input.
use crate::repository::Error;
use std::{path::{Path,PathBuf},fs,os::unix::fs::{MetadataExt,OpenOptionsExt},os::fd::AsRawFd,sync::{Mutex,OnceLock,atomic::{AtomicBool,Ordering}}};
#[cfg(feature="controlled-real")]pub const ROOT:&str="/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/source-engine-v1";
#[cfg(not(any(feature="controlled-real",feature="online-synthetic")))]pub const ROOT:&str="/private/tmp/lifeos-p3-159-unified-proactive-v1/offline/source-engine";
#[cfg(feature="online-synthetic")]pub const ROOT:&str="/private/tmp/lifeos-p3-159-unified-proactive-v1/online-synthetic/source-engine";
pub const PARENT:&str="/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1";
pub const HEALTH_DB:&str="/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite";
pub const HEALTH_ZIP:&str="/Users/xxe/Downloads/导出.zip";
static ACTIVE:AtomicBool=AtomicBool::new(false);
static LEASE:OnceLock<Mutex<Option<(fs::File,crate::artifact_io::Dir)>>>=OnceLock::new();
pub fn is_real()->bool{cfg!(feature="controlled-real")}
pub fn active()->bool{!is_real()||ACTIVE.load(Ordering::Acquire)}
pub fn source_path()->PathBuf{if is_real(){PathBuf::from("/Users/xxe/IT-obstain")}else{Path::new(ROOT).join("fixtures/app-source")}}
pub fn activate_from_user_click()->Result<(),Error>{verify()?;ACTIVE.store(true,Ordering::Release);Ok(())}
pub fn expected_marker()->Result<serde_json::Value,Error>{Ok(if is_real(){serde_json::json!({"task":"P3-152","mode":"real","version":1,"kind":"source-engine","owner":"01a07f0e-dbbd-7d23-9e6d-68f2152f9484","root":ROOT})}else{serde_json::json!({"task":"P3-159","owner":"01a07f0e-dbbd-7d23-9e6d-68f2152f9484","root":ROOT,"kind":"synthetic-source-engine"})})}
pub fn lock_file(path:&Path)->Result<fs::File,Error>{let f=fs::OpenOptions::new().create(true).write(true).mode(0o600).custom_flags(libc::O_NOFOLLOW|libc::O_CLOEXEC).open(path).map_err(|_|Error::new("source_busy"))?;let m=f.metadata().map_err(|_|Error::new("source_busy"))?;if !m.is_file()||m.nlink()!=1||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o600||unsafe{libc::flock(f.as_raw_fd(),libc::LOCK_EX|libc::LOCK_NB)}!=0{return Err(Error::new("source_busy"))}Ok(f)}
pub fn verify()->Result<PathBuf,Error>{
 if is_real(){
  let mut lease=LEASE.get_or_init(Default::default).lock().map_err(|_|Error::new("source_busy"))?;
  let parent=crate::artifact_io::Dir::absolute(Path::new(PARENT),false,true)?;
  let mut marker=parent.open(".lifeos-p3-152-owner.json")?;
  let expected=serde_json::json!({"task":"P3-152","mode":"real","owner":"01a07f0e-dbbd-7d23-9e6d-68f2152f9484","root":PARENT});
  if serde_json::from_slice::<serde_json::Value>(&marker.read_limit(4096)?).ok()!=Some(expected){return Err(Error::new("engine_marker_rejected"))}
  let d=parent.child("source-engine-v1",false)?;
  let mut f=d.open(".owner.json")?;if serde_json::from_slice::<serde_json::Value>(&f.read_limit(4096)?).ok()!=Some(expected_marker()?){return Err(Error::new("engine_marker_rejected"))}
  for n in ["artifacts","tmp",".runtime"]{d.child(n,false)?;}
  if let Some((fd,held))=lease.as_ref(){held.validate()?;let mut named=held.child(".runtime",false)?.open("source-engine.lock")?;let a=fd.metadata().map_err(|_|Error::new("source_busy"))?;let b=named.descriptor()?.metadata().map_err(|_|Error::new("source_busy"))?;if a.dev()!=b.dev()||a.ino()!=b.ino(){return Err(Error::new("source_busy"))}}else{*lease=Some((lock_file(&Path::new(ROOT).join(".runtime/source-engine.lock"))?,d.clone()))}
  d.validate()?;return Ok(PathBuf::from(ROOT))
 }
 let p=Path::new(ROOT);let m=fs::symlink_metadata(p).map_err(|_|Error::new("engine_root_missing"))?;if !m.is_dir()||m.file_type().is_symlink()||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o700||fs::canonicalize(p).ok().as_deref()!=Some(p){return Err(Error::new("engine_root_rejected"))}
 let d=crate::artifact_io::Dir::absolute(p,false,true)?;let mut f=d.open(".owner.json")?;if serde_json::from_slice::<serde_json::Value>(&f.read_limit(4096)?).ok()!=Some(expected_marker()?){return Err(Error::new("engine_marker_rejected"))}Ok(p.into())
}
pub fn store_path(fixture:&str)->Result<PathBuf,Error>{if fixture.is_empty()||fixture.len()>60||!fixture.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-')||is_real()&&fixture!="conversation"{return Err(Error::new("fixture_rejected"))}Ok(verify()?.join(if is_real(){"sources.sqlite".into()}else{format!("{fixture}.sqlite")}))}
pub fn helper(name:&str)->Result<PathBuf,Error>{match name{"parse_source.py"=>Ok(Path::new(env!("CARGO_MANIFEST_DIR")).join("tools/parse_source.py")),"alias_metadata"=>if is_real(){Ok(std::env::current_exe().map_err(|_|Error::new("helper_unavailable"))?.parent().ok_or_else(||Error::new("helper_unavailable"))?.parent().unwrap().join("Resources/alias_metadata"))}else{Ok(Path::new(ROOT).join("alias_metadata"))},_=>Err(Error::new("helper_unavailable"))}}
