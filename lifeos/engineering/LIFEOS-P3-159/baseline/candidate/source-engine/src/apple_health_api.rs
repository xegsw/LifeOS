//! Internal application request model. Host registration requires the pending IPC approval.
use crate::{
    apple_health as health,
    repository::{self, Error},
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::sync::{Mutex, OnceLock};
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    version: u8,
    payload: Action,
}
#[derive(Debug, Deserialize)]
#[serde(tag = "action", rename_all = "lowercase", deny_unknown_fields)]
enum Action {
    List {},
    Status {},
    Start { file: String },
}
#[derive(Default)]
struct Job {
    fixture: String,
    running: bool,
    value: Value,
}
static JOB: OnceLock<Mutex<Job>> = OnceLock::new();
fn job() -> &'static Mutex<Job> {
    JOB.get_or_init(Default::default)
}
pub fn parse(bytes: &str) -> Result<Request, Error> {
    serde_json::from_value(crate::strict_json::parse(bytes)?)
        .map_err(|_| Error::new("health_request_rejected"))
}
pub fn dispatch_raw(body: tauri::ipc::InvokeBody, fixture: &str) -> Result<Value, Error> {
    let tauri::ipc::InvokeBody::Raw(bytes) = body else {
        return Err(Error::new("health_raw_required"));
    };
    if bytes.len() > 4096 {
        return Err(Error::new("health_request_limit"));
    }
    let text = std::str::from_utf8(&bytes).map_err(|_| Error::new("health_request_rejected"))?;
    dispatch(parse(text)?, fixture)
}
pub fn dispatch(r: Request, fixture: &str) -> Result<Value, Error> {
    if r.version != 1 {
        return Err(Error::new("health_request_rejected"));
    }
    match r.payload {
        Action::List {} => if crate::runtime_root::is_real(){Ok(json!({"files":["导出.zip"],"mode":"real"}))}else{Ok(json!({"files":health::files()?,"mode":"synthetic"}))},
        Action::Status {} => {
            let j = job().lock().map_err(|_| Error::new("health_busy"))?;
            if j.fixture == fixture && !j.value.is_null() {
                return Ok(j.value.clone());
            }
            drop(j);
            let c = repository::open(fixture)?;
            use rusqlite::OptionalExtension;
            if crate::runtime_root::is_real(){status_table(&c)?;let last:Option<String>=c.query_row("SELECT value FROM health_import_status WHERE id=1",[],|r|r.get(0)).optional()?;let mut v:Value=last.and_then(|x|serde_json::from_str(&x).ok()).unwrap_or(json!({"status":"idle"}));if v["status"]=="running"{v["status"]=json!("paused");}return Ok(v)}
            let last:Option<String>=c.query_row("SELECT json_extract(body,'$.result') FROM records WHERE json_extract(body,'$.protocol')='apple-file-v1' AND json_extract(body,'$.kind')='health_batch' ORDER BY json_extract(body,'$.receivedAt') DESC,id DESC LIMIT 1",[],|r|r.get(0)).optional()?;
            Ok(last
                .and_then(|v| serde_json::from_str(&v).ok())
                .unwrap_or(json!({"status":"idle"})))
        }
        Action::Start { file } => {
            if file.starts_with("test-") {
                return Err(Error::new("health_filename_rejected"));
            }
            let mut j = job().lock().map_err(|_| Error::new("health_busy"))?;
            if j.running {
                return Err(Error::new("health_busy"));
            }
            if crate::runtime_root::is_real(){if file!="导出.zip"{return Err(Error::new("health_filename_rejected"))}}else{health::selected(&file)?;} // Start is a manual action; worker validates again.
            j.fixture = fixture.into();
            j.running = true;
            j.value = json!({"status":"running","phase":"读取与校验","file":file,"processed":0});
            if crate::runtime_root::is_real(){persist_started(&mut j,|v|save_status(fixture,v))?;}
            let initial = j.value.clone();
            drop(j);
            let fixture = fixture.to_owned();
            std::thread::spawn(move || {
                let result = std::panic::catch_unwind(|| {
                    if crate::runtime_root::is_real(){return crate::health_target::import_fixed(&file,&serde_json::from_str(include_str!("../apple_health_limits.json")).map_err(|_|Error::new("health_limits_rejected"))?,|n|{if let Ok(mut j)=job().lock(){j.value["processed"]=json!(n);j.value["phase"]=json!("校验与事务导入");}})}
                    let mut c = repository::open(&fixture)?;
                    health::import(
                        &mut c,
                        &file,
                        health::now(),
                        &serde_json::from_str(include_str!("../apple_health_limits.json"))
                            .map_err(|_| Error::new("health_limits_rejected"))?,
                        |n| {
                            if let Ok(mut j) = job().lock() {
                                j.value["processed"] = json!(n);
                                j.value["phase"] = json!("校验与事务导入");
                            }
                        },
                        None,
                    )
                })
                .unwrap_or_else(|_| Err(Error::new("health_import_interrupted")));
                if let Ok(mut j) = job().lock() {
                    j.running = false;
                    j.value = match result {
                        Ok(v) => v,
                        Err(e) => {
                            json!({"status":"failed","file":file,"failed":1,"inserted":0,"code":e.code,"recordCountsKnown":false})
                        }
                    };
                    if crate::runtime_root::is_real()&&save_status(&fixture,&j.value).is_err(){j.value["statusPersistenceWarning"]=json!(true);}
                }
            });
            Ok(initial)
        }
    }
}
pub fn running()->bool{job().lock().map(|j|j.running).unwrap_or(true)}
fn status_table(c:&rusqlite::Connection)->Result<(),Error>{c.prepare("SELECT id,value FROM health_import_status LIMIT 0").map_err(|_|Error::new("health_schema_rejected"))?;Ok(())}
fn save_status(fixture:&str,v:&Value)->Result<(),Error>{let c=repository::open(fixture)?;status_table(&c)?;c.execute("INSERT INTO health_import_status VALUES(1,?1) ON CONFLICT(id) DO UPDATE SET value=?1",[v.to_string()])?;Ok(())}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn action_schema_rejects_nested_unknown_and_forbidden_file() {
        for raw in [
            r#"{"version":1,"payload":{"action":"list","file":"x.xml"}}"#,
            r#"{"version":1,"payload":{"action":"status","file":"x.xml"}}"#,
            r#"{"version":1,"payload":{"action":"start"}}"#,
            r#"{"version":1,"payload":{"action":"start","file":{"path":"x.xml"}}}"#,
            r#"{"version":1,"payload":{"action":"start","file":"x.xml","extra":{}}}"#,
            r#"{"version":1,"version":1,"payload":{"action":"list"}}"#,
            r#"{"version":1,"other":0,"payload":{"action":"list"}}"#,
        ] {
            assert!(parse(raw).is_err(), "{raw}");
        }
        assert!(parse(r#"{"version":1,"payload":{"action":"list"}}"#).is_ok());
        assert!(parse(
            r#"{"version":1,"payload":{"action":"start","file":"01-synthetic-export.xml"}}"#
        )
        .is_ok());
    }
    #[test]
    fn start_busy_status_completion_and_retry() {
        let fixture = format!("apple-api-{}-{}", std::process::id(), health::now());
        let request = |file: &str| {
            parse(&json!({"version":1,"payload":{"action":"start","file":file}}).to_string())
                .unwrap()
        };
        dispatch(request("07-large.xml"), &fixture).unwrap();
        assert_eq!(
            dispatch(request("01-synthetic-export.xml"), &fixture)
                .unwrap_err()
                .code,
            "health_busy"
        );
        let status = || {
            dispatch(
                parse(r#"{"version":1,"payload":{"action":"status"}}"#).unwrap(),
                &fixture,
            )
            .unwrap()
        };
        let until_done = || {
            for _ in 0..600 {
                let v = status();
                if v["status"] != "running" {
                    return v;
                }
                std::thread::sleep(std::time::Duration::from_millis(20));
            }
            panic!("timeout")
        };
        assert_eq!(until_done()["status"], "completed");
        dispatch(request("04-broken.xml"), &fixture).unwrap();
        assert_eq!(until_done()["status"], "failed");
        dispatch(request("07-large.xml"), &fixture).unwrap();
        assert_eq!(until_done()["status"], "duplicate");
    }
    #[test]
    fn raw_wire_rejects_before_any_host_contact() {
        use tauri::ipc::InvokeBody;
        for body in [
            InvokeBody::Json(json!({"version":1,"payload":{"action":"list"}})),
            InvokeBody::Raw(vec![b'a'; 4097]),
            InvokeBody::Raw(vec![0xff]),
            InvokeBody::Raw(
                br#"{"version":1,"payload":{"action":"list","action":"status"}}"#.to_vec(),
            ),
        ] {
            assert!(dispatch_raw(body, "not/a/fixture").is_err());
        }
    }
}
#[cfg(feature="boundary-tests")]
pub fn synthetic_status_schema_check()->Result<(),Error>{
 assert!(!crate::runtime_root::is_real());let c=rusqlite::Connection::open_in_memory()?;
 let version=||c.query_row("PRAGMA schema_version",[],|r|r.get::<_,i64>(0)).unwrap();let before=version();
 assert_eq!(status_table(&c).unwrap_err().code,"health_schema_rejected");assert_eq!(version(),before);
 c.execute_batch("CREATE TABLE health_import_status(id INTEGER PRIMARY KEY CHECK(id=1),value TEXT NOT NULL);INSERT INTO health_import_status VALUES(1,'{\"status\":\"running\",\"file\":\"synthetic.zip\"}')")?;
 let before=version();status_table(&c)?;assert_eq!(version(),before);Ok(())
}

fn persist_started(j:&mut Job,save:impl FnOnce(&Value)->Result<(),Error>)->Result<(),Error>{
 if let Err(e)=save(&j.value){j.running=false;j.value=json!({"status":"failed","file":j.value["file"],"failed":1,"inserted":0,"code":e.code,"recordCountsKnown":false});return Err(e)}Ok(())
}
#[cfg(feature="boundary-tests")]
pub fn synthetic_start_persistence_check()->Result<(),Error>{
 let mut j=Job{fixture:"synthetic".into(),running:true,value:json!({"status":"running","file":"synthetic.zip","processed":0})};
 assert_eq!(persist_started(&mut j,|_|Err(Error::new("database_unavailable"))).unwrap_err().code,"database_unavailable");assert!(!j.running);assert_eq!(j.value["status"],"failed");assert_eq!(j.value["inserted"],0);Ok(())
}
