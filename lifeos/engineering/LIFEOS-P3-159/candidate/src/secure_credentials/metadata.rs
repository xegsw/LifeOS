//! One approved metadata inspection. Opaque objects remain in the C adapter.
use serde_json::{json,Value};
#[repr(C)]#[derive(Clone,Copy,Default)]struct Rule{kind:u32,count:u32,prompt:u32}
#[repr(C)]#[derive(Default)]struct Raw{stage:u32,status:i32,found:u32,count:u32,rules:[Rule;32]}
extern "C"{fn lifeos_metadata(service:*const u8,sl:u32,account:*const u8,al:u32,out:*mut Raw);}
fn summary(r:Raw)->Value{
 let stage=match r.stage{1=>"default_keychain",2=>"single_item_reference",3=>"item_access",4=>"decrypt_rules",5=>"rule_contents",7=>"complete",_=>"unknown"};
 let rules=if r.stage==7&&r.status==0&&r.count<=32 {Some(r.rules[..r.count as usize].iter().map(|r|json!({"applicationList":match r.kind{0=>"unrestricted",1=>"empty",2=>"restricted",_=>"unknown"},"trustedApplicationCount":r.count,"promptFlags":r.prompt,"requiresPasswordPrompt":r.prompt&1!=0})).collect::<Vec<_>>())}else{None};
 json!({"stage":stage,"osStatus":r.status,"itemFound":r.found==1,"decryptRuleCount":rules.as_ref().map(Vec::len),"rules":rules,"currentAppMatches":"unknown","priorAppMatches":"unknown"})
}
pub(crate) fn inspect(reference:&str)->Value{
 let Ok(lineage)=super::reference_lineage(reference)else{return super::ReadDiagnostic::new("configuration_binding",None).value()};
 let mut result=None;
 let operation=super::with_noninteractive_policy(&super::MacosInteractionPolicy,||{
  let service=lineage.keychain_service();let mut out=Raw::default();
  unsafe{lifeos_metadata(service.as_ptr(),service.len() as u32,reference.as_ptr(),reference.len() as u32,&mut out);}
  result=Some(summary(out));Ok(())
 });
 if operation.is_err(){super::ReadDiagnostic::capture().value()}else{result.unwrap()}
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn metadata_summary_distinguishes_unrestricted_empty_and_restricted_without_objects(){let mut r=Raw{stage:7,count:3,found:1,..Default::default()};r.rules[0]=Rule{kind:0,count:0,prompt:1};r.rules[1]=Rule{kind:1,count:0,prompt:0};r.rules[2]=Rule{kind:2,count:2,prompt:16};let v=summary(r);assert_eq!(v["rules"][0]["applicationList"],"unrestricted");assert_eq!(v["rules"][1]["applicationList"],"empty");assert_eq!(v["rules"][2]["trustedApplicationCount"],2);assert_eq!(v["rules"][0]["requiresPasswordPrompt"],true);assert_eq!(v["currentAppMatches"],"unknown");assert_eq!(v["priorAppMatches"],"unknown");assert_eq!(v.as_object().unwrap().len(),7);}
 #[test]fn metadata_partial_or_denied_never_publishes_partial_acl(){for stage in 0..7{let v=summary(Raw{stage,status:-25293,count:32,found:1,..Default::default()});assert!(v["rules"].is_null());assert!(v["decryptRuleCount"].is_null());assert_eq!(v["osStatus"],-25293);}}
}

#[cfg(test)]pub(crate) fn inspect_fake(reference:&str)->Value{
 extern "C"{fn lifeos_metadata_fake(service:*const u8,sl:u32,account:*const u8,al:u32,out:*mut Raw);fn lifeos_metadata_fake_calls()->i32;fn lifeos_metadata_fake_releases()->i32;}
 let service=super::reference_lineage(reference).unwrap().keychain_service();let mut raw=Raw::default();unsafe{let calls=lifeos_metadata_fake_calls();let releases=lifeos_metadata_fake_releases();lifeos_metadata_fake(service.as_ptr(),service.len() as u32,reference.as_ptr(),reference.len() as u32,&mut raw);assert_eq!(lifeos_metadata_fake_calls(),calls+1);assert_eq!(lifeos_metadata_fake_releases(),releases+1);}summary(raw)
}
