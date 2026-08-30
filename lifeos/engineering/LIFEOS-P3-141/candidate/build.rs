use std::env;
use std::fs;
use std::path::{Component, Path, PathBuf};

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

fn frozen_runtime_root() -> (PathBuf, String) {
    let mode = env::var("LIFEOS_INPUT_MODE")
        .unwrap_or_else(|_| reject("missing required build-time input mode"));
    if mode != "synthetic" && mode != "real_self_use" {
        reject("input mode must be synthetic or real_self_use");
    }
    let phase_b_receipt = env::var("LIFEOS_P3_141_PHASE_B_RECEIPT").ok();
    if mode == "real_self_use"
        && phase_b_receipt.as_deref() != Some("LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS")
    {
        reject("phase_b_independent_pass_required before runtime-root inspection");
    }
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
    let parent = root.parent().unwrap_or_else(|| reject("root must have a parent"));
    if !no_linked_ancestor(parent) {
        reject("root parent or an ancestor is not a real directory");
    }
    if mode == "synthetic" || root.exists() {
        if !no_linked_ancestor(&root) {
            reject("root or an ancestor is not a real directory");
        }
        let canonical_root = fs::canonicalize(&root)
            .unwrap_or_else(|_| reject("root cannot be canonicalized"));
        if canonical_root != root {
            reject("root must be canonical without links or lexical normalization");
        }
    }
    (root, mode)
}

fn main() {
    let (root, mode) = frozen_runtime_root();
    println!("cargo:rerun-if-env-changed=LIFEOS_RUNTIME_ROOT");
    println!("cargo:rerun-if-env-changed=LIFEOS_INPUT_MODE");
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_B_RECEIPT");
    println!("cargo:rustc-env=LIFEOS_RUNTIME_ROOT={}", root.display());
    println!("cargo:rustc-env=LIFEOS_INPUT_MODE={mode}");
    if let Ok(receipt) = env::var("LIFEOS_P3_141_PHASE_B_RECEIPT") {
        println!("cargo:rustc-env=LIFEOS_P3_141_PHASE_B_RECEIPT={receipt}");
    }
    tauri_build::build()
}
