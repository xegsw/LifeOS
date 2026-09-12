mod repository{#[derive(Debug,serde::Serialize)]pub struct Error{pub code:String}impl Error{pub fn new(s:&str)->Self{Self{code:s.into()}}}impl From<rusqlite::Error> for Error{fn from(_:rusqlite::Error)->Self{Self::new("store_operation_failed")}}}
#[path="../strict_json.rs"]mod strict_json;
#[path="../health_conversation_host.rs"]mod health_conversation_host;
use std::io::{self,BufRead,Write};
fn main(){unsafe{libc::umask(0o077);}let s=health_conversation_host::Store::open_driver().unwrap();for line in io::stdin().lock().lines(){let v:serde_json::Value=serde_json::from_str(&line.unwrap()).unwrap();let r=s.dispatch(v["command"].as_str().unwrap(),&serde_json::to_vec(&v["request"]).unwrap());let result=match r{Ok(x)=>serde_json::json!({"id":v["id"],"ok":true,"result":x}),Err(e)=>serde_json::json!({"id":v["id"],"ok":false,"error":e})};println!("{}",result);io::stdout().flush().unwrap();}}
