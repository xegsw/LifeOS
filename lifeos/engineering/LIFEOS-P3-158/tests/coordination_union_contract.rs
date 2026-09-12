
#[test]
fn v8_external_union_contract_matrix() {
 let s=Arc::new(Mutex::new(store()));let first=prepare(&s.lock().unwrap(),"如果合成预报下雨，就创建本地安排");let out=send(&s,&first,query(&first,2,0));let p=second(&s.lock().unwrap(),&out);let mut t=s.lock().unwrap().v8_get(p["turnRequestId"].as_str().unwrap()).unwrap();
 t["targetMap"]["matrix-target"]=json!({"id":"matrix-action","version":1,"status":"planned"});
 let mut variants=vec![json!({"operation":"none"}),json!({"operation":"clarify","question":"请明确事项","targetRefs":[],"intent":"unknown"}),create(&p),conditional(&p,false),query(&first,0,0)];
 for op in ["adjust","complete","cancel"] {let mut c=json!({"operation":op,"targetRef":"matrix-target","expectedVersion":1,"evidenceSpans":spans(&p)});if op=="adjust"{c["content"]=json!("公开合成调整");c["sourceRefs"]=json!([]);}variants.push(c);}
 for c in variants {let response=json!({"schemaVersion":8,"answerText":"","candidate":c});assert!(contract::response(&t,response.clone(),"first").is_ok(),"positive {}",c["operation"]);
  let mut extra=response.clone();extra["candidate"]["permissionToken"]=json!("forged");assert!(contract::response(&t,extra,"first").is_err());
  for field in c.as_object().unwrap().keys(){let mut missing=response.clone();missing["candidate"].as_object_mut().unwrap().remove(field);assert!(contract::response(&t,missing,"first").is_err(),"missing {field}");let mut null=response.clone();null["candidate"][field]=Value::Null;assert!(contract::response(&t,null,"first").is_err(),"null {field}");}
  let raw=c.to_string();let duplicate=format!("{{\"operation\":{},{}",c["operation"],&raw[1..]);assert!(crate::strict_json::parse(&duplicate).is_err());
 }
 for (field,too_long) in [("answerText",2001)]{let mut r=json!({"schemaVersion":8,"answerText":"","candidate":{"operation":"none"}});r[field]=json!("字".repeat(too_long));assert!(contract::response(&t,r,"first").is_err());}
 for n in [0,501] {let mut c=create(&p);c["content"]=json!("字".repeat(n));assert!(contract::response(&t,json!({"schemaVersion":8,"answerText":"","candidate":c}),"first").is_err());}
 let mut c=create(&p);c["evidenceSpans"]=json!([]);assert!(contract::response(&t,json!({"schemaVersion":8,"answerText":"","candidate":c}),"first").is_err());
}
