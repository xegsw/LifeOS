# coding: utf-8
from pathlib import Path
import re,shutil
r=Path(__file__).resolve().parents[1]/'candidate';old=r.parents[1]/'LIFEOS-P3-148/candidate'
for name in ['secure_credentials.rs','provider_store.rs','wire_encoding.rs','provider_transport.rs','model_port.rs']:
 s=(old/'src'/name).read_text().replace('P3-148','P3-152').replace('p3-148','p3-152').replace('P3_148','P3_152')
 if name=='secure_credentials.rs':s=s.split('#[cfg(test)]\nmod tests')[0]
 if name=='provider_store.rs':
  s=s.split('#[cfg(test)]\nmod p148_tests')[0]
  s=re.sub(r'#\[cfg\(test\)\]\n#\[path = "provider_lifecycle_tests.rs"\]\nmod lifecycle_mock;\n','',s)
  s=re.sub(r'        #\[cfg\(test\)\]\n        if let Some\(result\) = lifecycle_mock::(?:add|find|delete)\(.*?\n        }\n','',s,flags=re.S)
  s=re.sub(r'\s*#\[cfg\(test\)\]\n\s*lifecycle_mock::checkpoint\("[^"]+"\)\?;','',s)
  start=s.index('        "test_connection" => {');end=s.index('        "select_model" => {',start)
  s=s[:start]+'        "test_connection" => return fail("real_capability_denied"),\n'+s[end:]
  start=s.index('            if s["testReceiptId"] != p["testReceiptId"]');end=s.index('            s.clone()',start)
  s=s[:start]+'''            let model=p["modelId"].as_str().ok_or_else(|| Error::new("model_rejected"))?;
            if model.is_empty()||model.len()>128||!model.bytes().all(|b|b.is_ascii_alphanumeric()||b"_.:-".contains(&b)){return fail("model_rejected");}
            if !s["models"].as_array().unwrap().contains(&p["modelId"]){s["models"].as_array_mut().unwrap().push(p["modelId"].clone());}
            s["modelId"] = p["modelId"].clone();
            s["enabled"] = json!(envelope.is_some());
'''+s[end:]
  s=s.replace('            s = default_profile();\n            s["credentialRevision"] = json!(cr + 1);\n            s["credentialState"]', '            s["enabled"] = json!(s.get("modelId").is_some());\n            s["credentialRevision"] = json!(cr + 1);\n            s["credentialState"]',1)
 if name=='provider_transport.rs':
  s=s.replace('("/models", false) | ("/chat/completions", true)','("/chat/completions", true)')
  start=s.index('pub fn models(');end=s.index('pub struct DeepSeekModel;',start)
  s=s[:start]+s[end:]
  s=s.split('#[cfg(test)]\nmod p148_transport_checks')[0]
 (r/'src'/name).write_text(s)
s=(old/'src/conversation_contract.rs').read_text();s=s[:s.index('pub fn validate(')];(r/'src/conversation_contract.rs').write_text(s)
(r/'src/runtime_root.rs').write_text('''//! P3-152 synthetic stage: a compile-time false network/Keychain gate.
pub fn is_real()->bool{false}
pub fn verify()->Result<std::path::PathBuf,crate::repository::Error>{crate::health_conversation_host::verify_root()?;Ok(std::path::PathBuf::from(crate::health_conversation_host::ROOT).join("synthetic"))}
''')
p=r/'src/health_conversation_host.rs';s=p.read_text().replace('pub const ROOT:', 'pub const ROOT:');
# Expose only the existing exact root ownership check to the provider adapter.
pos=s.index('pub struct Store') if 'pub struct Store' in s else -1
print(s[:s.index('impl Store')][-1800:])
