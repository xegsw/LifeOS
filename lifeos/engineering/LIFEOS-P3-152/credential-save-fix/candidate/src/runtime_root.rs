//! Fixed compile-time modes. No caller-selected paths or legacy fallback.
use std::{path::{Path,PathBuf},fs,os::unix::fs::{MetadataExt,OpenOptionsExt,DirBuilderExt},io::Write};
use crate::repository::Error;
#[cfg(all(feature="controlled-real",test))]compile_error!("real tests are forbidden; use synthetic branch tests");
pub const REAL_ROOT:&str="/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1";
pub const HEALTH_DB:&str="/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite";
pub fn is_real()->bool{cfg!(feature="controlled-real")}
pub fn mode()->&'static str{if is_real(){"real"}else{"synthetic"}}
fn rejected()->Error{Error::new("runtime_target_rejected")}
fn check(p:&Path,dir:bool,mode:u32)->Result<(),Error>{let m=fs::symlink_metadata(p).map_err(|_|rejected())?;if m.file_type().is_symlink()||m.is_dir()!=dir||(!dir&&(!m.is_file()||m.nlink()!=1))||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=mode{return Err(rejected());}Ok(())}
fn real_root_at(root:&Path)->Result<PathBuf,Error>{
 let mut ancestor=PathBuf::new();for part in root.parent().ok_or_else(rejected)?.components(){ancestor.push(part);let m=fs::symlink_metadata(&ancestor).map_err(|_|rejected())?;if !m.is_dir()||m.file_type().is_symlink(){return Err(rejected());}}
 let marker=root.join(".lifeos-p3-152-owner.json");let expected=serde_json::json!({"task":"P3-152","mode":"real","owner":"01a07f0e-dbbd-7d23-9e6d-68f2152f9484","root":root});
 match fs::symlink_metadata(root){Err(e) if e.kind()==std::io::ErrorKind::NotFound=>{fs::DirBuilder::new().mode(0o700).create(root).map_err(|_|rejected())?;let mut f=fs::OpenOptions::new().create_new(true).write(true).mode(0o600).custom_flags(libc::O_NOFOLLOW|libc::O_CLOEXEC).open(&marker).map_err(|_|rejected())?;f.write_all(expected.to_string().as_bytes()).map_err(|_|rejected())?;f.sync_all().map_err(|_|rejected())?;},Ok(_)=>(),Err(_)=>return Err(rejected())}
 check(root,true,0o700)?;check(&marker,false,0o600)?;let bytes=fs::read(&marker).map_err(|_|rejected())?;if bytes.len()>1024||serde_json::from_slice::<serde_json::Value>(&bytes).ok()!=Some(expected){return Err(rejected());}
 for entry in fs::read_dir(root).map_err(|_|rejected())?{let entry=entry.map_err(|_|rejected())?;let name=entry.file_name();let n=name.to_str().ok_or_else(rejected)?;if ![".lifeos-p3-152-owner.json",".runtime","tmp","conversation.sqlite","conversation.sqlite-wal","conversation.sqlite-shm","conversation.sqlite-journal","provider.sqlite","provider.sqlite-wal","provider.sqlite-shm","provider.sqlite-journal","source-engine-v1"].contains(&n){return Err(rejected());}check(&entry.path(),[".runtime","tmp","source-engine-v1"].contains(&n),if [".runtime","tmp","source-engine-v1"].contains(&n){0o700}else{0o600})?;}
 for n in [".runtime","tmp"]{let p=root.join(n);match fs::DirBuilder::new().mode(0o700).create(&p){Ok(())=>(),Err(e) if e.kind()==std::io::ErrorKind::AlreadyExists=>(),Err(_)=>return Err(rejected())}check(&p,true,0o700)?;}Ok(root.to_owned())
}
pub fn verify()->Result<PathBuf,Error>{if is_real(){real_root_at(Path::new(REAL_ROOT))}else{crate::health_conversation_host::verify_root()?;Ok(PathBuf::from(crate::health_conversation_host::ROOT).join("synthetic"))}}
#[cfg(test)]mod tests{use super::*;#[test]fn new_root_and_foreign_conflict_fail_closed(){crate::health_conversation_host::verify_root().unwrap();let root=PathBuf::from(crate::health_conversation_host::ROOT).join(format!("root-test-{}-{}",std::process::id(),crate::conversation_store::uid("case")));assert_eq!(real_root_at(&root).unwrap(),root);assert_eq!(real_root_at(&root).unwrap(),root);fs::write(root.join("foreign"),b"synthetic-only").unwrap();assert!(real_root_at(&root).is_err());assert_eq!(fs::read(root.join("foreign")).unwrap(),b"synthetic-only");}#[test]fn real_root_constants_and_synthetic_mode(){assert!(!is_real());assert_eq!(REAL_ROOT,"/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1");assert_eq!(HEALTH_DB,"/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite");}}

#[cfg(test)]mod credential_root_tests {
 use super::*;
 #[test]fn source_child_preserves_parent_store_allowlist(){
  crate::health_conversation_host::verify_root().unwrap();
  let root=PathBuf::from(crate::health_conversation_host::ROOT).join(crate::conversation_store::uid("credential-root"));
  real_root_at(&root).unwrap();
  fs::DirBuilder::new().mode(0o700).create(root.join("source-engine-v1")).unwrap();
  assert_eq!(real_root_at(&root).unwrap(),root);
  fs::OpenOptions::new().create_new(true).write(true).mode(0o600).open(root.join("provider.sqlite")).unwrap();
  assert_eq!(real_root_at(&root).unwrap(),root);
  use std::os::unix::fs::PermissionsExt;
  fs::set_permissions(root.join("source-engine-v1"),fs::Permissions::from_mode(0o755)).unwrap();
  assert_eq!(real_root_at(&root).unwrap_err().code,"runtime_target_rejected");
 }
}
