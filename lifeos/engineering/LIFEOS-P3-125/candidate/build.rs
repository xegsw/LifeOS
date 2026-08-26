use std::env;
use std::fs;
use std::path::{Component, Path, PathBuf};

const ALLOWED_PARENT: &str = "/private/tmp/lifeos-p3-125-runtime-root-config-v1";

fn reject(message: &str) -> ! {
    panic!("LIFEOS_RUNTIME_ROOT rejected before build output: {message}");
}

fn real_directory(path: &Path) -> bool {
    match fs::symlink_metadata(path) {
        Ok(metadata) => metadata.file_type().is_dir() && !metadata.file_type().is_symlink(),
        Err(_) => false,
    }
}

fn no_linked_ancestor(path: &Path) -> bool {
    let mut current = PathBuf::new();
    for component in path.components() {
        match component {
            Component::RootDir => current.push(Path::new("/")),
            Component::Normal(name) => {
                current.push(name);
                if !real_directory(&current) {
                    return false;
                }
            }
            Component::CurDir | Component::ParentDir | Component::Prefix(_) => return false,
        }
    }
    true
}

fn frozen_runtime_root() -> PathBuf {
    let raw = env::var("LIFEOS_RUNTIME_ROOT")
        .unwrap_or_else(|_| reject("missing required build-time root"));
    if raw.is_empty() || raw.as_bytes().contains(&0) {
        reject("root is empty or contains a NUL byte");
    }
    let root = PathBuf::from(raw);
    if !root.is_absolute()
        || root
            .components()
            .any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_)))
    {
        reject("root must be an absolute normalized path");
    }
    let allowed_parent = Path::new(ALLOWED_PARENT);
    if !no_linked_ancestor(allowed_parent) || !no_linked_ancestor(&root) {
        reject("root or an ancestor is not a real directory");
    }
    let canonical_parent = fs::canonicalize(allowed_parent)
        .unwrap_or_else(|_| reject("authorized temporary parent cannot be canonicalized"));
    let canonical_root = fs::canonicalize(&root)
        .unwrap_or_else(|_| reject("root cannot be canonicalized"));
    if canonical_parent != allowed_parent || canonical_root != root || root.parent() != Some(allowed_parent) {
        reject("root must be a direct, canonical child of the frozen task temporary parent");
    }
    root
}

fn main() {
    let root = frozen_runtime_root();
    println!("cargo:rerun-if-env-changed=LIFEOS_RUNTIME_ROOT");
    println!("cargo:rustc-env=LIFEOS_RUNTIME_ROOT={}", root.display());
    tauri_build::build()
}
