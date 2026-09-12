pub mod repository {
 #[derive(Debug,serde::Serialize)] pub struct Error { pub code:String }
 impl Error { pub fn new(s:&str)->Self { Self{code:s.into()} } }
 impl From<rusqlite::Error> for Error { fn from(_:rusqlite::Error)->Self {Self::new("store_operation_failed")} }
 #[derive(serde::Deserialize)] #[serde(deny_unknown_fields)] pub struct Request {pub version:u8,pub operation:String,pub payload:serde_json::Value}
}
pub mod conversation_store {
 pub fn now()->u64 {std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_millis() as u64}
 pub fn uid(prefix:&str)->String {use rand::RngCore;let mut b=[0u8;16];rand::rngs::OsRng.fill_bytes(&mut b);format!("{}-{}",prefix,b.iter().map(|b|format!("{b:02x}")).collect::<String>())}
}
