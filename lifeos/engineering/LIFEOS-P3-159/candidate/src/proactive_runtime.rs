//! Native process-lifetime scheduler. No frontend visibility or permission claims.
use std::{ffi::c_void, sync::Arc, time::Duration};
use tauri::Manager;

#[link(name = "CoreGraphics", kind = "framework")]
unsafe extern "C" {
    fn CGSessionCopyCurrentDictionary() -> *const c_void;
}
#[link(name = "CoreFoundation", kind = "framework")]
unsafe extern "C" {
    fn CFDictionaryGetValue(dict: *const c_void, key: *const c_void) -> *const c_void;
    fn CFStringCreateWithCString(
        allocator: *const c_void,
        s: *const i8,
        encoding: u32,
    ) -> *const c_void;
    fn CFGetTypeID(v: *const c_void) -> usize;
    fn CFBooleanGetTypeID() -> usize;
    fn CFBooleanGetValue(v: *const c_void) -> bool;
    fn CFRelease(v: *const c_void);
}
fn unlocked_console() -> bool {
    // Public session API: https://developer.apple.com/documentation/coregraphics/cgsessioncopycurrentdictionary()
    // The additional lock flag is a conservative veto; native focus is also required.
    unsafe {
        let d = CGSessionCopyCurrentDictionary();
        if d.is_null() {
            return false;
        }
        let on_key = CFStringCreateWithCString(
            std::ptr::null(),
            c"kCGSSessionOnConsoleKey".as_ptr(),
            0x08000100,
        );
        if on_key.is_null() {
            CFRelease(d);
            return false;
        }
        let on = CFDictionaryGetValue(d, on_key);
        let key = CFStringCreateWithCString(
            std::ptr::null(),
            c"CGSSessionScreenIsLocked".as_ptr(),
            0x08000100,
        );
        if key.is_null() {
            CFRelease(d);
            return false;
        }
        let lock = CFDictionaryGetValue(d, key);
        let active =
            !on.is_null() && CFGetTypeID(on) == CFBooleanGetTypeID() && CFBooleanGetValue(on);
        let locked = !lock.is_null()
            && (CFGetTypeID(lock) != CFBooleanGetTypeID() || CFBooleanGetValue(lock));
        CFRelease(on_key);
        CFRelease(key);
        CFRelease(d);
        active && !locked
    }
}
pub(crate) fn foreground(app: &tauri::AppHandle) -> bool {
    app.get_webview_window("main").is_some_and(|w| {
        w.is_visible().unwrap_or(false)
            && w.is_focused().unwrap_or(false)
            && !w.is_minimized().unwrap_or(true)
    }) && unlocked_console()
}
pub fn start(app: tauri::AppHandle) {
    let store = Arc::clone(&app.state::<crate::State>().0);
    std::thread::spawn(move || {
        let mut was_visible = false;
        while app.get_webview_window("main").is_some() {
            let visible = foreground(&app);
            if visible && !was_visible {
                if let Ok(s) = store.try_lock() {
                    let _ = s.proactive_foreground();
                    was_visible = true;
                }
            }
            if !visible {
                was_visible = false;
            }
            let outcome = if crate::runtime_root::network_enabled() {
                crate::host_gateway::proactive_tick(
                    &store,
                    || foreground(&app),
                    &mut crate::provider_transport::DeepSeekModel,
                )
            } else {
                crate::host_gateway::proactive_tick(
                    &store,
                    || foreground(&app),
                    &mut crate::host_gateway::SyntheticControlledModel,
                )
            };
            // Only fixed codes/status are retained by the repository. Never log model/user text.
            let _ = outcome;
            std::thread::sleep(Duration::from_secs(1));
        }
    });
}
