use super::*;
use crate::{conversation_contract as contract, provider_store};
const SLOT: &str = "_provider_lifecycle";

impl Store {
 fn lifecycle(&self)->R<Value>{if crate::runtime_root::is_online(){return Ok(provider_store::online_configuration()?.0)}Ok(get(&self.c,"sources",SLOT)?.unwrap_or(json!({"schemaVersion":1,"revision":0,"state":"not_tested"}))) }
 fn bound(&self,v:&Value,p:&Value,c:&Value)->bool{provider_store::effective_bound(v,p,c)}
 pub(crate) fn provider_view(&self)->R<Value>{
  let mut p=provider_store::settings(&self.fixture())?;let c=self.catalog()?;let v=self.lifecycle()?;
  if crate::runtime_root::is_online(){use sha2::{Digest,Sha256};p["configurationFingerprint"]=json!(format!("{:x}",Sha256::digest(json!({"catalog":c,"lifecycle":v}).to_string().as_bytes())));}
  Ok(provider_store::effective_view(p,&c,&v))
 }
 fn lifecycle_cas(&self,p:&Value)->R<(Value,Value,Value)>{
  let profile=provider_store::settings(&self.fixture())?;let catalog=self.catalog()?;let state=self.lifecycle()?;
  for (k,actual) in [("expectedCredentialRevision",&profile["credentialRevision"]),("expectedProfileRevision",&profile["profileRevision"]),("expectedCatalogRevision",&catalog["revision"]),("expectedSettingsRevision",&state["revision"])]{
   contract::num(p,k,0)?;if &p[k]!=actual{return Err(error("settings_revision_conflict"));}
  }
  if profile["credentialState"]!="stored"{return Err(error("credential_missing"));}
  if !catalog["settings"].is_null()&&(catalog["settings"]["primary"]["mode"]!="cloud"||catalog["settings"]["primary"]["providerId"]!="deepseek"||catalog["settings"]["primary"]["endpointUrl"]!="https://api.deepseek.com"){return Err(error("provider_not_enabled"));}
  Ok((profile,catalog,state))
 }
 pub(crate) fn lifecycle_action(&self,op:&str,p:Value)->R<Value>{
  if crate::runtime_root::is_online(){return Err(error("online_configuration_readonly"))}
  let mut fields=vec!["requestId","expectedCredentialRevision","expectedProfileRevision","expectedCatalogRevision","expectedSettingsRevision"];
  match op {"test_models"=>(),"select_model"=>fields.extend(["testReceiptId","modelId"]),"set_enabled"=>fields.extend(["testReceiptId","enabled"]),_=>return Err(error("operation_rejected"))}
  contract::fields(&p,&fields,&[])?;let rid=contract::id(&p,"requestId")?;
  for k in ["expectedCredentialRevision","expectedProfileRevision","expectedCatalogRevision","expectedSettingsRevision"]{contract::num(&p,k,0)?;}
  if op!="test_models"{contract::id(&p,"testReceiptId")?;}
  if op=="set_enabled"&&!p["enabled"].is_boolean(){return Err(error("dto_rejected"));}
  if op=="select_model"&&p["modelId"].as_str().is_none_or(|s|s.is_empty()||s.len()>128){return Err(error("model_rejected"));}
  if op=="test_models"{
   let mut fresh=false;
   self.tx(&rid,op,&p,|c|{let(profile,catalog,prior)=self.lifecycle_cas(&p)?;
    let v=json!({"id":SLOT,"kind":"private_provider_lifecycle","authorized":false,"schemaVersion":1,"revision":prior["revision"].as_u64().unwrap_or(0)+1,"state":"outcome_unknown","testReceiptId":rid,"transport":"deepseek-models-v1","recipient":"https://api.deepseek.com/models","method":"GET","requestContainsContext":false,"credentialRevision":profile["credentialRevision"],"profileRevision":profile["profileRevision"],"catalogRevision":catalog["revision"],"models":[],"selectedModel":null,"enabled":false});
    put(c,"sources",SLOT,&v)?;fresh=true;Ok(json!({"state":"outcome_unknown"}))
   })?;
   if !fresh{return Ok(json!({"state":self.provider_view()?["connectionState"],"replay":true}));}
   // Pending state is durable before key access or network. There is no retry on replay/restart.
   let result=provider_store::credential(&self.fixture()).and_then(|key|{
    fetch_models(&key)
   });
   let mut state=self.lifecycle()?;
   match result {Ok(models)=>{state["models"]=json!(models);state["state"]=json!("succeeded");},Err(e)=>{
    let code=match e.code.as_str(){"provider_authentication"|"provider_timeout"|"provider_network"|"provider_protocol"|"response_too_large"|"dispatch_outcome_unknown"|"credential_missing"|"credential_unavailable"|"credential_authentication_failed"=>e.code,_=>"provider_unavailable".into()};
    state["state"]=json!(if matches!(code.as_str(),"provider_timeout"|"provider_network"|"dispatch_outcome_unknown"){"outcome_unknown"}else{"failed"});state["errorCode"]=json!(code);
   }}
   self.c.execute_batch("BEGIN IMMEDIATE")?;let saved=(||{put(&self.c,"sources",SLOT,&state)?;let out=json!({"state":state["state"],"testReceiptId":rid});self.c.execute("UPDATE requests SET result=?1 WHERE id=?2",params![out.to_string(),rid])?;self.c.execute("UPDATE meta SET revision=revision+1 WHERE id=1",[])?;Ok(out)})();
   return match saved{Ok(v)=>{self.c.execute_batch("COMMIT")?;Ok(v)},Err(e)=>{let _=self.c.execute_batch("ROLLBACK");Err(e)}};
  }
  self.tx(&rid,op,&p,|c|{let(profile,catalog,mut v)=self.lifecycle_cas(&p)?;
   if !self.bound(&v,&profile,&catalog)||v["state"]!="succeeded"||v["testReceiptId"]!=p["testReceiptId"]{return Err(error("model_not_tested"));}
   if op=="select_model"{
    if !v["models"].as_array().is_some_and(|ms|ms.contains(&p["modelId"])){return Err(error("model_not_tested"));}
    if v["selectedModel"].as_str().is_some_and(|m|json!(m)!=p["modelId"]){v["state"]=json!("not_tested");v["enabled"]=json!(false);v["models"]=json!([]);v["selectedModel"]=Value::Null;v["revision"]=json!(v["revision"].as_u64().unwrap_or(0)+1);put(c,"sources",SLOT,&v)?;return Ok(json!({"state":"retest_required"}));}
    v["selectedModel"]=p["modelId"].clone();v["enabled"]=json!(false);
   }else{if v["selectedModel"].is_null(){return Err(error("model_selection_required"));}v["enabled"]=p["enabled"].clone();}
   v["revision"]=json!(v["revision"].as_u64().unwrap_or(0)+1);put(c,"sources",SLOT,&v)?;Ok(json!({"state":"saved"}))
  })
 }
}

fn fetch_models(key:&[u8])->R<Vec<String>>{
 #[cfg(test)] {TEST_CALLS.with(|c|c.set(c.get()+1));if let Some(result)=TEST_RESULT.with(|c|c.borrow_mut().take()){return result;}}
 if crate::runtime_root::is_real(){crate::provider_transport::models(key)}else{Ok(vec!["user-synthetic-model".into(),"user-chosen-synthetic".into(),"fictional-model-b".into()])}
}
#[cfg(test)]thread_local!{static TEST_CALLS:std::cell::Cell<usize>=const{std::cell::Cell::new(0)};static TEST_RESULT:std::cell::RefCell<Option<R<Vec<String>>>>=const{std::cell::RefCell::new(None)};}

#[cfg(test)]mod tests{
 use super::*;
 pub(super) fn store()->Store{verify_root().unwrap();let mut s=Store::open(&PathBuf::from(ROOT).join(format!("synthetic/{}.sqlite",crate::conversation_store::uid("settings")))).unwrap();s.connect_source().unwrap();s.controlled("save_ai_provider_settings","save_credential",json!({"requestId":"key","expectedCredentialRevision":0,"apiKey":"fictional-private-canary-9876"})).unwrap();s}
 fn payload(s:&Store,op:&str,extra:Value)->Value{let v=s.provider_view().unwrap();let mut p=json!({"requestId":crate::conversation_store::uid("setting"),"expectedCredentialRevision":v["credentialRevision"],"expectedProfileRevision":v["profileRevision"],"expectedCatalogRevision":s.catalog().unwrap()["revision"],"expectedSettingsRevision":v["settingsRevision"]});if op!="test_models"{p["testReceiptId"]=v.get("testReceiptId").cloned().unwrap_or(json!("missing"));}for(k,v)in extra.as_object().unwrap(){p[k]=v.clone();}p}
 fn action(s:&Store,op:&str,extra:Value)->R<Value>{s.controlled("save_ai_provider_settings",op,payload(s,op,extra))}
 fn select(s:&Store){action(s,"select_model",json!({"modelId":"user-synthetic-model"})).unwrap();}
 #[test]fn full_lifecycle_switch_retest_and_restart(){let s=store();assert_eq!(s.provider_view().unwrap()["enabled"],false);assert!(action(&s,"select_model",json!({"modelId":"user-synthetic-model"})).is_err());action(&s,"test_models",json!({})).unwrap();let v=s.provider_view().unwrap();assert!(v.get("modelId").is_none());assert_eq!(v["enabled"],false);assert!(action(&s,"set_enabled",json!({"enabled":true})).is_err());select(&s);assert_eq!(s.provider_view().unwrap()["enabled"],false);action(&s,"set_enabled",json!({"enabled":true})).unwrap();assert_eq!(s.provider_view().unwrap()["enabled"],true);
 assert_eq!(action(&s,"select_model",json!({"modelId":"fictional-model-b"})).unwrap()["state"],"retest_required");assert_eq!(s.provider_view().unwrap()["enabled"],false);action(&s,"test_models",json!({})).unwrap();action(&s,"select_model",json!({"modelId":"fictional-model-b"})).unwrap();action(&s,"set_enabled",json!({"enabled":true})).unwrap();let path=s.c.path().unwrap().to_owned();let before=s.provider_view().unwrap();drop(s);let s=Store::open(Path::new(&path)).unwrap();assert_eq!(s.provider_view().unwrap(),before);assert_eq!(provider_store::credential(&s.fixture()).unwrap().as_slice(),b"fictional-private-canary-9876");}
 #[test]fn legacy_auto_enabled_directory_has_no_authority(){let s=store();provider_store::dispatch(&crate::repository::Request{version:5,operation:"select_model".into(),payload:json!({"requestId":"legacy","modelId":"untested-legacy-model"})},&s.fixture()).unwrap();let v=s.provider_view().unwrap();assert_eq!(v["enabled"],false);assert_eq!(v["models"],json!([]));assert!(v.get("modelId").is_none());assert_eq!(v["credentialState"],"stored");assert!(s.controlled("save_ai_provider_settings","select_model",json!({"requestId":"old-dto","modelId":"untested-legacy-model"})).is_err());}
 #[test]fn duplicate_test_calls_once_and_unknown_never_retries(){let s=store();TEST_CALLS.with(|v|v.set(0));TEST_RESULT.with(|v|*v.borrow_mut()=Some(Err(error("provider_timeout"))));let p=payload(&s,"test_models",json!({}));assert_eq!(s.lifecycle_action("test_models",p.clone()).unwrap()["state"],"outcome_unknown");s.lifecycle_action("test_models",p).unwrap();assert_eq!(TEST_CALLS.with(|v|v.get()),1);assert_eq!(s.provider_view().unwrap()["models"],json!([]));assert_eq!(s.provider_view().unwrap()["enabled"],false);action(&s,"test_models",json!({})).unwrap();assert_eq!(TEST_CALLS.with(|v|v.get()),2);}
 #[test]fn credentials_receipt_and_config_revision_are_bound(){let s=store();action(&s,"test_models",json!({})).unwrap();let mut wrong=payload(&s,"select_model",json!({"modelId":"user-synthetic-model"}));wrong["testReceiptId"]=json!("forged");assert!(s.lifecycle_action("select_model",wrong).is_err());assert!(action(&s,"select_model",json!({"modelId":"not-in-directory"})).is_err());let stale=payload(&s,"select_model",json!({"modelId":"user-synthetic-model"}));s.controlled("save_ai_provider_settings","save_credential",json!({"requestId":"new-key","expectedCredentialRevision":1,"apiKey":"fictional-replacement-key-4321"})).unwrap();assert!(s.lifecycle_action("select_model",stale).is_err());assert_eq!(s.provider_view().unwrap()["connectionState"],"not_tested");action(&s,"test_models",json!({})).unwrap();select(&s);action(&s,"set_enabled",json!({"enabled":true})).unwrap();put(&s.c,"sources","_settings_catalog",&json!({"revision":7,"settings":null})).unwrap();assert_eq!(s.provider_view().unwrap()["enabled"],false);assert_eq!(s.provider_view().unwrap()["models"],json!([]));}
 #[test]fn reserved_lifecycle_never_enters_context_or_receipt_secret(){let s=store();action(&s,"test_models",json!({})).unwrap();let mut v=s.lifecycle().unwrap();v["authorized"]=json!(true);v["text"]=json!("private-lifecycle-canary");put(&s.c,"sources",SLOT,&v).unwrap();assert!(!enabled(&s.c,SLOT).unwrap());put(&s.c,"records","forged-lifecycle",&json!({"id":"forged-lifecycle","kind":"source_projection","domain":"health","sourceId":SLOT,"metric":"sleep","status":"active","version":1,"observedAt":now(),"text":"private-lifecycle-canary"})).unwrap();let d=json!({"requestId":"draft","turnId":"private","revision":1,"text":"睡眠记录"});s.draft(decode(d.clone()).unwrap(),d).unwrap();let p=json!({"requestId":"prepare","turnId":"private","expectedDraftRevision":1});let packet=s.prepare(decode(p.clone()).unwrap(),p).unwrap();assert!(!packet.to_string().contains("private-lifecycle-canary"));assert!(!packet["snapshot"]["sources"].to_string().contains(SLOT));let rows:Vec<String>=s.c.prepare("SELECT payload||result FROM requests").unwrap().query_map([],|r|r.get(0)).unwrap().collect::<Result<_,_>>().unwrap();assert!(!rows.join("").contains("fictional-private-canary-9876"));select(&s);action(&s,"set_enabled",json!({"enabled":true})).unwrap();let forged=json!({"requestId":"forged","turnId":"private","packetId":packet["id"],"modelId":"user-synthetic-model","inputRefs":[{"id":"forged-lifecycle","version":1,"authorizationGeneration":1}]});assert!(s.controlled("resolve_request_context","prepare_disclosure",forged).is_err());let clean=json!({"requestId":"clean","turnId":"private","packetId":packet["id"],"modelId":"user-synthetic-model","inputRefs":[]});let out=s.controlled("resolve_request_context","prepare_disclosure",clean).unwrap();assert!(!out["exactBody"].as_str().unwrap().contains("private-lifecycle-canary"));}
 #[test]fn all_revision_cas_and_raw_errors_fail_closed(){let s=store();TEST_CALLS.with(|v|v.set(0));for field in ["expectedCredentialRevision","expectedProfileRevision","expectedCatalogRevision","expectedSettingsRevision"]{let mut p=payload(&s,"test_models",json!({}));p[field]=json!(999);assert!(s.lifecycle_action("test_models",p).is_err());}assert_eq!(TEST_CALLS.with(|v|v.get()),0);TEST_RESULT.with(|v|*v.borrow_mut()=Some(Err(error("raw-http-error-private-canary"))));action(&s,"test_models",json!({})).unwrap();assert_eq!(s.provider_view().unwrap()["testErrorCode"],"provider_unavailable");let rows:Vec<String>=s.c.prepare("SELECT payload||result FROM requests").unwrap().query_map([],|r|r.get(0)).unwrap().collect::<Result<_,_>>().unwrap();assert!(!rows.join("").contains("raw-http-error-private-canary"));}
 #[test]fn actual_catalog_changes_disable_and_unapproved_endpoint_is_rejected(){for variant in 0..4{let s=store();action(&s,"test_models",json!({})).unwrap();select(&s);action(&s,"set_enabled",json!({"enabled":true})).unwrap();let mut c=super::super::controlled_tests::catalog_config("cloud","deepseek","");match variant{0=>c=super::super::controlled_tests::catalog_config("local","ollama",""),1=>c=super::super::controlled_tests::catalog_config("cloud","openai",""),2=>c["advanced"]["timeoutSeconds"]=json!(61),_=>c["primary"]["modelLabel"]=json!("new-pending-label")};s.save_catalog(json!({"requestId":"config","expectedRevision":0,"settings":c})).unwrap();assert_eq!(s.provider_view().unwrap()["enabled"],false);assert_eq!(s.provider_view().unwrap()["connectionState"],"not_tested");}let s=store();let mut c=super::super::controlled_tests::catalog_config("cloud","deepseek","");c["primary"]["endpointUrl"]=json!("https://unapproved.invalid");assert!(s.save_catalog(json!({"requestId":"bad","expectedRevision":0,"settings":c})).is_err());}
 #[test]fn strict_dto_cannot_inject_transport_or_nulls(){let s=store();for field in ["url","apiKey","body","providerId"]{let mut p=payload(&s,"test_models",json!({}));p[field]=json!("forged");assert!(s.lifecycle_action("test_models",p).is_err());}let mut p=payload(&s,"test_models",json!({}));p["expectedCredentialRevision"]=Value::Null;assert!(s.lifecycle_action("test_models",p).is_err());}
}

#[cfg(test)]mod metadata_joint_tests{
 use super::*;
 #[test]fn metadata_entry_uses_identical_effective_provider_logic_with_full_store_and_fake_ffi(){
  for case in ["raw_false_effective_true","raw_true_effective_false","model_changed","credential_revision","profile_revision","catalog_revision","missing_lifecycle"]{
   let s=super::tests::store();let raw=provider_store::settings(&s.fixture()).unwrap();assert_eq!(raw["enabled"],false);
   let mut lifecycle=json!({"schemaVersion":1,"revision":1,"state":"succeeded","credentialRevision":raw["credentialRevision"],"profileRevision":raw["profileRevision"],"catalogRevision":0,"models":["deepseek-v4-pro","other-model"],"selectedModel":"deepseek-v4-pro","enabled":true,"testReceiptId":"fixture"});
   if case=="raw_true_effective_false"{provider_store::metadata_set_fake_raw_enabled(&s.fixture());lifecycle["enabled"]=json!(false);}
   if case=="model_changed"{lifecycle["selectedModel"]=json!("other-model");}
   for (name,field) in [("credential_revision","credentialRevision"),("profile_revision","profileRevision"),("catalog_revision","catalogRevision")]{if case==name{lifecycle[field]=json!(99);}}
   if case!="missing_lifecycle"{put(&s.c,"sources",SLOT,&lifecycle).unwrap();}
   let authoritative=s.provider_view().unwrap();let should=authoritative["enabled"]==true&&authoritative["modelId"]=="deepseek-v4-pro";assert_eq!(should,case=="raw_false_effective_true");
   let mut calls=0;let result=provider_store::metadata_fixture(&s.fixture(),&s.c,|reference|{calls+=1;crate::secure_credentials::metadata::inspect_fake(reference)});
   assert_eq!(result.is_ok(),should,"{case}");assert_eq!(calls,usize::from(should));if should{let result=result.unwrap();assert_eq!(result["stage"],"complete");assert!(!result.to_string().contains("fictional"));assert_eq!(result["currentAppMatches"],"unknown");}
   assert!(Store::actions(&s.c).unwrap().is_empty());
  }
 }
}
