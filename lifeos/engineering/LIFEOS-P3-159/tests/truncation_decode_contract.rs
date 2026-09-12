
#[test]
fn p158_truncation_classification_contract() {
 use crate::provider_transport::decode_chat_response;
 let wrap=|reason:&str,content:&str|json!({"choices":[{"finish_reason":reason,"message":{"content":content}}]}).to_string();
 for content in ["", "{", "{\"schemaVersion\":8,\"answerText\":\"\",\"candidate\":{\"operation\":\"none\"}}"] {assert_eq!(decode_chat_response(wrap("length",content).as_bytes()).err().unwrap().code,"provider_response_truncated");}
 assert_eq!(decode_chat_response(wrap("stop","").as_bytes()).err().unwrap().code,"provider_response_empty");
 assert_eq!(decode_chat_response(wrap("stop",&"x".repeat(16001)).as_bytes()).err().unwrap().code,"response_too_large");
 assert_eq!(decode_chat_response(b"{").err().unwrap().code,"provider_protocol");
 let good=wrap("stop","{\"schemaVersion\":8,\"answerText\":\"\",\"candidate\":{\"operation\":\"none\"}}");assert!(decode_chat_response(good.as_bytes()).is_ok());
 let r=store();let p=prepare(&r,"查询公开合成笔记");let body:Value=serde_json::from_str(p["exactBody"].as_str().unwrap()).unwrap();assert_eq!(body["max_tokens"],1024);assert_eq!(body["response_format"]["type"],"json_object");assert!(body.get("thinking").is_none());assert!(p["systemPolicy"].as_str().unwrap().contains("answerText=\"\""));
}
