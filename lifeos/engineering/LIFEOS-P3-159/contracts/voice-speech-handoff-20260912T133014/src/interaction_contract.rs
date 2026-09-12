//! Mirror of PM LIFEOS-INTERACTION-V1; not a model or execution protocol.
use serde::{Serialize,Deserialize};
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(deny_unknown_fields)] pub struct Ref {pub id:String,pub revision:u64}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(tag="kind",rename_all="snake_case",deny_unknown_fields)]
pub enum Origin {Keyboard,Voice {#[serde(rename="sessionId")]session_id:String,#[serde(rename="segmentId")]segment_id:String,#[serde(rename="asrRequestId")]asr_request_id:String,language:String}}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(rename_all="camelCase",deny_unknown_fields)]
pub struct UserTurn {
 #[serde(deserialize_with="schema")]pub schema_version:String,pub turn_id:String,pub conversation_ref:Ref,pub text:String,pub origin:Origin,pub finalized_at:String,
 #[serde(default,skip_serializing_if="Option::is_none")]pub reply_to:Option<Ref>,
 #[serde(default,skip_serializing_if="Option::is_none")]pub presented_proactive_ref:Option<Ref>,
 #[serde(default,skip_serializing_if="Option::is_none")]pub interrupted_speech_request_id:Option<String>
}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(tag="kind",rename_all="snake_case",deny_unknown_fields)]
pub enum AssistantContent {
 Response{text:String},Question{text:String},
 Suggestion{text:String,#[serde(rename="whyNow")]why_now:String,#[serde(rename="evidenceRefs")]evidence_refs:Vec<Ref>,#[serde(rename="inferenceFlags")]inference_flags:Vec<String>},
 Receipt{text:String,#[serde(rename="receiptRef")]receipt_ref:Ref},Error{text:String,code:String}
}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(rename_all="camelCase",deny_unknown_fields)]
pub struct AssistantTurn {
 #[serde(deserialize_with="schema")]pub schema_version:String,pub turn_ref:Ref,pub conversation_ref:Ref,
 #[serde(default,skip_serializing_if="Option::is_none")]pub in_reply_to_turn_id:Option<String>,#[serde(deserialize_with="assistant_origin")]pub origin:String,
 #[serde(default,skip_serializing_if="Option::is_none")]pub proactive_ref:Option<Ref>,pub content:AssistantContent,pub finalized_at:String
}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(rename_all="camelCase",deny_unknown_fields)]
pub struct SpeechOutputRequest {
 #[serde(deserialize_with="schema")]pub schema_version:String,pub request_id:String,pub session_id:String,pub session_generation:u64,pub assistant_turn_ref:Ref,
 #[serde(default,skip_serializing_if="Option::is_none")]pub proactive_decision_ref:Option<Ref>,pub projection_ref:Ref,pub policy_revision:u64,#[serde(deserialize_with="voice")]pub voice:String,#[serde(deserialize_with="speech_language")]pub language:String
}
#[derive(Debug,Clone,PartialEq,Serialize,Deserialize)]
#[serde(rename_all="snake_case")]pub enum InterruptionReason {UserSpeech,UserStop,Disabled,DeviceLost,SessionClosed,OutputInvalidated}
#[derive(Debug,Clone,Serialize,Deserialize)]
#[serde(rename_all="camelCase",deny_unknown_fields)]
pub struct SpeechInterrupted {
 #[serde(deserialize_with="schema")]pub schema_version:String,pub event_id:String,pub session_id:String,pub session_generation:u64,pub speech_request_id:String,pub assistant_turn_ref:Ref,pub reason:InterruptionReason,pub occurred_at:String,
 #[serde(default,skip_serializing_if="Option::is_none")]pub played_milliseconds:Option<u64>
}

fn one_of<'de,D:serde::Deserializer<'de>>(d:D,allowed:&[&str])->Result<String,D::Error>{let s=String::deserialize(d)?;if allowed.contains(&s.as_str()){Ok(s)}else{Err(serde::de::Error::custom("interaction literal rejected"))}}
fn schema<'de,D:serde::Deserializer<'de>>(d:D)->Result<String,D::Error>{one_of(d,&["interaction-v1"])}
fn assistant_origin<'de,D:serde::Deserializer<'de>>(d:D)->Result<String,D::Error>{one_of(d,&["conversation","proactive","transaction"])}
fn voice<'de,D:serde::Deserializer<'de>>(d:D)->Result<String,D::Error>{one_of(d,&["mimo_default"])}
fn speech_language<'de,D:serde::Deserializer<'de>>(d:D)->Result<String,D::Error>{one_of(d,&["zh-CN"])}
#[derive(Debug,Clone,Serialize,Deserialize)]
#[serde(rename_all="camelCase",deny_unknown_fields)]pub struct ProactiveCandidate<E>{#[serde(deserialize_with="schema")]pub schema_version:String,pub evaluation_id:String,pub candidate:E}
#[derive(Debug,Clone,Serialize,Deserialize)]
#[serde(tag="kind",rename_all="snake_case",deny_unknown_fields)]pub enum ProactiveDecision{
 Silence{#[serde(rename="schemaVersion",deserialize_with="schema")]schema_version:String,#[serde(rename="decisionRef")]decision_ref:Ref,#[serde(rename="reasonCode")]reason_code:String},
 Surface{#[serde(rename="schemaVersion",deserialize_with="schema")]schema_version:String,#[serde(rename="decisionRef")]decision_ref:Ref,#[serde(rename="proactiveRef")]proactive_ref:Ref,#[serde(rename="assistantTurn")]assistant_turn:AssistantTurn}
}
#[derive(Debug,Clone,Serialize,Deserialize)]
#[serde(tag="status",rename_all="snake_case",deny_unknown_fields)]pub enum UserTurnReceipt{
 Accepted{#[serde(rename="turnId")]turn_id:String,#[serde(rename="recordRef")]record_ref:Ref},
 Duplicate{#[serde(rename="turnId")]turn_id:String,#[serde(rename="recordRef")]record_ref:Ref},
 PendingAuthorization{#[serde(rename="turnId")]turn_id:String,code:String},
 Rejected{#[serde(rename="turnId")]turn_id:String,code:String},
 Unknown{#[serde(rename="turnId")]turn_id:String,code:String}
}
#[cfg(test)]mod tests{
 use super::*;use serde_json::{Value,json};
 fn round<T:serde::de::DeserializeOwned+Serialize>(v:&Value){let t:T=serde_json::from_value(v.clone()).unwrap();assert_eq!(serde_json::to_value(t).unwrap(),*v);}
 #[test]fn interaction_public_union_wire_fixtures_roundtrip(){let fixture:Value=serde_json::from_str(include_str!("../../tests/interaction_v1_fixtures.json")).unwrap();for v in fixture["users"].as_array().unwrap(){round::<UserTurn>(v)}for v in fixture["assistants"].as_array().unwrap(){round::<AssistantTurn>(v)}for v in fixture["receipts"].as_array().unwrap(){round::<UserTurnReceipt>(v)}for v in fixture["decisions"].as_array().unwrap(){round::<ProactiveDecision>(v)}round::<SpeechOutputRequest>(&fixture["speech"]);round::<SpeechInterrupted>(&fixture["interrupted"]);round::<ProactiveCandidate<crate::proactive_contract::Evaluation>>(&fixture["candidate"]);}
 #[test]fn interaction_closed_literals_and_authority_fields_rejected(){let fixture:Value=serde_json::from_str(include_str!("../../tests/interaction_v1_fixtures.json")).unwrap();let mut a=fixture["assistants"][0].clone();a["origin"]=json!("model_candidate");assert!(serde_json::from_value::<AssistantTurn>(a).is_err());for field in ["voice","language","schemaVersion"]{let mut s=fixture["speech"].clone();s[field]=json!("forged");assert!(serde_json::from_value::<SpeechOutputRequest>(s).is_err());}let mut r=fixture["receipts"][0].clone();r["authorized"]=json!(true);assert!(serde_json::from_value::<UserTurnReceipt>(r).is_err());}
}
