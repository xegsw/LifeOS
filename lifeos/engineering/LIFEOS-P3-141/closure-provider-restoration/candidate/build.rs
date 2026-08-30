use serde::de::{self, DeserializeOwned, DeserializeSeed, MapAccess, SeqAccess, Visitor};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::env;
use std::fmt;
use std::fs;
use std::os::unix::fs::MetadataExt;
use std::path::{Component, Path, PathBuf};
use std::process::Command;

const TASK_ID: &str = "LIFEOS-P3-141";
const TASK_SHA256: &str = "88b0dbcafd525604b08ebb0dffc07dc360635666612c87a2cdc94e661e72ac5a";
const ABF_ID: &str = "ABF-P3-141-v1";
const ABF_SHA256: &str = "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2";
const RECEIPT_SCHEMA: &str = "lifeos.p3-141.phase-b-independent-pass-receipt.v1";
const MANIFEST_SCHEMA: &str = "lifeos.p3-141.phase-b-independent-manifest.v1";
const RECEIPT_FILE: &str = "phase_b_pass_receipt.json";
const REVIEW_MANIFEST_FILE: &str = "FINAL_MANIFEST.json";
const MAX_RECEIPT_BYTES: u64 = 16 * 1024;
const MAX_MANIFEST_BYTES: u64 = 1024 * 1024;

#[derive(Clone, Copy, PartialEq, Eq)]
enum BuildMode { SyntheticReview, PhaseCReal }

impl BuildMode {
    fn input_mode(self) -> &'static str {
        match self { Self::SyntheticReview => "synthetic", Self::PhaseCReal => "real_self_use" }
    }
    fn value(self) -> &'static str {
        match self { Self::SyntheticReview => "synthetic_review", Self::PhaseCReal => "phase_c_real" }
    }
}

fn reject(message: &str) -> ! {
    panic!("LIFEOS_P3_141_PHASE_B_GATE rejected before runtime-root inspection: {message}");
}

fn build_mode() -> BuildMode {
    // The legacy token is deliberately never an authorization mechanism.  A
    // caller that retains it is rejected rather than silently falling back.
    if env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT").is_some() {
        reject("legacy receipt string is prohibited; use an independently-owned receipt path only");
    }
    let build = env::var("LIFEOS_P3_141_BUILD_MODE")
        .unwrap_or_else(|_| reject("missing explicit LIFEOS_P3_141_BUILD_MODE"));
    let input = env::var("LIFEOS_INPUT_MODE")
        .unwrap_or_else(|_| reject("missing required build-time input mode"));
    match (build.as_str(), input.as_str()) {
        ("synthetic_review", "synthetic") => {
            if env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH").is_some() {
                reject("synthetic review builds may not consume a Phase B receipt");
            }
            BuildMode::SyntheticReview
        }
        ("phase_c_real", "real_self_use") => BuildMode::PhaseCReal,
        _ => reject("build mode and input mode must be the explicit approved pair"),
    }
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
                if !real_directory(&current) { return false; }
            }
            Component::CurDir | Component::ParentDir | Component::Prefix(_) => return false,
        }
    }
    true
}

fn normalized_absolute(raw: &str, what: &str) -> PathBuf {
    if raw.is_empty() || raw.as_bytes().contains(&0) { reject(&format!("{what} is empty or contains a NUL byte")); }
    let path = PathBuf::from(raw);
    if !path.is_absolute() || path.components().any(|part| matches!(part, Component::CurDir | Component::ParentDir | Component::Prefix(_))) {
        reject(&format!("{what} must be an absolute normalized path"));
    }
    path
}

fn frozen_runtime_root(build_mode: BuildMode) -> PathBuf {
    let raw = env::var("LIFEOS_RUNTIME_ROOT").unwrap_or_else(|_| reject("missing required build-time root"));
    let root = normalized_absolute(&raw, "runtime root");
    let parent = root.parent().unwrap_or_else(|| reject("root must have a parent"));
    if !no_linked_ancestor(parent) { reject("root parent or an ancestor is not a real directory"); }
    if build_mode == BuildMode::SyntheticReview || root.exists() {
        if !no_linked_ancestor(&root) { reject("root or an ancestor is not a real directory"); }
        let canonical_root = fs::canonicalize(&root).unwrap_or_else(|_| reject("root cannot be canonicalized"));
        if canonical_root != root { reject("root must be canonical without links or lexical normalization"); }
    }
    root
}

fn sha256_hex(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(bytes);
    format!("{:x}", hasher.finalize())
}

fn lowercase_hex(value: &str, len: usize) -> bool {
    value.len() == len && value.bytes().all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

fn safe_label(value: &str) -> bool {
    !value.is_empty() && value.len() <= 80 && value.bytes().all(|b| b.is_ascii_alphanumeric() || matches!(b, b'-' | b'_'))
}

fn readonly_regular(path: &Path, max: u64, what: &str) -> Vec<u8> {
    let meta = fs::symlink_metadata(path).unwrap_or_else(|_| reject(&format!("{what} is missing")));
    if !meta.file_type().is_file() || meta.file_type().is_symlink() || meta.nlink() != 1 || meta.mode() & 0o022 != 0 || meta.len() == 0 || meta.len() > max {
        reject(&format!("{what} must be one read-only regular non-linked file of bounded size"));
    }
    let parent = path.parent().unwrap_or_else(|| reject(&format!("{what} has no parent")));
    if !no_linked_ancestor(parent) { reject(&format!("{what} has a linked or non-directory ancestor")); }
    let canonical = fs::canonicalize(path).unwrap_or_else(|_| reject(&format!("{what} cannot be canonicalized")));
    if canonical != path { reject(&format!("{what} is not a canonical direct file")); }
    fs::read(path).unwrap_or_else(|_| reject(&format!("{what} cannot be read")))
}

// Receipt JSON must reject duplicate fields at every nesting level before the
// typed, deny-unknown-fields schema is applied. serde_json::Value alone would
// retain the last duplicate key and would be unsafe for an authorization gate.
struct NoDuplicateJson;
impl<'de> DeserializeSeed<'de> for NoDuplicateJson {
    type Value = ();
    fn deserialize<D: de::Deserializer<'de>>(self, deserializer: D) -> Result<(), D::Error> {
        deserializer.deserialize_any(NoDuplicateVisitor)
    }
}
struct NoDuplicateVisitor;
impl<'de> Visitor<'de> for NoDuplicateVisitor {
    type Value = ();
    fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result { f.write_str("JSON without duplicate object keys") }
    fn visit_bool<E: de::Error>(self, _: bool) -> Result<(), E> { Ok(()) }
    fn visit_i64<E: de::Error>(self, _: i64) -> Result<(), E> { Ok(()) }
    fn visit_u64<E: de::Error>(self, _: u64) -> Result<(), E> { Ok(()) }
    fn visit_f64<E: de::Error>(self, _: f64) -> Result<(), E> { Ok(()) }
    fn visit_str<E: de::Error>(self, _: &str) -> Result<(), E> { Ok(()) }
    fn visit_string<E: de::Error>(self, _: String) -> Result<(), E> { Ok(()) }
    fn visit_none<E: de::Error>(self) -> Result<(), E> { Ok(()) }
    fn visit_unit<E: de::Error>(self) -> Result<(), E> { Ok(()) }
    fn visit_seq<A: SeqAccess<'de>>(self, mut seq: A) -> Result<(), A::Error> {
        while let Some(()) = seq.next_element_seed(NoDuplicateJson)? {}
        Ok(())
    }
    fn visit_map<A: MapAccess<'de>>(self, mut map: A) -> Result<(), A::Error> {
        let mut keys = HashSet::new();
        while let Some(key) = map.next_key::<String>()? {
            if !keys.insert(key.clone()) { return Err(de::Error::custom(format!("duplicate JSON key: {key}"))); }
            map.next_value_seed(NoDuplicateJson)?;
        }
        Ok(())
    }
}

fn strict_json<T: DeserializeOwned>(bytes: &[u8], what: &str) -> T {
    let mut duplicate_check = serde_json::Deserializer::from_slice(bytes);
    NoDuplicateJson.deserialize(&mut duplicate_check).unwrap_or_else(|_| reject(&format!("{what} is malformed or contains duplicate fields")));
    duplicate_check.end().unwrap_or_else(|_| reject(&format!("{what} has trailing data")));
    serde_json::from_slice(bytes).unwrap_or_else(|_| reject(&format!("{what} fails the exact schema")))
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReviewIdentity { role: String, attempt_id: String }
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReviewManifestBinding { file: String, sha256: String, schema: String }
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct PassReceipt {
    schema: String,
    task_id: String,
    task_sha256: String,
    abf_id: String,
    abf_sha256: String,
    candidate_commit: String,
    candidate_tree_sha256: String,
    verdict: String,
    review_identity: ReviewIdentity,
    review_manifest: ReviewManifestBinding,
    issued_at_utc: String,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ReviewManifest {
    schema: String,
    task_id: String,
    review_identity: ReviewIdentity,
    review_conclusion: String,
    candidate_commit: String,
    candidate_tree_sha256: String,
    file_count_excluding_manifest: u64,
    tree_sha256_excluding_manifest: String,
    files: serde_json::Value,
}

fn git(top: &Path, args: &[&str], what: &str) -> Vec<u8> {
    let output = Command::new("git").arg("-C").arg(top).args(args).output().unwrap_or_else(|_| reject(&format!("cannot invoke git for {what}")));
    if !output.status.success() { reject(&format!("git validation failed for {what}")); }
    output.stdout
}

fn git_string(top: &Path, args: &[&str], what: &str) -> String {
    String::from_utf8(git(top, args, what)).unwrap_or_else(|_| reject(&format!("git output invalid for {what}"))).trim().to_owned()
}

fn git_top(path: &Path, what: &str) -> PathBuf {
    let raw = git_string(path, &["rev-parse", "--show-toplevel"], what);
    let top = normalized_absolute(&raw, what);
    if !no_linked_ancestor(&top) { reject(&format!("{what} is linked or not a real directory")); }
    let canonical = fs::canonicalize(&top).unwrap_or_else(|_| reject(&format!("{what} cannot be canonicalized")));
    if canonical != top { reject(&format!("{what} must be canonical")); }
    top
}

fn git_common_dir(top: &Path, what: &str) -> PathBuf {
    let raw = git_string(top, &["rev-parse", "--path-format=absolute", "--git-common-dir"], what);
    let common = normalized_absolute(&raw, what);
    if !no_linked_ancestor(&common) { reject(&format!("{what} is linked or not a real directory")); }
    common
}

fn declared_peer_worktree(candidate_top: &Path, review_top: &Path) -> bool {
    let listing = git_string(candidate_top, &["worktree", "list", "--porcelain"], "declared peer-worktree check");
    let needle = format!("worktree {}", review_top.display());
    listing.lines().any(|line| line == needle)
}

fn git_head_bytes(top: &Path, relative: &Path, what: &str) -> Vec<u8> {
    let rel = relative.to_str().unwrap_or_else(|| reject(&format!("{what} is not UTF-8")));
    git(top, &["show", &format!("HEAD:{rel}")], what)
}

fn candidate_tree_sha256(root: &Path) -> String {
    fn visit(root: &Path, current: &Path, files: &mut Vec<PathBuf>) {
        let entries = fs::read_dir(current).unwrap_or_else(|_| reject("candidate tree cannot be enumerated"));
        for entry in entries {
            let entry = entry.unwrap_or_else(|_| reject("candidate tree entry cannot be read"));
            let path = entry.path();
            let meta = fs::symlink_metadata(&path).unwrap_or_else(|_| reject("candidate tree metadata unavailable"));
            if meta.file_type().is_symlink() || (!meta.file_type().is_file() && !meta.file_type().is_dir()) { reject("candidate tree contains a non-regular or linked entry"); }
            if meta.file_type().is_dir() { visit(root, &path, files); }
            else { files.push(path.strip_prefix(root).unwrap_or_else(|_| reject("candidate tree relative path rejected")).to_path_buf()); }
        }
    }
    let mut files = Vec::new();
    visit(root, root, &mut files);
    files.sort();
    let mut hasher = Sha256::new();
    for relative in files {
        let text = relative.to_str().unwrap_or_else(|| reject("candidate path is not UTF-8"));
        let bytes = fs::read(root.join(&relative)).unwrap_or_else(|_| reject("candidate content cannot be read"));
        hasher.update((text.len() as u64).to_be_bytes());
        hasher.update(text.as_bytes());
        hasher.update((bytes.len() as u64).to_be_bytes());
        hasher.update(bytes);
    }
    format!("{:x}", hasher.finalize())
}

fn validate_phase_b_receipt() -> String {
    let raw = env::var("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH")
        .unwrap_or_else(|_| reject("phase_c_real requires an explicit independent receipt path before runtime-root inspection"));
    let receipt_path = normalized_absolute(&raw, "Phase B receipt path");
    if receipt_path.file_name().and_then(|value| value.to_str()) != Some(RECEIPT_FILE) { reject("receipt file name is not authorized"); }
    let receipt_bytes = readonly_regular(&receipt_path, MAX_RECEIPT_BYTES, "Phase B receipt");
    let attempt_dir = receipt_path.parent().unwrap_or_else(|| reject("receipt parent missing"));
    let review_root = attempt_dir.parent().unwrap_or_else(|| reject("receipt review root missing"));
    let task_review = review_root.parent().unwrap_or_else(|| reject("receipt task review root missing"));
    let reviews = task_review.parent().unwrap_or_else(|| reject("receipt reviews root missing"));
    let lifeos = reviews.parent().unwrap_or_else(|| reject("receipt lifeos root missing"));
    if review_root.file_name().and_then(|value| value.to_str()) != Some("independent-review")
        || task_review.file_name().and_then(|value| value.to_str()) != Some(TASK_ID)
        || reviews.file_name().and_then(|value| value.to_str()) != Some("reviews")
        || lifeos.file_name().and_then(|value| value.to_str()) != Some("lifeos")
        || !safe_label(attempt_dir.file_name().and_then(|value| value.to_str()).unwrap_or("")) {
        reject("receipt is not located in the authorized review-owned hierarchy");
    }
    let manifest_path = attempt_dir.join(REVIEW_MANIFEST_FILE);
    let manifest_bytes = readonly_regular(&manifest_path, MAX_MANIFEST_BYTES, "review manifest");
    let review_top = git_top(attempt_dir, "review ownership root");
    let candidate_root = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| reject("candidate root unavailable")));
    let candidate_top = git_top(&candidate_root, "candidate ownership root");
    if !git(&review_top, &["status", "--porcelain=v1", "--untracked-files=all"], "review mutable-history check").is_empty() {
        reject("review ownership worktree is mutable or dirty");
    }
    let receipt_relative = receipt_path.strip_prefix(&review_top).unwrap_or_else(|_| reject("receipt is outside review ownership root"));
    let manifest_relative = manifest_path.strip_prefix(&review_top).unwrap_or_else(|_| reject("manifest is outside review ownership root"));
    if git_head_bytes(&review_top, receipt_relative, "receipt HEAD content") != receipt_bytes
        || git_head_bytes(&review_top, manifest_relative, "manifest HEAD content") != manifest_bytes {
        reject("receipt or manifest differs from committed review history");
    }
    let receipt: PassReceipt = strict_json(&receipt_bytes, "Phase B receipt");
    let manifest: ReviewManifest = strict_json(&manifest_bytes, "review manifest");
    if receipt.schema != RECEIPT_SCHEMA || receipt.task_id != TASK_ID || receipt.task_sha256 != TASK_SHA256
        || receipt.abf_id != ABF_ID || receipt.abf_sha256 != ABF_SHA256 || receipt.verdict != "PASS" {
        reject("receipt task, ABF, schema, or Pass verdict binding rejected");
    }
    if receipt.review_identity.role != "independent_review" || receipt.review_identity.attempt_id != attempt_dir.file_name().and_then(|value| value.to_str()).unwrap_or("") {
        reject("receipt review identity rejected");
    }
    if receipt.review_manifest.file != REVIEW_MANIFEST_FILE || receipt.review_manifest.schema != MANIFEST_SCHEMA
        || receipt.review_manifest.sha256 != sha256_hex(&manifest_bytes) || !lowercase_hex(&receipt.review_manifest.sha256, 64) {
        reject("receipt review-manifest hash binding rejected");
    }
    if manifest.schema != MANIFEST_SCHEMA || manifest.task_id != TASK_ID || manifest.review_conclusion != "PASS"
        || manifest.review_identity.role != "independent_review" || manifest.review_identity.attempt_id != receipt.review_identity.attempt_id
        || manifest.candidate_commit != receipt.candidate_commit || manifest.candidate_tree_sha256 != receipt.candidate_tree_sha256
        || !lowercase_hex(&manifest.tree_sha256_excluding_manifest, 64) || !manifest.files.is_object() || manifest.file_count_excluding_manifest == 0 {
        reject("review manifest identity or Pass binding rejected");
    }
    if !lowercase_hex(&receipt.candidate_commit, 40) || !lowercase_hex(&receipt.candidate_tree_sha256, 64)
        || receipt.issued_at_utc.len() < 20 || receipt.issued_at_utc.len() > 35 || !receipt.issued_at_utc.is_ascii()
        || !receipt.issued_at_utc.contains('T') || !receipt.issued_at_utc.ends_with('Z') || receipt.issued_at_utc.contains(' ') {
        reject("receipt candidate binding or timestamp format rejected");
    }
    let candidate_commit = git_string(&candidate_top, &["rev-parse", "HEAD"], "candidate commit");
    if receipt.candidate_commit != candidate_commit { reject("receipt is stale or bound to a different candidate commit"); }
    let actual_tree = candidate_tree_sha256(&candidate_root);
    if receipt.candidate_tree_sha256 != actual_tree { reject("receipt is stale or bound to a different candidate tree"); }
    // Field semantics are checked above, but no syntactically correct receipt
    // becomes an authorization until it is also owned by a declared peer
    // review worktree of this repository.
    let review_common = git_common_dir(&review_top, "review Git common directory");
    let candidate_common = git_common_dir(&candidate_top, "candidate Git common directory");
    let same_owner = fs::metadata(&review_top).map(|meta| meta.uid()).ok() == fs::metadata(&candidate_top).map(|meta| meta.uid()).ok();
    if review_top == candidate_top || review_common != candidate_common || !declared_peer_worktree(&candidate_top, &review_top)
        || !same_owner || receipt_path.starts_with(&candidate_root) || !review_root.starts_with(&review_top) {
        reject("receipt is not independently owned outside the candidate tree");
    }
    sha256_hex(&receipt_bytes)
}

fn write_phase_b_binding(build_mode: BuildMode, binding: Option<String>) {
    let out = PathBuf::from(env::var("OUT_DIR").unwrap_or_else(|_| reject("OUT_DIR unavailable"))).join("phase_b_receipt_binding.rs");
    let source = match binding {
        Some(digest) => format!("const VALIDATED_PHASE_B_RECEIPT_SHA256: Option<&str> = Some(\"{digest}\");\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
        None => format!("const VALIDATED_PHASE_B_RECEIPT_SHA256: Option<&str> = None;\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
    };
    fs::write(out, source).unwrap_or_else(|_| reject("validated Phase B binding could not be written"));
}

fn main() {
    let build_mode = build_mode();
    // This happens before the runtime root is even parsed. Only phase_c_real
    // builds invoke the review-owned verifier; synthetic review remains an
    // explicitly separate, offline compilation mode.
    let binding = if build_mode == BuildMode::PhaseCReal { Some(validate_phase_b_receipt()) } else { None };
    let root = frozen_runtime_root(build_mode);
    write_phase_b_binding(build_mode, binding);
    println!("cargo:rerun-if-changed=ui");
    println!("cargo:rerun-if-changed=tauri.conf.json");
    println!("cargo:rerun-if-env-changed=LIFEOS_RUNTIME_ROOT");
    println!("cargo:rerun-if-env-changed=LIFEOS_INPUT_MODE");
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_BUILD_MODE");
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_B_RECEIPT");
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_B_RECEIPT_PATH");
    println!("cargo:rustc-env=LIFEOS_RUNTIME_ROOT={}", root.display());
    println!("cargo:rustc-env=LIFEOS_INPUT_MODE={}", build_mode.input_mode());
    tauri_build::build()
}
