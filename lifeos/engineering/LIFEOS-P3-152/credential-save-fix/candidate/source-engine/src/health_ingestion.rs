//! Internal application port and SQLite/source adapters, synthetic profile only.
use crate::{health_domain::{self as domain, Envelope, Observation}, repository::{self, Error}};
use rusqlite::{Connection, params, TransactionBehavior};
use serde_json::{json, Value};
use sha2::{Digest,Sha256};
use std::collections::{BTreeMap,BTreeSet};
type R<T>=Result<T,Error>;
pub trait HealthRepository { fn receive(&mut self, e:&Envelope, received_at:i64)->R<Value>; }
pub struct SqliteHealth<'a>(pub &'a mut Connection);
pub(crate) fn rows(c:&Connection,table:&str,kind:&str)->R<Vec<Value>> {
 let mut q=c.prepare(&format!("SELECT body FROM {table} WHERE json_extract(body,'$.kind')=? ORDER BY id"))?;
 let raw=q.query_map([kind],|r|r.get::<_,String>(0))?.collect::<Result<Vec<_>,_>>()?;
 raw.into_iter().map(|s|serde_json::from_str(&s).map_err(|_|Error::new("health_store_corrupt"))).collect()
}
pub(crate) fn put(c:&Connection,table:&str,v:&Value)->R<()> { c.execute(&format!("INSERT INTO {table}(id,body) VALUES(?1,?2) ON CONFLICT(id) DO UPDATE SET body=excluded.body"),params![v["id"].as_str().ok_or_else(||Error::new("health_store_corrupt"))?,v.to_string()])?;Ok(()) }
impl HealthRepository for SqliteHealth<'_> {
 fn receive(&mut self,e:&Envelope, received_at:i64)->R<Value> {
  let hash=format!("{:x}",Sha256::digest(serde_json::to_vec(e).map_err(|_|Error::new("health_envelope_rejected"))?));
  let batch=format!("health-batch:{}:{}",e.source.id,e.batch_id);
  let tx=self.0.transaction_with_behavior(TransactionBehavior::Immediate)?;
  if rows(&tx,"states","health_current_state")?.iter().any(|s|s["protocol"]=="apple-file-v1"){return Err(Error::new("health_protocol_overlap"));}
  for b in rows(&tx,"records","health_batch")? {if b["id"]==batch {return if b["contentHash"]==hash {Ok(json!({"state":"duplicate","changed":0}))}else{Err(Error::new("health_batch_conflict"))};}}
  let mut history:BTreeMap<String,Observation>=BTreeMap::new();
  let mut current:BTreeMap<String,Observation>=BTreeMap::new();
  for r in rows(&tx,"records","health_sample")? {
   let o:Observation=serde_json::from_value(r["observation"].clone()).map_err(|_|Error::new("health_store_corrupt"))?;
   if current.get(&o.identity()).is_none_or(|old|old.sample.revision<o.sample.revision){current.insert(o.identity(),o.clone());}
   history.insert(o.record_id(),o);
  }
  let before=current.clone(); let mut inserted=0;
  for o in domain::observations(e,received_at) {
   if let Some(old)=history.get(&o.record_id()) {if !old.same_content(&o){return Err(Error::new("health_version_conflict"));}continue;}
   put(&tx,"records",&json!({"id":o.record_id(),"kind":"health_sample","status":"observed","domain":"Health","modelEligible":false,"sourceId":format!("health-source:{}",o.source.id),"externalId":o.sample.sample_id,"version":o.sample.revision,"observation":o}))?;
   inserted+=1;
   if current.get(&o.identity()).is_none_or(|old|old.sample.revision<o.sample.revision) {current.insert(o.identity(),o.clone());}
   history.insert(o.record_id(),o);
  }
  let mut affected=BTreeSet::new();
  for (id,new) in &current {if before.get(id).is_none_or(|old|old.sample.revision!=new.sample.revision){affected.extend(new.keys());if let Some(old)=before.get(id){affected.extend(old.keys());}}}
  crate::health_snapshot::reject_v1_mixing(&tx,&affected)?;
  let all:Vec<_>=current.into_values().collect();
  for k in &affected {put(&tx,"states",&domain::project(k,&all))?;}
  put(&tx,"sources",&json!({"id":format!("health-source:{}",e.source.id),"kind":"health_source","name":e.source.name,"externalSourceId":e.source.id,"authorized":false,"ingestAuthorized":true,"generation":1,"modelEligible":false,"receivedAt":received_at,"observedAt":all.iter().filter(|o|o.source.id==e.source.id).map(|o|o.sample.end_ms).max()}))?;
  put(&tx,"records",&json!({"id":batch,"kind":"health_batch","status":"observed","modelEligible":false,"contentHash":hash,"batchId":e.batch_id,"receivedAt":received_at,"samples":e.samples.len(),"inserted":inserted,"changedStates":affected.len()}))?;
  tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1",[])?;
  tx.commit()?;Ok(json!({"state":"received","inserted":inserted,"changed":affected.len()}))
 }
}
pub fn ingest(port:&mut impl HealthRepository, bytes:&[u8], received_at:i64)->R<Value> {let e=domain::parse(bytes)?;port.receive(&e,received_at)}
fn now()->i64 {std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_millis() as i64}
fn read_file(dir:&crate::artifact_io::Dir,name:&str)->R<Vec<u8>> {
 let mut f=dir.open(name)?;
 let meta=f.descriptor()?.metadata().map_err(|_|Error::new("health_file_rejected"))?;
 if std::os::unix::fs::MetadataExt::nlink(&meta)!=1 {return Err(Error::new("health_file_rejected"));}
 let bytes=f.read_limit(domain::LIMIT as u64)?;f.validate()?;Ok(bytes)
}
/// Kept only in this process; failures are visible without writing invalid batch data.
pub fn scan(fixture:&str)->R<Value> {
 if crate::runtime_root::is_real(){return Err(Error::new("health_synthetic_only"));}
 let inbox=crate::artifact_io::Dir::root()?.child("inbox",true)?;
 let mut names=inbox.entries()?;names.sort();
 // Explicit rejection instead of a silently incomplete or starving scan.
 if names.len()>64 {return Err(Error::new("health_inbox_limit"));}
 let mut c=repository::open(fixture)?;c.busy_timeout(std::time::Duration::from_secs(2))?;
 let mut results=vec![];
 for name in names {
  if !name.ends_with(".json"){continue;}
  let result=read_file(&inbox,&name).and_then(|bytes|receive_bytes(&mut c,&bytes,now()));
  results.push(match result {Ok(value)=>json!({"file":name,"result":value}),Err(error)=>json!({"file":name,"error":error.code})});
 }
 Ok(json!({"kind":"health_receiver","mode":"synthetic","files":results}))
}
static STATUS: std::sync::OnceLock<std::sync::Mutex<Value>>=std::sync::OnceLock::new();
pub fn status()->Value {let mut v=STATUS.get_or_init(||std::sync::Mutex::new(json!({"mode":"synthetic","files":[]}))).lock().unwrap().clone(); v["id"]=json!("health-inbox");v["kind"]=json!("health_source");v["authorized"]=json!(false);v["modelEligible"]=json!(false);v}
pub fn start() {std::thread::spawn(||loop {let s=match scan("app"){Ok(v)=>v,Err(e)=>json!({"mode":"synthetic","error":e.code})};*STATUS.get_or_init(||std::sync::Mutex::new(Value::Null)).lock().unwrap()=s;std::thread::sleep(std::time::Duration::from_secs(3));});}
#[cfg(test)]
mod tests;

pub fn receive_bytes(c:&mut Connection,bytes:&[u8],at:i64)->R<Value>{if bytes.len()>domain::LIMIT{return Err(Error::new("health_batch_limit"));}let v=crate::strict_json::parse(std::str::from_utf8(bytes).map_err(|_|Error::new("health_envelope_rejected"))?)?;if v["schema"]=="health-window-snapshot-v1"{crate::health_snapshot::receive(c,bytes,at)}else{ingest(&mut SqliteHealth(c),bytes,at)}}
