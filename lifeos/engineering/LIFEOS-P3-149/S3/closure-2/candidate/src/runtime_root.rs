//! Sole filesystem authority. No arbitrary path or runtime profile switch.
use crate::repository::Error;
use serde_json::Value;
use std::{
    fs::{self, OpenOptions},
    io::Read,
    os::unix::fs::{MetadataExt, OpenOptionsExt, PermissionsExt},
    path::{Path, PathBuf},
};
#[path = "../root_profile.rs"]
mod policy;
#[cfg(not(test))]
pub const ROOT: &str = env!("P3_149_COMPILED_ROOT");
#[cfg(test)]
pub const ROOT: &str = if env!("P3_149_COMPILED_SOURCE").is_empty() {
    env!("P3_149_COMPILED_ROOT")
} else {
    "/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-2/fixtures/pilot-normal-v1"
};
pub const PROFILE: &str = env!("P3_149_COMPILED_PROFILE");
pub const CHILDREN: &[&str] = &["fixtures", ".runtime", "tmp", "artifacts"];
static ACTIVE: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);
static ACTIVATING: std::sync::Mutex<()> = std::sync::Mutex::new(());
pub fn is_real() -> bool {
    PROFILE == "source-pilot-1"
}
pub fn active() -> bool {
    !is_real() || ACTIVE.load(std::sync::atomic::Ordering::Acquire)
}
pub fn source_path() -> PathBuf {
    if is_real() {
        #[cfg(test)]
        return PathBuf::from("/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-2/fixtures/app-source");
        #[cfg(not(test))]
        return PathBuf::from(env!("P3_149_COMPILED_SOURCE"));
    }
    Path::new(ROOT).join("fixtures/app-source")
}
fn spec() -> Result<Value, Error> {
    let value = policy::select(PROFILE).map_err(err)?;
    #[cfg(test)]
    {
        let mut value = value;
        if is_real() {
            value["root"] = serde_json::json!(ROOT);
            value["marker"]["root"] = serde_json::json!(ROOT);
            value["marker"]["owner"] = serde_json::json!("pilot-normal-test");
        }
        return Ok(value);
    }
    #[cfg(not(test))]
    Ok(value)
}
pub fn activate_from_user_click() -> Result<(), Error> {
    if !is_real() {
        return Ok(());
    }
    policy::validate_environment(PROFILE).map_err(err)?;
    let _guard = ACTIVATING.lock().map_err(|_| err("activation_failed"))?;
    if active() {
        return Ok(());
    }
    // The reviewed real build may only verify the existing 147 marker, never
    // create a root, enumerate old assets, scan source paths, or migrate a DB.
    verify()?;
    ACTIVE.store(true, std::sync::atomic::Ordering::Release);
    Ok(())
}
pub fn helper(name: &str) -> Result<PathBuf, Error> {
    #[cfg(test)]
    if is_real() {
        return Ok(if name == "parse_source.py" {
            PathBuf::from(concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/tools/parse_source.py"
            ))
        } else {
            Path::new("/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-2").join(name)
        });
    }
    if is_real() {
        #[cfg(not(test))]
        {
            return std::env::current_exe()
                .ok()
                .and_then(|p| p.parent()?.parent().map(|p| p.join("Resources").join(name)))
                .ok_or_else(|| err("helper_unavailable"));
        }
    }
    Ok(if name == "parse_source.py" {
        PathBuf::from(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/tools/parse_source.py"
        ))
    } else {
        Path::new(env!("P3_149_COMPILED_ROOT")).join(name)
    })
}
fn err(s: &str) -> Error {
    Error::new(s)
}
fn directory(path: &Path) -> Result<(), Error> {
    let m = fs::symlink_metadata(path).map_err(|_| err("root_missing"))?;
    if !m.is_dir()
        || m.file_type().is_symlink()
        || m.uid() != unsafe { libc::getuid() }
        || m.permissions().mode() & 0o777 != 0o700
        || fs::canonicalize(path).map_err(|_| err("root_rejected"))? != path
    {
        return Err(err("root_rejected"));
    }
    Ok(())
}
fn verify_at(root: &Path, spec: &Value) -> Result<PathBuf, Error> {
    // Reject root/profile mixing before even lstat of the supplied path.
    if root.as_os_str()
        != spec["root"]
            .as_str()
            .ok_or_else(|| err("profile_rejected"))?
        || spec["marker"]["root"] != spec["root"]
    {
        return Err(err("profile_rejected"));
    }
    directory(root)?;
    let mut f = OpenOptions::new()
        .read(true)
        .custom_flags(libc::O_NOFOLLOW | libc::O_NONBLOCK | libc::O_CLOEXEC)
        .open(
            root.join(
                spec["markerFile"]
                    .as_str()
                    .unwrap_or(".lifeos-p3-149-owner.json"),
            ),
        )
        .map_err(|_| err("marker_missing"))?;
    let m = f.metadata().map_err(|_| err("marker_rejected"))?;
    if !m.is_file()
        || m.uid() != unsafe { libc::getuid() }
        || m.permissions().mode() & 0o777 != 0o600
        || m.len() > 4096
    {
        return Err(err("marker_rejected"));
    }
    let mut bytes = Vec::new();
    f.read_to_end(&mut bytes)
        .map_err(|_| err("marker_rejected"))?;
    let actual: Value = serde_json::from_slice(&bytes).map_err(|_| err("marker_rejected"))?;
    if actual != spec["marker"] {
        return Err(err("marker_rejected"));
    }
    for child in if is_real() { &[][..] } else { CHILDREN } {
        directory(&root.join(child))?;
    }
    Ok(root.to_path_buf())
}
pub fn expected_marker() -> Result<Value, Error> {
    Ok(spec()?["marker"].clone())
}
pub fn profile_info() -> Result<Value, Error> {
    policy::validate_environment(PROFILE).map_err(err)?;
    Ok(serde_json::json!({"profile":PROFILE,"root":ROOT}))
}
pub fn verify() -> Result<PathBuf, Error> {
    policy::validate_environment(PROFILE).map_err(err)?;
    verify_at(Path::new(ROOT), &spec()?)
}
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn pilot_normal_lifecycle() {
        if !is_real() {
            return;
        }
        // Test-only constants map BOTH source and output inside the engineering fixture root.
        assert!(ROOT.starts_with("/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-2/fixtures/"));
        assert!(source_path().starts_with("/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-2/fixtures/"));
        let call = |name: &str, payload: Value| {
            crate::source_api::dispatch(
                name,
                crate::source_api::Request {
                    version: 1,
                    payload,
                },
                "app",
            )
            .unwrap()
        };
        assert!(!active());
        assert_eq!(
            call("get_source_status", json!({}))["connectors"],
            json!([])
        );
        call(
            "connect_source_directory",
            json!({"requestId":format!("pilot-normal-connect-{}",std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos())}),
        );
        let done = || {
            for _ in 0..400 {
                let v = call("get_source_status", json!({}));
                let s = &v["connectors"][0];
                assert!(s["error"].is_null());
                if s["scanComplete"] == true && s["pending"] == 0 {
                    return s.clone();
                }
                std::thread::sleep(std::time::Duration::from_millis(100));
            }
            panic!("ordinary fixture timeout")
        };
        let status = done();
        assert_eq!(status["discovered"], 6);
        assert_eq!(status["parsed"], 3);
        let generation = status["grantGeneration"].clone();
        let control = |action: &str| {
            call(
                "control_source_job",
                json!({"requestId":format!("normal-{action}-{}",std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()),"connectorId":"directory","expectedGeneration":generation,"action":action}),
            )
        };
        control("pause");
        ACTIVE.store(false, std::sync::atomic::Ordering::Release);
        assert_eq!(
            call("get_source_status", json!({}))["connectors"],
            json!([])
        );
        call(
            "connect_source_directory",
            json!({"requestId":"pilot-normal-reopen"}),
        );
        assert_eq!(
            call("get_source_status", json!({}))["connectors"][0]["status"],
            "paused"
        );
        control("resume");
        done();
        let result = call(
            "get_source_evidence",
            json!({"mode":"search","connectorId":"directory","expectedGeneration":generation,"query":"项目计划"}),
        );
        assert!(!result["results"].as_array().unwrap().is_empty());
        control("refresh");
        done();
        control("disconnect");
        assert_eq!(
            call("get_source_status", json!({}))["connectors"],
            json!([])
        );
        assert_eq!(
            std::fs::metadata(Path::new(ROOT).join("capture.sqlite"))
                .unwrap()
                .permissions()
                .mode()
                & 0o777,
            0o600
        );
        println!("ordinary pilot fixture: lazy status, click initialization, six-file import, pause/reopen/resume, search, refresh, disconnect; no real roots contacted");
    }
    #[test]
    fn exact_profiles_and_mixing_without_contact() {
        let e = policy::select("engineering").unwrap();
        assert!(policy::select("independent-review").is_err());
        assert_eq!(e["root"], ROOT);
        for name in ["", "synthetic", "real", "../engineering", "/arbitrary/root"] {
            assert!(policy::select(name).is_err());
        }
        let mut r = e.clone();
        r["root"] = json!(Path::new(ROOT).join("fixtures/rejected-profile"));
        r["marker"]["root"] = r["root"].clone();
        // No filesystem call: mismatch exits before directory().
        assert_eq!(
            verify_at(Path::new(e["root"].as_str().unwrap()), &r)
                .unwrap_err()
                .code,
            "profile_rejected"
        );
        assert_eq!(
            verify_at(Path::new(r["root"].as_str().unwrap()), &e)
                .unwrap_err()
                .code,
            "profile_rejected"
        );
        assert_eq!(
            verify_at(Path::new("/arbitrary/root"), &e)
                .unwrap_err()
                .code,
            "profile_rejected"
        );
        assert_ne!(e["marker"], r["marker"]);
    }
    #[test]
    fn injected_root_marker_and_runtime_fail_closed() {
        // Injection is private to tests. Never use the actual review root.
        let parent = verify().unwrap().join("fixtures").join(format!(
            "root-authority-{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&parent).unwrap();
        fs::set_permissions(&parent, fs::Permissions::from_mode(0o700)).unwrap();
        let mut spec = policy::select(PROFILE).unwrap();
        spec["root"] = json!(parent);
        spec["marker"]["root"] = json!(parent);
        let marker = parent.join(".lifeos-p3-149-owner.json");
        assert_eq!(
            verify_at(&parent, &spec).unwrap_err().code,
            "marker_missing"
        );
        fs::write(&marker, b"{}").unwrap();
        fs::set_permissions(&marker, fs::Permissions::from_mode(0o600)).unwrap();
        assert_eq!(
            verify_at(&parent, &spec).unwrap_err().code,
            "marker_rejected"
        );
        fs::write(&marker, serde_json::to_vec(&spec["marker"]).unwrap()).unwrap();
        for child in CHILDREN {
            let p = parent.join(child);
            fs::create_dir(&p).unwrap();
            fs::set_permissions(p, fs::Permissions::from_mode(0o700)).unwrap();
        }
        assert!(verify_at(&parent, &spec).is_ok());
        for field in ["owner", "schema", "root"] {
            let mut bad = spec["marker"].clone();
            bad[field] = json!("wrong");
            fs::write(&marker, serde_json::to_vec(&bad).unwrap()).unwrap();
            assert_eq!(
                verify_at(&parent, &spec).unwrap_err().code,
                "marker_rejected"
            );
        }
        fs::write(&marker, serde_json::to_vec(&spec["marker"]).unwrap()).unwrap();
        fs::set_permissions(parent.join(".runtime"), fs::Permissions::from_mode(0o755)).unwrap();
        assert!(verify_at(&parent, &spec).is_err());
        fs::set_permissions(parent.join(".runtime"), fs::Permissions::from_mode(0o700)).unwrap();
        fs::remove_dir(parent.join("fixtures")).unwrap();
        std::os::unix::fs::symlink(parent.join("tmp"), parent.join("fixtures")).unwrap();
        assert!(verify_at(&parent, &spec).is_err());
        fs::remove_file(parent.join("fixtures")).unwrap();
        fs::create_dir(parent.join("fixtures")).unwrap();
        fs::set_permissions(parent.join("fixtures"), fs::Permissions::from_mode(0o700)).unwrap();
        assert!(verify_at(&parent, &spec).is_ok());
        fs::remove_dir_all(parent).unwrap();
    }
}

#[cfg(test)]
mod p149_e03_checks {
    use super::*;
    #[test]
    fn p149_e03_fixed_configuration_without_filesystem() {
        let e = policy::select("engineering").unwrap();
        assert!(policy::select("independent-review").is_err());
        assert_eq!(e["root"], ROOT);
        for name in [
            "",
            "synthetic",
            "real",
            "unknown",
            "../engineering",
            "/arbitrary/root",
        ] {
            assert!(policy::select(name).is_err());
        }
        assert!(matches!(PROFILE, "engineering" | "independent-review"));
        assert!(!is_real());
        assert_eq!(
            ROOT,
            policy::select(PROFILE).unwrap()["root"].as_str().unwrap()
        );
        assert_eq!(source_path(), Path::new(ROOT).join("fixtures/app-source"));
        assert_eq!(profile_info().unwrap()["profile"], PROFILE);
        // Pure policy and PathBuf assertions only: do not call verify/verify_at.
    }
}
