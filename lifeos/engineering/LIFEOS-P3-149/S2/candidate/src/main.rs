#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod artifact_io;
mod apple_health;
mod apple_health_api;
mod health_domain;
mod health_snapshot;
mod health_ingestion;
mod conversation_contract;
mod conversation_store;
mod ipc_boundary;
mod model_port;
mod provider_store;
mod provider_transport;
mod repository;
mod runtime_root;
mod secure_credentials;
mod source_api;
mod source_file;
mod source_store;
mod source_targets;
mod source_worker;
mod strict_json;
mod wire_encoding;
use repository::{Error, Request};
use serde_json::{json, Value};
use std::io::{self, BufRead};
// Host work runs off the UI thread; the compiled engineering profile denies real transport.
macro_rules! command {
    ($name:ident) => {
        #[tauri::command]
        async fn $name(request: tauri::ipc::Request<'_>) -> Result<Value, Error> {
            let body = request.body().clone();
            tauri::async_runtime::spawn_blocking(move || {
                ipc_boundary::dispatch_with(stringify!($name), body, |request, modern| {
                    if modern {
                        conversation_store::dispatch(stringify!($name), request, "app")
                    } else {
                        repository::dispatch(stringify!($name), request, "app")
                    }
                })
            })
            .await
            .map_err(|_| Error::new("database_unavailable"))?
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
command!(send_source_ai_request);
macro_rules! source_command {
    ($name:ident) => {
        #[tauri::command]
        async fn $name(request: source_api::Request) -> Result<Value, Error> {
            tauri::async_runtime::spawn_blocking(move || {
                source_api::dispatch(stringify!($name), request, "app")
            })
            .await
            .map_err(|_| Error::new("database_unavailable"))?
        }
    };
}
source_command!(connect_source_directory);
source_command!(control_source_job);
source_command!(get_source_status);
source_command!(authorize_source_target);
source_command!(get_source_evidence);
#[tauri::command]
async fn import_apple_health_file(request:tauri::ipc::Request<'_>)->Result<Value,Error>{
    let body=request.body().clone();
    tauri::async_runtime::spawn_blocking(move||apple_health_api::dispatch_raw(body,"app")).await.map_err(|_|Error::new("health_import_interrupted"))?
}
fn main() {
    if runtime_root::is_real() {
        // No user content diagnostic channel in the real application, including panic output.
        std::panic::set_hook(Box::new(|_| {}));
        unsafe {
            let fd = libc::open(c"/dev/null".as_ptr(), libc::O_RDWR);
            if fd >= 0 {
                libc::dup2(fd, 0);
                libc::dup2(fd, 1);
                libc::dup2(fd, 2);
                if fd > 2 {
                    libc::close(fd);
                }
            }
            libc::umask(0o077);
        }
    }
    let args: Vec<String> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("--profile-info") {
        match runtime_root::profile_info() {
            Ok(v) => println!("{}", v),
            Err(e) => {
                eprintln!("{}", e.code);
                std::process::exit(2);
            }
        }
        return;
    }
    if args.get(1).map(String::as_str) == Some("--init-synthetic-fixture") {
        if runtime_root::is_real() {
            std::process::exit(2);
        }
        let fixture = args.get(2).expect("fixture required");
        let c = repository::open(fixture).expect("synthetic fixture init");
        source_store::init(&c).expect("synthetic source schema");
        c.execute_batch("CREATE TABLE IF NOT EXISTS source_api_requests(id TEXT PRIMARY KEY,payload TEXT NOT NULL,result TEXT NOT NULL);CREATE TABLE IF NOT EXISTS source_runtime_errors(connector_id TEXT PRIMARY KEY,code TEXT NOT NULL);").expect("synthetic api schema");
        return;
    }
    if args.get(1).map(String::as_str) == Some("--repository-stdio") {
        if runtime_root::is_real() {
            std::process::exit(2);
        }
        let fixture = args.get(2).map(String::as_str).unwrap_or("app");
        for line in io::stdin().lock().lines() {
            let result = line.map_err(|_| Error::new("stdio_failed")).and_then(|s| {
                let mut v: Value = strict_json::parse(&s)?;
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
                if req.version == 3 || ipc == "send_source_ai_request" {
                    conversation_store::dispatch(&ipc, req, fixture)
                } else {
                    repository::dispatch(&ipc, req, fixture)
                }
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
    // Only the fixed synthetic health inbox is processed while this App is running.
    let mut context = tauri::generate_context!();
    context.config_mut().app.windows[0].create = false;
    if std::env::var("LIFEOS_P3_149_VIEWPORT").ok().as_deref() == Some("narrow") {
        context.config_mut().app.windows[0].width = 700.0;
        context.config_mut().app.windows[0].height = 760.0;
    }
    let mut window_config = context.config().app.windows[0].clone();
    if runtime_root::is_real() {
        window_config.title = "LifeOS · 来源支撑的对话".into();
    }
    tauri::Builder::default()
        .setup(move |app| {
            let c = repository::open("app").map_err(|e| std::io::Error::other(e.code))?;
            source_store::init(&c).map_err(|e| std::io::Error::other(e.code))?;
            c.execute_batch("CREATE TABLE IF NOT EXISTS source_api_requests(id TEXT PRIMARY KEY,payload TEXT NOT NULL,result TEXT NOT NULL);CREATE TABLE IF NOT EXISTS source_runtime_errors(connector_id TEXT PRIMARY KEY,code TEXT NOT NULL);")?;
            drop(c);
            // S2 imports only on explicit user selection; no inbox polling.
            tauri::WebviewWindowBuilder::from_config(app, &window_config)?
                .initialization_script(format!(
                    "window.__LIFEOS_REAL_SOURCE__ = {};",
                    runtime_root::is_real()
                ))
                .devtools(!runtime_root::is_real())
                .incognito(runtime_root::is_real())
                .build()?;
            Ok(())
        })
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
            send_source_ai_request,
            connect_source_directory,
            control_source_job,
            get_source_status,
            authorize_source_target,
            get_source_evidence,
            import_apple_health_file
        ])
        .run(context)
        .expect("P3-149 app failed");
}
