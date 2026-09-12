#[path="../host_support.rs"]mod host_support;pub use host_support::{repository,conversation_store};
#[path="../strict_json.rs"]mod strict_json;
#[path="../health_conversation_host.rs"]mod health_conversation_host;
use std::io::{self,BufRead,Write};
fn main(){unsafe{libc::umask(0o077);}let s=std::sync::Arc::new(std::sync::Mutex::new(health_conversation_host::Store::open_driver().unwrap()));for line in io::stdin().lock().lines(){let v:serde_json::Value=serde_json::from_str(&line.unwrap()).unwrap();let s=s.clone();std::thread::spawn(move||{let r=host_gateway::dispatch(&s,v["command"].as_str().unwrap(),&serde_json::to_vec(&v["request"]).unwrap());let result=match r{Ok(x)=>serde_json::json!({"id":v["id"],"ok":true,"result":x}),Err(e)=>serde_json::json!({"id":v["id"],"ok":false,"error":e})};println!("{}",result);io::stdout().flush().unwrap();});}}


#[path="../conversation_contract.rs"]mod conversation_contract;
#[path="../runtime_root.rs"]mod runtime_root;
#[path="../secure_credentials.rs"]mod secure_credentials;
#[path="../provider_store.rs"]mod provider_store;
#[path="../wire_encoding.rs"]mod wire_encoding;
#[path="../provider_transport.rs"]mod provider_transport;
#[path="../model_port.rs"]mod model_port;

#[path="../host_gateway.rs"]mod host_gateway;

#[path="../health_reader.rs"]mod health_reader;
#[path="../health_source.rs"]mod health_source;
