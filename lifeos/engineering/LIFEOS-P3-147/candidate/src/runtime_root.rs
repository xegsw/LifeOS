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
pub const ROOT: &str = env!("P3_147_COMPILED_ROOT");
pub const PROFILE: &str = env!("P3_147_COMPILED_PROFILE");
pub const CHILDREN: &[&str] = &["fixtures", ".runtime", "tmp", "artifacts"];
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
        .open(root.join(".lifeos-p3-147-owner.json"))
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
    for child in CHILDREN {
        directory(&root.join(child))?;
    }
    Ok(root.to_path_buf())
}
pub fn profile_info() -> Result<Value, Error> {
    policy::validate_environment(PROFILE).map_err(err)?;
    Ok(serde_json::json!({"profile":PROFILE,"root":ROOT}))
}
pub fn verify() -> Result<PathBuf, Error> {
    policy::validate_environment(PROFILE).map_err(err)?;
    verify_at(Path::new(ROOT), &policy::select(PROFILE).map_err(err)?)
}
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn exact_profiles_and_mixing_without_contact() {
        let e = policy::select("engineering").unwrap();
        let r = policy::select("independent-review").unwrap();
        for name in ["", "synthetic", "real", "../engineering", "/arbitrary/root"] {
            assert!(policy::select(name).is_err());
        }
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
        let marker = parent.join(".lifeos-p3-147-owner.json");
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
