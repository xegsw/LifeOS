#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
mod repository {
    #[derive(Debug,serde::Serialize)] pub struct Error{pub code:String}
    impl Error{pub fn new(s:&str)->Self{Self{code:s.into()}}}
    impl From<rusqlite::Error> for Error{fn from(_:rusqlite::Error)->Self{Self::new("readonly_query_failed")}}
}
mod strict_json;
mod health_reader;
use repository::Error;
use std::{sync::Mutex,io::Write,os::fd::FromRawFd};
use tauri::Manager;
struct State(Mutex<health_reader::Reader>);
#[tauri::command]
async fn get_today(request:tauri::ipc::Request<'_>,app:tauri::AppHandle)->Result<serde_json::Value,Error>{
    let body=request.body().clone();
    tauri::async_runtime::spawn_blocking(move||{let state=app.state::<State>();let reader=state.0.try_lock().map_err(|_|Error::new("readonly_busy"))?;reader.dispatch(body)}).await.map_err(|_|Error::new("readonly_query_failed"))?
}
fn main(){
    std::panic::set_hook(Box::new(|_|{}));unsafe{libc::umask(0o077);let lim=libc::rlimit{rlim_cur:0,rlim_max:0};libc::setrlimit(libc::RLIMIT_CORE,&lim);}
    let out=unsafe{libc::dup(1)};if out>=0{unsafe{libc::fcntl(out,libc::F_SETFD,libc::FD_CLOEXEC);}}
    unsafe{let f=libc::open(c"/dev/null".as_ptr(),libc::O_RDWR);if f>=0{libc::dup2(f,0);libc::dup2(f,1);libc::dup2(f,2);if f>2{libc::close(f);}}}
    let real=env!("P3_150_MODE")=="real";
    let path=if real{"/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite"}else{"/private/tmp/lifeos-p3-150-health-view-v1/synthetic/health-import.sqlite"};
    let reader=match health_reader::Reader::open(std::path::Path::new(path)){Ok(r)=>r,Err(e)=>{if out>=0{let mut o=unsafe{std::fs::File::from_raw_fd(out)};let _=writeln!(o,"{{\"status\":\"failed\",\"code\":\"{}\"}}",e.code);}return;}};
    let title=if real{"LifeOS P3-150 - Health Readonly"}else{"LifeOS P3-150 - Synthetic Readonly"};
    let builder=tauri::Builder::default().manage(State(Mutex::new(reader))).invoke_handler(tauri::generate_handler![get_today]).setup(move|app|{
        tauri::WebviewWindowBuilder::new(app,"main",tauri::WebviewUrl::App("index.html".into())).title(title).inner_size(1280.0,949.0).min_inner_size(560.0,640.0).incognito(true).initialization_script(if real{"window.__HEALTH_REAL_READONLY__=true;"}else{"window.__HEALTH_REAL_READONLY__=false;"}).build()?;
        if out>=0{let mut o=unsafe{std::fs::File::from_raw_fd(out)};let _=writeln!(o,"{{\"status\":\"readonly_view_started\",\"mode\":\"{}\"}}",if real{"real"}else{"synthetic"});}
        Ok(())
    });
    let _=builder.run(tauri::generate_context!());
}
