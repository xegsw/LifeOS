use serde::Deserialize;
use std::env;
use std::fs;
use std::os::unix::fs::{MetadataExt, PermissionsExt};
use std::path::{Component, Path, PathBuf};

const TASK_ID: &str = "LIFEOS-P3-141";
const BUILD_MODE: &str = "revision_3_synthetic";
const AUTHORIZED_ROOT_ENV: &str = "LIFEOS_P3_141_AUTHORIZED_SYNTHETIC_ROOT";
const RUNTIME_ROOT_ENV: &str = "LIFEOS_RUNTIME_ROOT";
const AUTHORIZED_ROOT_MARKER: &str = ".lifeos-p3-141-authorized-synthetic-root.json";
const AUTHORIZED_ROOT_SCHEMA: &str = "lifeos.p3-141.authorized-synthetic-root.v1";
const AUTHORIZED_ROOT_OWNER: &str = "lifeos-p3-141-revision-3-synthetic-root-authority";

#[derive(Debug, Deserialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
struct AuthorizedSyntheticRootMarker {
    schema: String,
    task_id: String,
    authorized_root: String,
    mode: String,
    owner: String,
}

fn reject(message: &str) -> ! {
    panic!("{TASK_ID} Revision-3 synthetic build rejected before runtime contact: {message}");
}

fn real_directory(path: &Path) -> bool {
    let Ok(metadata) = fs::symlink_metadata(path) else { return false; };
    metadata.file_type().is_dir()
        && !metadata.file_type().is_symlink()
        && fs::canonicalize(path).map(|resolved| resolved == path).unwrap_or(false)
}

fn direct_real_ancestors(path: &Path) -> bool {
    let mut current = PathBuf::new();
    for component in path.components() {
        match component {
            Component::RootDir => current.push(Path::new("/")),
            Component::Normal(name) => {
                current.push(name);
                if !real_directory(&current) { return false; }
            }
            Component::CurDir | Component::ParentDir | Component::Prefix(_) => return false,
        }
    }
    true
}

fn normalized_absolute(raw: &str, subject: &str) -> PathBuf {
    if raw.is_empty() || raw.as_bytes().contains(&0) { reject(&format!("{subject} is empty or contains a NUL byte")); }
    let path = PathBuf::from(raw);
    if !path.is_absolute() || path.components().any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_))) {
        reject(&format!("{subject} must be absolute and normalized"));
    }
    path
}

fn allowed_authorized_root_name(name: &str) -> bool {
    let Some(suffix) = name.strip_prefix("lifeos-p3-141-revision-3-") else { return false; };
    let Some((kind, run)) = suffix.split_once('-') else { return false; };
    if !matches!(kind, "engineering" | "independent" | "root") { return false; }
    let valid_run = !run.is_empty()
        && run.len() <= 72
        && !run.starts_with('-')
        && !run.ends_with('-')
        && !run.contains("--")
        && run.bytes().all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'-');
    match kind {
        "engineering" => valid_run && (run.starts_with("closure-") || run == "bundle-lineage-v1"),
        "independent" => valid_run && run.starts_with("review-"),
        "root" => valid_run && run.starts_with("authority-"),
        _ => false,
    }
}

fn validate_authorized_root(root: &Path) {
    if root.parent() != Some(Path::new("/private/tmp")) || !direct_real_ancestors(root) {
        reject("authorized synthetic root must be a direct real child of /private/tmp");
    }
    let name = root.file_name().and_then(|part| part.to_str()).unwrap_or_else(|| reject("authorized synthetic root name is invalid"));
    if !allowed_authorized_root_name(name) { reject("authorized synthetic root name is outside the strict P3-141 Revision-3 format"); }
    let metadata = fs::symlink_metadata(root).unwrap_or_else(|_| reject("authorized synthetic root is unavailable"));
    if !metadata.file_type().is_dir() || metadata.file_type().is_symlink() || metadata.permissions().mode() & 0o777 != 0o700 || fs::canonicalize(root).map(|resolved| resolved != root).unwrap_or(true) {
        reject("authorized synthetic root must be a canonical 0700 non-symlink directory");
    }
    let marker_path = root.join(AUTHORIZED_ROOT_MARKER);
    let marker_metadata = fs::symlink_metadata(&marker_path).unwrap_or_else(|_| reject("authorized synthetic root marker is missing"));
    if !marker_metadata.file_type().is_file() || marker_metadata.file_type().is_symlink() || marker_metadata.nlink() != 1 || marker_metadata.permissions().mode() & 0o777 != 0o600 {
        reject("authorized synthetic root marker must be a 0600 ordinary non-symlink file");
    }
    let marker: AuthorizedSyntheticRootMarker = serde_json::from_slice(&fs::read(&marker_path).unwrap_or_else(|_| reject("authorized synthetic root marker is unreadable")))
        .unwrap_or_else(|_| reject("authorized synthetic root marker schema is invalid"));
    let expected = AuthorizedSyntheticRootMarker {
        schema: AUTHORIZED_ROOT_SCHEMA.into(), task_id: TASK_ID.into(), authorized_root: root.display().to_string(),
        mode: BUILD_MODE.into(), owner: AUTHORIZED_ROOT_OWNER.into(),
    };
    if marker != expected { reject("authorized synthetic root marker does not bind this exact task root"); }
}

fn main() {
    if env::var("LIFEOS_P3_141_BUILD_MODE").ok().as_deref() != Some(BUILD_MODE)
        || env::var("LIFEOS_INPUT_MODE").ok().as_deref() != Some("synthetic") {
        reject("only the explicit Revision-3 synthetic build mode is permitted");
    }
    for prohibited in ["LIFEOS_P3_141_PHASE_B_RECEIPT", "LIFEOS_P3_141_PHASE_B_RECEIPT_PATH", "LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH"] {
        if env::var_os(prohibited).is_some() { reject("legacy Phase-B/Phase-C receipt inputs are prohibited"); }
    }
    let authorized_root = normalized_absolute(&env::var(AUTHORIZED_ROOT_ENV).unwrap_or_else(|_| reject("missing required task-scoped authorized synthetic root")), "authorized synthetic root");
    let runtime_root = normalized_absolute(&env::var(RUNTIME_ROOT_ENV).unwrap_or_else(|_| reject("missing required runtime root")), "runtime root");
    println!("cargo:rerun-if-changed={}", authorized_root.join(AUTHORIZED_ROOT_MARKER).display());
    validate_authorized_root(&authorized_root);
    if runtime_root.parent() != Some(authorized_root.as_path()) || runtime_root.file_name() != Some(std::ffi::OsStr::new("runtime")) || !direct_real_ancestors(&runtime_root) {
        reject("runtime root must be the direct real runtime child of this authorized synthetic root");
    }
    let runtime_metadata = fs::symlink_metadata(&runtime_root).unwrap_or_else(|_| reject("runtime root is unavailable"));
    if !runtime_metadata.file_type().is_dir() || runtime_metadata.file_type().is_symlink() || runtime_metadata.permissions().mode() & 0o777 != 0o700 || fs::canonicalize(&runtime_root).map(|resolved| resolved != runtime_root).unwrap_or(true) {
        reject("runtime root must be a canonical 0700 non-symlink directory");
    }
    let output = PathBuf::from(env::var("OUT_DIR").unwrap_or_else(|_| reject("OUT_DIR unavailable"))).join("revision_3_synthetic_binding.rs");
    let binding = format!(
        "pub const COMPILED_BUILD_MODE: &str = {};\npub const COMPILED_RUNTIME_ROOT: &str = {};\npub const COMPILED_AUTHORIZED_SYNTHETIC_ROOT: &str = {};\n",
        serde_json::to_string(BUILD_MODE).unwrap(), serde_json::to_string(&runtime_root.display().to_string()).unwrap(), serde_json::to_string(&authorized_root.display().to_string()).unwrap(),
    );
    fs::write(output, binding).unwrap_or_else(|_| reject("synthetic binding could not be written"));
    println!("cargo:rerun-if-changed=ui");
    for name in [RUNTIME_ROOT_ENV, AUTHORIZED_ROOT_ENV, "LIFEOS_INPUT_MODE", "LIFEOS_P3_141_BUILD_MODE"] { println!("cargo:rerun-if-env-changed={name}"); }
    tauri_build::build();
}
