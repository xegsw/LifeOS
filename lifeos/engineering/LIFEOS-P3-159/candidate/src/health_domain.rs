//! Pure bounded synthetic health contract and deterministic projection. No I/O.
use crate::repository::Error;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
pub const LIMIT: usize = 128 * 1024;
pub const DAY: i64 = 86_400_000;
type R<T> = Result<T, Error>;
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Source { pub id: String, pub name: String }
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Sample { pub sample_id: String, pub revision: u32, pub metric: String, pub start_ms: i64, pub end_ms: i64, pub value: f64, pub unit: String }
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Envelope { pub schema: String, pub batch_id: String, pub exported_at_ms: i64, pub window_start_ms: i64, pub window_end_ms: i64, pub timezone_offset_minutes: i32, pub source: Source, pub samples: Vec<Sample> }
#[derive(Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct Observation { pub source: Source, pub sample: Sample, pub offset: i32, pub received_at: i64 }
impl Observation {
 pub fn identity(&self) -> String { format!("{}:{}", self.source.id, self.sample.sample_id) }
 pub fn record_id(&self) -> String { format!("health:{}:{}", self.identity(), self.sample.revision) }
 pub fn same_content(&self, other: &Self) -> bool { self.source == other.source && self.sample == other.sample && self.offset == other.offset }
 pub fn keys(&self) -> BTreeSet<Key> { let shift = self.offset as i64 * 60000; ((self.sample.start_ms+shift).div_euclid(DAY)..=(self.sample.end_ms-1+shift).div_euclid(DAY)).map(|day| Key{day,offset:self.offset,metric:self.sample.metric.clone()}).collect() }
}
#[derive(Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct Key { pub day: i64, pub offset: i32, pub metric: String }
impl Key { pub fn id(&self)->String {format!("health:{}:{}:{}",self.metric,self.day,self.offset)} }
fn bad()->Error {Error::new("health_envelope_rejected")}
fn ident(s:&str)->bool {!s.is_empty() && s.len()<=80 && s.bytes().all(|b|b.is_ascii_alphanumeric() || b"_-".contains(&b))}
pub fn parse(bytes:&[u8])->R<Envelope> {
 if bytes.len()>LIMIT {return Err(Error::new("health_batch_limit"));}
 let raw = crate::strict_json::parse(std::str::from_utf8(bytes).map_err(|_|bad())?).map_err(|_|bad())?;
 let e:Envelope=serde_json::from_value(raw).map_err(|_|bad())?;
 let time=|t| (1_577_836_800_000..4_102_444_800_000i64).contains(&t);
 if e.schema!="health-envelope-v1" || !ident(&e.batch_id) || !ident(&e.source.id) || e.source.name.trim().is_empty() || e.source.name.chars().count()>80 || e.source.name.chars().any(char::is_control) || !(-840..=840).contains(&e.timezone_offset_minutes) || !time(e.window_start_ms) || !time(e.window_end_ms) || !time(e.exported_at_ms) || e.window_start_ms>=e.window_end_ms || e.window_end_ms-e.window_start_ms>7*DAY || e.exported_at_ms<e.window_end_ms || e.samples.len()>256 {return Err(bad());}
 let mut versions:BTreeMap<(&str,u32),&Sample>=BTreeMap::new();
 for s in &e.samples {
  if !ident(&s.sample_id) || !(1..=1_000_000).contains(&s.revision) || s.start_ms<e.window_start_ms || s.end_ms>e.window_end_ms || s.start_ms>=s.end_ms || !s.value.is_finite() || s.value<0.0 {return Err(bad());}
  let valid=match s.metric.as_str() {"sleep"=>s.unit=="milliseconds" && s.value==(s.end_ms-s.start_ms) as f64,"steps"=>s.unit=="count" && s.value.fract()==0.0 && s.value<=1_000_000.0,"exercise"=>s.unit=="minutes" && s.value<=(s.end_ms-s.start_ms) as f64/60000.0,_=>false};
  if !valid {return Err(bad());}
  if let Some(old)=versions.insert((&s.sample_id,s.revision),s) {if old!=s {return Err(Error::new("health_version_conflict"));}}
 }
 Ok(e)
}
pub fn observations(e:&Envelope,received_at:i64)->Vec<Observation> {e.samples.iter().map(|sample|Observation{source:e.source.clone(),sample:sample.clone(),offset:e.timezone_offset_minutes,received_at}).collect()}
fn union(mut spans:Vec<(i64,i64)>)->i64 {spans.sort();let mut total=0;let mut end=i64::MIN;for(a,b)in spans{total+=b-a.max(end).min(b);end=end.max(b);}total}
pub fn project(k:&Key, all:&[Observation])->Value {
 let start=k.day*DAY-k.offset as i64*60000; let end=start+DAY;
 let rows:Vec<_>=all.iter().filter(|o|o.offset==k.offset && o.sample.metric==k.metric && o.sample.start_ms<end && o.sample.end_ms>start).collect();
 let mut groups:BTreeMap<String,Vec<&Observation>>=BTreeMap::new(); for o in &rows {groups.entry(o.source.id.clone()).or_default().push(o);}
 let mut sources=vec![];let mut all_spans=vec![];let mut estimated=false;
 for (source_id, items) in groups {
  let mut spans=vec![];let mut count=0.0;let mut split=false;
  for o in &items {let s=&o.sample;let a=s.start_ms.max(start);let b=s.end_ms.min(end);spans.push((a,b));all_spans.push((a,b));count+=s.value*(b-a)as f64/(s.end_ms-s.start_ms)as f64;split|=a!=s.start_ms||b!=s.end_ms;}
  spans.sort();let overlap=spans.windows(2).any(|w|w[1].0<w[0].1);
  let value=if k.metric=="sleep" {json!(union(spans) as f64/60000.0)} else if overlap {Value::Null} else {json!(count)};
  estimated|=split && k.metric!="sleep";
  sources.push(json!({"sourceId":source_id,"name":items[0].source.name,"value":value,"uncertain":overlap && k.metric!="sleep","estimated":split && k.metric!="sleep"}));
 }
 let value=if rows.is_empty(){Value::Null}else if k.metric=="sleep"{json!(union(all_spans) as f64/60000.0)}else if sources.len()==1 {sources[0]["value"].clone()}else{Value::Null};
 json!({"id":k.id(),"kind":"health_current_state","domain":"Health","status":"observed","modelEligible":false,"sourceId":"health-projection","dayIndex":k.day,"offsetMinutes":k.offset,"metric":k.metric,"value":value,"unit":if k.metric=="steps"{"count"}else{"minutes"},"estimated":estimated,"method":if rows.is_empty(){"no_current_sample"}else if k.metric=="sleep"{"sleep_interval_union"}else if sources.len()>1{"per_source_unmerged"}else if value.is_null(){"overlap_uncertain"}else if estimated{"duration_prorated_estimate"}else{"nonoverlapping_source_samples"},"sources":sources,"refs":rows.iter().map(|o|json!({"id":o.record_id(),"sourceId":o.source.id,"sampleId":o.sample.sample_id,"version":o.sample.revision})).collect::<Vec<_>>(),"observedAt":rows.iter().map(|o|o.sample.end_ms).max(),"receivedAt":rows.iter().map(|o|o.received_at).max()})
}
