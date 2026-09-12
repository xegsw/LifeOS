use super::*;
use sha2::{Digest,Sha256};
fn hash(b:&[u8])->String{format!("{:x}",Sha256::digest(b))}
impl Store{
 pub(crate) fn invalidate_notes(&self)->R<()>{let mut q=self.c.prepare("SELECT id FROM records WHERE json_extract(body,'$.engineRef') IS NOT NULL")?;let ids=q.query_map([],|r|r.get::<_,String>(0))?.collect::<Result<Vec<_>,_>>()?;drop(q);for key in ids{Self::invalidate(&self.c,&key)?;self.c.execute("UPDATE records SET body=json_set(body,'$.status','stale') WHERE id=?1",[key])?;}Ok(())}
 pub(crate) fn refresh_notes(&self,question:&str)->R<()>{
  let purpose=domain(&self.c,question)?;if purpose=="health"{return Ok(())}
  let rows=lifeos_source_engine::context(&self.fixture(),&question.chars().take(300).collect::<String>()).map_err(|e|error(&e.code))?;
  let purpose=if purpose=="ambiguous"{"source"}else{purpose.as_str()};
  let existing={let mut q=self.c.prepare("SELECT body FROM records WHERE json_extract(body,'$.engineRef') IS NOT NULL AND json_extract(body,'$.status')='active' LIMIT 129")?;let rows=q.query_map([],|r|r.get::<_,String>(0))?.collect::<Result<Vec<_>,_>>()?;rows};
  if existing.len()>128{return Err(error("source_budget_rejected"))}
  let mut keys=vec![];
  for r in rows{
   let reference=&r["engineRef"];let key=format!("note-source-{}",&hash(r["id"].as_str().unwrap().as_bytes())[..32]);keys.push(key.clone());
   let source=format!("note-{}",&hash(reference["connectorId"].as_str().unwrap().as_bytes())[..24]);
   put(&self.c,"sources",&source,&json!({"id":source,"authorized":true,"generation":reference["authorizationGeneration"],"synthetic":!crate::runtime_root::is_real()}))?;
   let old=get(&self.c,"records",&key)?;let version=old.as_ref().and_then(|v|v["version"].as_u64()).unwrap_or(1);
   let mut record=json!({"id":key,"kind":"source_projection","sourceId":source,"domain":purpose,"version":version,"status":"active","text":r["text"],"observedAt":r["observedAt"],"estimated":false,"engineRef":reference,"bridgeQuestion":question.to_lowercase()});
   if old.as_ref().is_some_and(|o|o!=&record){record["version"]=json!(version+1);Self::invalidate(&self.c,&key)?;}
   put(&self.c,"records",&key,&record)?;
  }
  for raw in existing{let r:Value=serde_json::from_str(&raw).map_err(|_|error("source_contract_rejected"))?;let key=r["id"].as_str().unwrap();if !keys.iter().any(|k|k==key){Self::invalidate(&self.c,key)?;self.c.execute("UPDATE records SET body=json_set(body,'$.status','stale') WHERE id=?1",[key])?;}}
  Ok(())
 }
}
