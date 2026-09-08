#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod repository;
mod source_api;
mod source_file;
mod source_store;
mod source_targets;
mod source_worker;
use repository::{Error, Request};
use serde_json::{json, Value};
use std::io::{self, BufRead};
// Production credentials and provider sources are retained but deliberately NOT modules.
macro_rules! command {
    ($name:ident) => {
        #[tauri::command]
        fn $name(request: Request) -> Result<Value, Error> {
            repository::dispatch(stringify!($name), request, "app")
        }
    };
}
command!(capture_record);
command!(get_today);
command!(runtime_status);
command!(confirm_capture_context);
command!(get_context_recovery);
command!(get_context_next_action);
command!(decide_context_next_action);
command!(record_action_result);
command!(assemble_global_ai_context);
command!(get_evidence_backed_understanding);
command!(decide_understanding_feedback);
command!(get_ai_provider_settings);
command!(save_ai_provider_settings);
command!(save_ai_provider_credential);
command!(test_ai_provider_connection);
command!(set_ai_provider_enabled);
command!(upsert_durable_memory);
command!(update_current_state);
command!(resolve_request_context);
command!(get_context_disclosure_receipt);
macro_rules! source_command {
    ($name:ident) => {
        #[tauri::command]
        fn $name(request: source_api::Request) -> Result<Value, Error> {
            source_api::dispatch(stringify!($name), request, "app")
        }
    };
}
source_command!(connect_source_directory);
source_command!(control_source_job);
source_command!(get_source_status);
source_command!(authorize_source_target);
source_command!(get_source_evidence);
fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--repository-stdio") {
        let fixture = args.get(2).map(String::as_str).unwrap_or("app");
        for line in io::stdin().lock().lines() {
            let result = line.map_err(|_| Error::new("stdio_failed")).and_then(|s| {
                let mut v: Value =
                    serde_json::from_str(&s).map_err(|_| Error::new("malformed_request"))?;
                let ipc = v
                    .get("ipc")
                    .and_then(Value::as_str)
                    .ok_or_else(|| Error::new("unknown_ipc"))?
                    .to_string();
                if source_api::COMMANDS.contains(&ipc.as_str()) {
                    let request = serde_json::from_value(
                        v.get_mut("request")
                            .ok_or_else(|| Error::new("malformed_request"))?
                            .take(),
                    )
                    .map_err(|_| Error::new("malformed_request"))?;
                    return source_api::dispatch(&ipc, request, fixture);
                }
                let req: Request = serde_json::from_value(
                    v.get_mut("request")
                        .ok_or_else(|| Error::new("malformed_request"))?
                        .take(),
                )
                .map_err(|_| Error::new("malformed_request"))?;
                repository::dispatch(&ipc, req, fixture)
            });
            println!(
                "{}",
                match result {
                    Ok(v) => json!({"ok":v}),
                    Err(e) => json!({"error":e}),
                }
            );
        }
        return;
    }
    repository::open("app").expect("P3-147 root/store rejected");
    source_api::resume("app").expect("source resume failed");
    let mut context = tauri::generate_context!();
    if std::env::var("LIFEOS_P3_147_VIEWPORT").ok().as_deref() == Some("narrow") {
        context.config_mut().app.windows[0].width = 700.0;
        context.config_mut().app.windows[0].height = 760.0;
    }
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            capture_record,
            get_today,
            runtime_status,
            confirm_capture_context,
            get_context_recovery,
            get_context_next_action,
            decide_context_next_action,
            record_action_result,
            assemble_global_ai_context,
            get_evidence_backed_understanding,
            decide_understanding_feedback,
            get_ai_provider_settings,
            save_ai_provider_settings,
            save_ai_provider_credential,
            test_ai_provider_connection,
            set_ai_provider_enabled,
            upsert_durable_memory,
            update_current_state,
            resolve_request_context,
            get_context_disclosure_receipt,
            connect_source_directory,
            control_source_job,
            get_source_status,
            authorize_source_target,
            get_source_evidence
        ])
        .run(context)
        .expect("P3-147 app failed");
}
