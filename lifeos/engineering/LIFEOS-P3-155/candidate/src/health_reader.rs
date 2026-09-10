use crate::repository::Error;
use rusqlite::{Connection,OpenFlags,OptionalExtension,params};
use serde::Deserialize;
use serde_json::{Value,json};
use std::{fs::File,path::Path,ffi::CString,os::{fd::{AsRawFd,FromRawFd},unix::fs::MetadataExt},io::Read,time::{Instant,Duration}};
type R<T>=Result<T,Error>;
fn err(s:&str)->Error{Error::new(s)}
struct Node{name:String,fd:File}
struct Guard{chain:Vec<Node>,file:File,name:String,stamp:(u64,u64,u64,i64,i64,i64,i64)}
fn stamp(m:&std::fs::Metadata)->(u64,u64,u64,i64,i64,i64,i64){(m.dev(),m.ino(),m.len(),m.mtime(),m.mtime_nsec(),m.ctime(),m.ctime_nsec())}
impl Guard{
 fn open(path:&Path)->R<Self>{
  let mut chain=vec![Node{name:String::new(),fd:File::open("/").map_err(|_|err("readonly_path_rejected"))?}];
  let parts=path.components().collect::<Vec<_>>();if parts.first()!=Some(&std::path::Component::RootDir){return Err(err("readonly_path_rejected"));}
  for part in &parts[1..parts.len()-1]{let std::path::Component::Normal(n)=part else{return Err(err("readonly_path_rejected"));};let n=n.to_str().ok_or_else(||err("readonly_path_rejected"))?;let c=CString::new(n).map_err(|_|err("readonly_path_rejected"))?;
   let fd=unsafe{libc::openat(chain.last().unwrap().fd.as_raw_fd(),c.as_ptr(),libc::O_RDONLY|libc::O_DIRECTORY|libc::O_NOFOLLOW|libc::O_CLOEXEC)};if fd<0{return Err(err("readonly_path_rejected"));}chain.push(Node{name:n.into(),fd:unsafe{File::from_raw_fd(fd)}});
  }
  let name=path.file_name().and_then(|s|s.to_str()).ok_or_else(||err("readonly_path_rejected"))?.to_string();let c=CString::new(name.clone()).unwrap();let fd=unsafe{libc::openat(chain.last().unwrap().fd.as_raw_fd(),c.as_ptr(),libc::O_RDONLY|libc::O_NOFOLLOW|libc::O_CLOEXEC|libc::O_NONBLOCK)};
  if fd<0{return Err(err("readonly_database_unavailable"));}let file=unsafe{File::from_raw_fd(fd)};let m=file.metadata().map_err(|_|err("readonly_path_rejected"))?;
  let g=Self{chain,file,name,stamp:stamp(&m)};g.validate()?;Ok(g)
 }
 fn validate(&self)->R<()>{
  for i in 1..self.chain.len(){let node=&self.chain[i];let m=node.fd.metadata().map_err(|_|err("readonly_path_rejected"))?;let n=CString::new(node.name.clone()).unwrap();let mut st:libc::stat=unsafe{std::mem::zeroed()};
   if unsafe{libc::fstatat(self.chain[i-1].fd.as_raw_fd(),n.as_ptr(),&mut st,libc::AT_SYMLINK_NOFOLLOW)}!=0||st.st_ino!=m.ino()||st.st_dev as u64!=m.dev()||!m.is_dir(){return Err(err("readonly_path_rejected"));}
  }
  let dir=self.chain.last().unwrap();let dm=dir.fd.metadata().map_err(|_|err("readonly_path_rejected"))?;let m=self.file.metadata().map_err(|_|err("readonly_path_rejected"))?;
  if dm.uid()!=unsafe{libc::getuid()}||dm.mode()&0o777!=0o700||!m.is_file()||m.uid()!=unsafe{libc::getuid()}||m.mode()&0o777!=0o600||m.nlink()!=1{return Err(err("readonly_permissions_rejected"));}
  let mut st:libc::stat=unsafe{std::mem::zeroed()};let n=CString::new(self.name.clone()).unwrap();
  if unsafe{libc::fstatat(dir.fd.as_raw_fd(),n.as_ptr(),&mut st,libc::AT_SYMLINK_NOFOLLOW)}!=0||st.st_ino!=m.ino()||st.st_dev as u64!=m.dev()||st.st_mode as u32&libc::S_IFMT as u32!=libc::S_IFREG as u32||stamp(&m)!=self.stamp{return Err(err("readonly_database_changed"));}
  for suffix in ["-wal","-shm","-journal"]{let n=CString::new(format!("{}{suffix}",self.name)).unwrap();let mut st:libc::stat=unsafe{std::mem::zeroed()};let rc=unsafe{libc::fstatat(dir.fd.as_raw_fd(),n.as_ptr(),&mut st,libc::AT_SYMLINK_NOFOLLOW)};if rc==0{return Err(err("readonly_sidecar_required"));}if std::io::Error::last_os_error().kind()!=std::io::ErrorKind::NotFound{return Err(err("readonly_path_rejected"));}}
  Ok(())
 }
}
#[derive(Deserialize)]#[serde(deny_unknown_fields)]struct Request{version:u8,operation:String,payload:Query}
#[derive(Deserialize)]#[serde(rename_all="camelCase",deny_unknown_fields)]pub struct Query{metric:String,days:i64,end_day:Option<i64>,source:Option<String>,offset:Option<i64>,#[serde(default)]group_page:u32}
impl Query{fn check(&self)->R<()>{if !["sleep","steps","exercise"].contains(&self.metric.as_str())||![7,30,90].contains(&self.days)||self.end_day.is_some_and(|d|!(0..=47481).contains(&d))||self.group_page>1000||self.source.is_some()!=self.offset.is_some()||self.source.as_ref().is_some_and(|s|s.is_empty()||s.len()>640||s.chars().any(char::is_control))||self.offset.is_some_and(|o|!(-840..=840).contains(&o)){return Err(err("readonly_request_rejected"));}Ok(())}}
pub struct Reader{guard:Guard,c:Connection}
impl Reader{
 pub(crate) fn recent(&self,metric:&str,end:Option<i64>)->R<Value>{self.query(Query{metric:metric.into(),days:7,end_day:end,source:None,offset:None,group_page:0})}

 pub fn open(path:&Path)->R<Self>{let guard=Guard::open(path)?;let mut f=guard.file.try_clone().map_err(|_|err("readonly_path_rejected"))?;let mut header=[0u8;100];f.read_exact(&mut header).map_err(|_|err("readonly_database_unavailable"))?;if &header[..16]!=b"SQLite format 3\0"||header[18]!=1||header[19]!=1{return Err(err("readonly_sidecar_required"));}
  let c=Connection::open_with_flags(path,OpenFlags::SQLITE_OPEN_READ_ONLY|OpenFlags::SQLITE_OPEN_NO_MUTEX|OpenFlags::SQLITE_OPEN_NOFOLLOW)?;c.pragma_update(None,"query_only",true)?;c.busy_timeout(Duration::from_millis(150))?;
  let _:i64=c.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('records','sources','states')",[],|r|r.get(0)).and_then(|n|if n==3{Ok(n)}else{Err(rusqlite::Error::InvalidQuery)})?;guard.validate()?;let reader=Self{guard,c};reader.query(Query{metric:"steps".into(),days:7,end_day:None,source:None,offset:None,group_page:0})?;Ok(reader)
 }
 pub(crate) fn parse_body(body:tauri::ipc::InvokeBody)->R<Query>{let tauri::ipc::InvokeBody::Raw(b)=body else{return Err(err("readonly_raw_required"));};if b.len()>4096{return Err(err("readonly_request_rejected"));}let raw=std::str::from_utf8(&b).map_err(|_|err("readonly_request_rejected"))?;let r:Request=serde_json::from_value(crate::strict_json::parse(raw)?).map_err(|_|err("readonly_request_rejected"))?;if r.version!=2||r.operation!="health_view"{return Err(err("readonly_request_rejected"));}r.payload.check()?;Ok(r.payload)}
 pub fn dispatch(&self,body:tauri::ipc::InvokeBody)->R<Value>{self.query(Self::parse_body(body)?)}
 pub(crate) fn validated_query(&self,q:Query)->R<Value>{self.query(q)}
 fn query(&self,q:Query)->R<Value>{q.check()?;self.guard.validate()?;let started=Instant::now();self.c.progress_handler(1000,Some(move||started.elapsed()>Duration::from_secs(3)))?;
  let result=self.run_query(q);self.c.progress_handler(0,None::<fn()->bool>)?;self.guard.validate()?;let v=result?;if serde_json::to_vec(&v).map_err(|_|err("readonly_response_limit"))?.len()>131072{return Err(err("readonly_response_limit"));}Ok(v)
 }
 fn run_query(&self,q:Query)->R<Value>{
  let sql="SELECT json_extract(body,'$.sources[0].name') AS src,CAST(json_extract(body,'$.offsetMinutes') AS INTEGER) AS off,MAX(CAST(json_extract(body,'$.dayIndex') AS INTEGER)) AS last FROM states WHERE json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_current_state' AND json_extract(body,'$.metric')=?1 GROUP BY src,off";
  let mut stmt=self.c.prepare(&(sql.to_owned()+" ORDER BY src COLLATE BINARY,off LIMIT 33 OFFSET ?2"))?;let mut groups=stmt.query_map(params![q.metric,q.group_page as i64*32],|r|Ok(json!({"source":r.get::<_,String>(0)?,"offset":r.get::<_,i64>(1)?,"latestDay":r.get::<_,i64>(2)?})))?.collect::<Result<Vec<_>,_>>()?;let more=groups.len()>32;groups.truncate(32);
  let chosen=if let (Some(s),Some(o))=(q.source.as_ref(),q.offset){Some((s.clone(),o))}else{self.c.query_row(&(sql.to_owned()+" ORDER BY last DESC,src COLLATE BINARY,off LIMIT 1"),[&q.metric],|r|Ok((r.get::<_,String>(0)?,r.get::<_,i64>(1)?))).optional()?};
  let imported:Option<i64>=self.c.query_row("SELECT MAX(CAST(json_extract(body,'$.receivedAt') AS INTEGER)) FROM records WHERE id>='health-apple-batch:' AND id<'health-apple-batch;' AND json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_batch'",[],|r|r.get(0))?;
  let Some((source,offset))=chosen else{return Ok(json!({"metric":q.metric,"days":q.days,"groups":groups,"groupPage":q.group_page,"nextGroupPage":if more{Some(q.group_page+1)}else{None},"points":[],"latestDay":null,"importedAt":imported}));};
  let filter=" FROM states WHERE json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_current_state' AND json_extract(body,'$.metric')=?1 AND json_extract(body,'$.sources[0].name')=?2 AND CAST(json_extract(body,'$.offsetMinutes') AS INTEGER)=?3";
  let latest:Option<i64>=self.c.query_row(&("SELECT MAX(CAST(json_extract(body,'$.dayIndex') AS INTEGER))".to_owned()+filter),params![q.metric,source,offset],|r|r.get(0))?;
  let end=q.end_day.or(latest);let mut points=Vec::new();let mut observed=None;let mut received=None;
  if let Some(end)=end{let start=(end-q.days+1).max(0);let sql="SELECT CAST(json_extract(body,'$.dayIndex') AS INTEGER),json_extract(body,'$.value'),json_extract(body,'$.estimated'),json_extract(body,'$.method'),json_extract(body,'$.observedAt'),json_extract(body,'$.receivedAt')".to_owned()+filter+" AND CAST(json_extract(body,'$.dayIndex') AS INTEGER) BETWEEN ?4 AND ?5 ORDER BY CAST(json_extract(body,'$.dayIndex') AS INTEGER),id LIMIT 91";let mut stmt=self.c.prepare(&sql)?;
   let rows=stmt.query_map(params![q.metric,source,offset,start,end],|r|Ok((r.get::<_,i64>(0)?,r.get::<_,Option<f64>>(1)?,r.get::<_,Option<bool>>(2)?.unwrap_or(false),r.get::<_,Option<String>>(3)?,r.get::<_,Option<i64>>(4)?,r.get::<_,Option<i64>>(5)?)))?.collect::<Result<Vec<_>,_>>()?;
   if rows.len()>90{return Err(err("readonly_projection_ambiguous"));}let mut map=std::collections::BTreeMap::new();for (day,value,estimated,method,at,recv) in rows{if map.insert(day,json!({"day":day,"present":true,"value":value,"estimated":estimated,"method":method})).is_some(){return Err(err("readonly_projection_ambiguous"));}observed=observed.max(at);received=received.max(recv);}
   for day in start..=end{points.push(map.remove(&day).unwrap_or(json!({"day":day,"present":false,"value":null,"estimated":false})));}
  }
  Ok(json!({"metric":q.metric,"days":q.days,"source":source,"offset":offset,"endDay":end,"latestDay":latest,"observedAt":observed,"receivedAt":received,"importedAt":imported,"groups":groups,"groupPage":q.group_page,"nextGroupPage":if more{Some(q.group_page+1)}else{None},"points":points}))
 }
}


#[cfg(test)]mod aux_tests;
