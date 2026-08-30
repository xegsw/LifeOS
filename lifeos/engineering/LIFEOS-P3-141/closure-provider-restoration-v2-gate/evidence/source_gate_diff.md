# Revision-2 Phase-C gate source diff
Base: commit 48a26320646219117b28e81cd77dd6c8206fe99c. Allowed changes are the v2 build/receipt gate, its runtime binding name/error, and one gate test module.
## build.rs
--- /private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1/base-build.rs	2026-08-30 18:14:03
+++ candidate/build.rs	2026-08-30 18:13:13
@@ -10,12 +10,13 @@
 use std::process::Command;
 
 const TASK_ID: &str = "LIFEOS-P3-141";
-const TASK_SHA256: &str = "88b0dbcafd525604b08ebb0dffc07dc360635666612c87a2cdc94e661e72ac5a";
-const ABF_ID: &str = "ABF-P3-141-v1";
-const ABF_SHA256: &str = "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2";
-const RECEIPT_SCHEMA: &str = "lifeos.p3-141.phase-b-independent-pass-receipt.v1";
-const MANIFEST_SCHEMA: &str = "lifeos.p3-141.phase-b-independent-manifest.v1";
-const RECEIPT_FILE: &str = "phase_b_pass_receipt.json";
+const TASK_SHA256: &str = "c97419a1818e0aa6fe6fc61c487e3ef97746e199b2c7d22435d8c05090374800";
+const FIXED_INPUT_INVENTORY_SHA256: &str = "3651e046da8211f06bf5144a155a0505b7ddfbaab67a249e51d94aeae09861a5";
+const ABF_ID: &str = "ABF-P3-141-v2";
+const ABF_SHA256: &str = "096ad12beec63b78aaa3be92535b4a6ea632cdc4235c1d83f224db955d5dc9ea";
+const RECEIPT_SCHEMA: &str = "lifeos.p3-141.phase-c-independent-pass-receipt.v2";
+const MANIFEST_SCHEMA: &str = "lifeos.p3-141.independent-review-manifest.v2";
+const RECEIPT_FILE: &str = "phase_c_v2_independent_pass_receipt.json";
 const REVIEW_MANIFEST_FILE: &str = "FINAL_MANIFEST.json";
 const MAX_RECEIPT_BYTES: u64 = 16 * 1024;
 const MAX_MANIFEST_BYTES: u64 = 1024 * 1024;
@@ -33,14 +34,15 @@
 }
 
 fn reject(message: &str) -> ! {
-    panic!("LIFEOS_P3_141_PHASE_B_GATE rejected before runtime-root inspection: {message}");
+    panic!("LIFEOS_P3_141_PHASE_C_V2_GATE rejected before runtime-root inspection: {message}");
 }
 
 fn build_mode() -> BuildMode {
     // The legacy token is deliberately never an authorization mechanism.  A
     // caller that retains it is rejected rather than silently falling back.
-    if env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT").is_some() {
-        reject("legacy receipt string is prohibited; use an independently-owned receipt path only");
+    if env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT").is_some()
+        || env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH").is_some() {
+        reject("legacy Phase-B receipt inputs are prohibited; use the v2 independently-owned receipt path only");
     }
     let build = env::var("LIFEOS_P3_141_BUILD_MODE")
         .unwrap_or_else(|_| reject("missing explicit LIFEOS_P3_141_BUILD_MODE"));
@@ -48,8 +50,8 @@
         .unwrap_or_else(|_| reject("missing required build-time input mode"));
     match (build.as_str(), input.as_str()) {
         ("synthetic_review", "synthetic") => {
-            if env::var_os("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH").is_some() {
-                reject("synthetic review builds may not consume a Phase B receipt");
+            if env::var_os("LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH").is_some() {
+                reject("synthetic review builds may not consume a Phase-C v2 receipt");
             }
             BuildMode::SyntheticReview
         }
@@ -183,6 +185,7 @@
     schema: String,
     task_id: String,
     task_sha256: String,
+    fixed_input_inventory_sha256: String,
     abf_id: String,
     abf_sha256: String,
     candidate_commit: String,
@@ -197,6 +200,10 @@
 struct ReviewManifest {
     schema: String,
     task_id: String,
+    task_sha256: String,
+    fixed_input_inventory_sha256: String,
+    abf_id: String,
+    abf_sha256: String,
     review_identity: ReviewIdentity,
     review_conclusion: String,
     candidate_commit: String,
@@ -270,12 +277,36 @@
     format!("{:x}", hasher.finalize())
 }
 
-fn validate_phase_b_receipt() -> String {
-    let raw = env::var("LIFEOS_P3_141_PHASE_B_RECEIPT_PATH")
-        .unwrap_or_else(|_| reject("phase_c_real requires an explicit independent receipt path before runtime-root inspection"));
-    let receipt_path = normalized_absolute(&raw, "Phase B receipt path");
+fn validate_revision_2_binding(receipt: &PassReceipt, manifest: &ReviewManifest, candidate_commit: &str, candidate_tree: &str) {
+    if receipt.schema != RECEIPT_SCHEMA || receipt.task_id != TASK_ID || receipt.task_sha256 != TASK_SHA256
+        || receipt.fixed_input_inventory_sha256 != FIXED_INPUT_INVENTORY_SHA256
+        || receipt.abf_id != ABF_ID || receipt.abf_sha256 != ABF_SHA256 || receipt.verdict != "PASS" {
+        reject("receipt Revision-2 task, inventory, ABF, schema, or Pass verdict binding rejected");
+    }
+    if manifest.schema != MANIFEST_SCHEMA || manifest.task_id != TASK_ID || manifest.task_sha256 != TASK_SHA256
+        || manifest.fixed_input_inventory_sha256 != FIXED_INPUT_INVENTORY_SHA256
+        || manifest.abf_id != ABF_ID || manifest.abf_sha256 != ABF_SHA256 || manifest.review_conclusion != "PASS"
+        || manifest.review_identity.role != "independent_review" || manifest.review_identity.attempt_id != receipt.review_identity.attempt_id
+        || manifest.candidate_commit != receipt.candidate_commit || manifest.candidate_tree_sha256 != receipt.candidate_tree_sha256
+        || !lowercase_hex(&manifest.tree_sha256_excluding_manifest, 64) || !manifest.files.is_object() || manifest.file_count_excluding_manifest == 0 {
+        reject("review manifest is not the exact Revision-2 independent Pass binding");
+    }
+    if !lowercase_hex(&receipt.candidate_commit, 40) || !lowercase_hex(&receipt.candidate_tree_sha256, 64)
+        || receipt.issued_at_utc.len() < 20 || receipt.issued_at_utc.len() > 35 || !receipt.issued_at_utc.is_ascii()
+        || !receipt.issued_at_utc.contains('T') || !receipt.issued_at_utc.ends_with('Z') || receipt.issued_at_utc.contains(' ') {
+        reject("receipt candidate binding or timestamp format rejected");
+    }
+    if receipt.candidate_commit != candidate_commit || receipt.candidate_tree_sha256 != candidate_tree {
+        reject("receipt is stale or bound to a different Revision-2 candidate");
+    }
+}
+
+fn validate_phase_c_v2_receipt() -> String {
+    let raw = env::var("LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH")
+        .unwrap_or_else(|_| reject("phase_c_real requires an explicit v2 independent receipt path before runtime-root inspection"));
+    let receipt_path = normalized_absolute(&raw, "Phase-C v2 receipt path");
     if receipt_path.file_name().and_then(|value| value.to_str()) != Some(RECEIPT_FILE) { reject("receipt file name is not authorized"); }
-    let receipt_bytes = readonly_regular(&receipt_path, MAX_RECEIPT_BYTES, "Phase B receipt");
+    let receipt_bytes = readonly_regular(&receipt_path, MAX_RECEIPT_BYTES, "Phase-C v2 receipt");
     let attempt_dir = receipt_path.parent().unwrap_or_else(|| reject("receipt parent missing"));
     let review_root = attempt_dir.parent().unwrap_or_else(|| reject("receipt review root missing"));
     let task_review = review_root.parent().unwrap_or_else(|| reject("receipt task review root missing"));
@@ -296,18 +327,17 @@
     if !git(&review_top, &["status", "--porcelain=v1", "--untracked-files=all"], "review mutable-history check").is_empty() {
         reject("review ownership worktree is mutable or dirty");
     }
+    if !git(&candidate_top, &["status", "--porcelain=v1", "--untracked-files=all"], "candidate mutable-history check").is_empty() {
+        reject("candidate ownership worktree is mutable or dirty");
+    }
     let receipt_relative = receipt_path.strip_prefix(&review_top).unwrap_or_else(|_| reject("receipt is outside review ownership root"));
     let manifest_relative = manifest_path.strip_prefix(&review_top).unwrap_or_else(|_| reject("manifest is outside review ownership root"));
     if git_head_bytes(&review_top, receipt_relative, "receipt HEAD content") != receipt_bytes
         || git_head_bytes(&review_top, manifest_relative, "manifest HEAD content") != manifest_bytes {
         reject("receipt or manifest differs from committed review history");
     }
-    let receipt: PassReceipt = strict_json(&receipt_bytes, "Phase B receipt");
+    let receipt: PassReceipt = strict_json(&receipt_bytes, "Phase-C v2 receipt");
     let manifest: ReviewManifest = strict_json(&manifest_bytes, "review manifest");
-    if receipt.schema != RECEIPT_SCHEMA || receipt.task_id != TASK_ID || receipt.task_sha256 != TASK_SHA256
-        || receipt.abf_id != ABF_ID || receipt.abf_sha256 != ABF_SHA256 || receipt.verdict != "PASS" {
-        reject("receipt task, ABF, schema, or Pass verdict binding rejected");
-    }
     if receipt.review_identity.role != "independent_review" || receipt.review_identity.attempt_id != attempt_dir.file_name().and_then(|value| value.to_str()).unwrap_or("") {
         reject("receipt review identity rejected");
     }
@@ -315,21 +345,9 @@
         || receipt.review_manifest.sha256 != sha256_hex(&manifest_bytes) || !lowercase_hex(&receipt.review_manifest.sha256, 64) {
         reject("receipt review-manifest hash binding rejected");
     }
-    if manifest.schema != MANIFEST_SCHEMA || manifest.task_id != TASK_ID || manifest.review_conclusion != "PASS"
-        || manifest.review_identity.role != "independent_review" || manifest.review_identity.attempt_id != receipt.review_identity.attempt_id
-        || manifest.candidate_commit != receipt.candidate_commit || manifest.candidate_tree_sha256 != receipt.candidate_tree_sha256
-        || !lowercase_hex(&manifest.tree_sha256_excluding_manifest, 64) || !manifest.files.is_object() || manifest.file_count_excluding_manifest == 0 {
-        reject("review manifest identity or Pass binding rejected");
-    }
-    if !lowercase_hex(&receipt.candidate_commit, 40) || !lowercase_hex(&receipt.candidate_tree_sha256, 64)
-        || receipt.issued_at_utc.len() < 20 || receipt.issued_at_utc.len() > 35 || !receipt.issued_at_utc.is_ascii()
-        || !receipt.issued_at_utc.contains('T') || !receipt.issued_at_utc.ends_with('Z') || receipt.issued_at_utc.contains(' ') {
-        reject("receipt candidate binding or timestamp format rejected");
-    }
     let candidate_commit = git_string(&candidate_top, &["rev-parse", "HEAD"], "candidate commit");
-    if receipt.candidate_commit != candidate_commit { reject("receipt is stale or bound to a different candidate commit"); }
     let actual_tree = candidate_tree_sha256(&candidate_root);
-    if receipt.candidate_tree_sha256 != actual_tree { reject("receipt is stale or bound to a different candidate tree"); }
+    validate_revision_2_binding(&receipt, &manifest, &candidate_commit, &actual_tree);
     // Field semantics are checked above, but no syntactically correct receipt
     // becomes an authorization until it is also owned by a declared peer
     // review worktree of this repository.
@@ -343,23 +361,24 @@
     sha256_hex(&receipt_bytes)
 }
 
-fn write_phase_b_binding(build_mode: BuildMode, binding: Option<String>) {
-    let out = PathBuf::from(env::var("OUT_DIR").unwrap_or_else(|_| reject("OUT_DIR unavailable"))).join("phase_b_receipt_binding.rs");
+fn write_phase_c_v2_binding(build_mode: BuildMode, binding: Option<String>) {
+    let out = PathBuf::from(env::var("OUT_DIR").unwrap_or_else(|_| reject("OUT_DIR unavailable"))).join("phase_c_v2_receipt_binding.rs");
     let source = match binding {
-        Some(digest) => format!("const VALIDATED_PHASE_B_RECEIPT_SHA256: Option<&str> = Some(\"{digest}\");\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
-        None => format!("const VALIDATED_PHASE_B_RECEIPT_SHA256: Option<&str> = None;\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
+        Some(digest) => format!("const VALIDATED_PHASE_C_V2_RECEIPT_SHA256: Option<&str> = Some(\"{digest}\");\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
+        None => format!("const VALIDATED_PHASE_C_V2_RECEIPT_SHA256: Option<&str> = None;\nconst COMPILED_BUILD_MODE: &str = \"{}\";\n", build_mode.value()),
     };
-    fs::write(out, source).unwrap_or_else(|_| reject("validated Phase B binding could not be written"));
+    fs::write(out, source).unwrap_or_else(|_| reject("validated Phase-C v2 binding could not be written"));
 }
 
+#[cfg(not(test))]
 fn main() {
     let build_mode = build_mode();
     // This happens before the runtime root is even parsed. Only phase_c_real
     // builds invoke the review-owned verifier; synthetic review remains an
     // explicitly separate, offline compilation mode.
-    let binding = if build_mode == BuildMode::PhaseCReal { Some(validate_phase_b_receipt()) } else { None };
+    let binding = if build_mode == BuildMode::PhaseCReal { Some(validate_phase_c_v2_receipt()) } else { None };
     let root = frozen_runtime_root(build_mode);
-    write_phase_b_binding(build_mode, binding);
+    write_phase_c_v2_binding(build_mode, binding);
     println!("cargo:rerun-if-changed=ui");
     println!("cargo:rerun-if-changed=tauri.conf.json");
     println!("cargo:rerun-if-env-changed=LIFEOS_RUNTIME_ROOT");
@@ -367,7 +386,96 @@
     println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_BUILD_MODE");
     println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_B_RECEIPT");
     println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_B_RECEIPT_PATH");
+    println!("cargo:rerun-if-env-changed=LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH");
     println!("cargo:rustc-env=LIFEOS_RUNTIME_ROOT={}", root.display());
     println!("cargo:rustc-env=LIFEOS_INPUT_MODE={}", build_mode.input_mode());
     tauri_build::build()
 }
+
+#[cfg(test)]
+mod revision_2_gate_tests {
+    use super::*;
+    use std::panic::{catch_unwind, AssertUnwindSafe};
+    use std::os::unix::fs::{symlink, PermissionsExt};
+
+    fn receipt() -> PassReceipt {
+        PassReceipt {
+            schema: RECEIPT_SCHEMA.into(), task_id: TASK_ID.into(), task_sha256: TASK_SHA256.into(),
+            fixed_input_inventory_sha256: FIXED_INPUT_INVENTORY_SHA256.into(), abf_id: ABF_ID.into(), abf_sha256: ABF_SHA256.into(),
+            candidate_commit: "a".repeat(40), candidate_tree_sha256: "b".repeat(64), verdict: "PASS".into(),
+            review_identity: ReviewIdentity { role: "independent_review".into(), attempt_id: "provider-restoration-v2-gate".into() },
+            review_manifest: ReviewManifestBinding { file: REVIEW_MANIFEST_FILE.into(), sha256: "c".repeat(64), schema: MANIFEST_SCHEMA.into() },
+            issued_at_utc: "2026-08-30T00:00:00Z".into(),
+        }
+    }
+
+    fn manifest() -> ReviewManifest {
+        ReviewManifest {
+            schema: MANIFEST_SCHEMA.into(), task_id: TASK_ID.into(), task_sha256: TASK_SHA256.into(),
+            fixed_input_inventory_sha256: FIXED_INPUT_INVENTORY_SHA256.into(), abf_id: ABF_ID.into(), abf_sha256: ABF_SHA256.into(),
+            review_identity: ReviewIdentity { role: "independent_review".into(), attempt_id: "provider-restoration-v2-gate".into() },
+            review_conclusion: "PASS".into(), candidate_commit: "a".repeat(40), candidate_tree_sha256: "b".repeat(64),
+            file_count_excluding_manifest: 1, tree_sha256_excluding_manifest: "d".repeat(64), files: serde_json::json!({"synthetic": true}),
+        }
+    }
+
+    fn rejected(f: impl FnOnce()) {
+        assert!(catch_unwind(AssertUnwindSafe(f)).is_err());
+    }
+
+    #[test]
+    fn v2_receipt_contract_accepts_exact_revision_2_binding() {
+        validate_revision_2_binding(&receipt(), &manifest(), &"a".repeat(40), &"b".repeat(64));
+    }
+
+    #[test]
+    fn v2_receipt_contract_rejects_v1_mixed_stale_and_nonpass_bindings() {
+        let cases: Vec<Box<dyn Fn(&mut PassReceipt, &mut ReviewManifest)>> = vec![
+            Box::new(|r, _| r.abf_id = "ABF-P3-141-v1".into()),
+            Box::new(|r, _| r.abf_sha256 = "ff05a7a4b52ceef0a4325294cabbfe5ad91c131160d8b9c123bd8fa59fd5c8b2".into()),
+            Box::new(|r, _| r.task_sha256 = "88b0dbcafd525604b08ebb0dffc07dc360635666612c87a2cdc94e661e72ac5a".into()),
+            Box::new(|r, _| r.fixed_input_inventory_sha256 = "e".repeat(64)),
+            Box::new(|r, _| r.candidate_commit = "e".repeat(40)),
+            Box::new(|r, _| r.candidate_tree_sha256 = "e".repeat(64)),
+            Box::new(|_, m| m.abf_id = "ABF-P3-141-v1".into()),
+            Box::new(|_, m| m.review_conclusion = "REWORK".into()),
+            Box::new(|_, m| m.candidate_tree_sha256 = "e".repeat(64)),
+        ];
+        for change in cases {
+            let mut r = receipt();
+            let mut m = manifest();
+            change(&mut r, &mut m);
+            rejected(|| validate_revision_2_binding(&r, &m, &"a".repeat(40), &"b".repeat(64)));
+        }
+    }
+
+    #[test]
+    fn v2_receipt_schema_rejects_duplicate_extra_and_fallback_fields() {
+        let duplicate = br#"{"schema":"lifeos.p3-141.phase-c-independent-pass-receipt.v2","schema":"ABF-P3-141-v1"}"#;
+        let extra = br#"{"schema":"lifeos.p3-141.phase-c-independent-pass-receipt.v2","task_id":"LIFEOS-P3-141","task_sha256":"c97419a1818e0aa6fe6fc61c487e3ef97746e199b2c7d22435d8c05090374800","fixed_input_inventory_sha256":"3651e046da8211f06bf5144a155a0505b7ddfbaab67a249e51d94aeae09861a5","abf_id":"ABF-P3-141-v2","abf_sha256":"096ad12beec63b78aaa3be92535b4a6ea632cdc4235c1d83f224db955d5dc9ea","candidate_commit":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","candidate_tree_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","verdict":"PASS","review_identity":{"role":"independent_review","attempt_id":"provider-restoration-v2-gate"},"review_manifest":{"file":"FINAL_MANIFEST.json","sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","schema":"lifeos.p3-141.independent-review-manifest.v2"},"issued_at_utc":"2026-08-30T00:00:00Z","fallback":"attempt-8"}"#;
+        rejected(|| { let _: PassReceipt = strict_json(duplicate, "duplicate"); });
+        rejected(|| { let _: PassReceipt = strict_json(extra, "extra"); });
+    }
+
+    #[test]
+    fn v2_receipt_file_gate_rejects_symlink_and_directory_before_read() {
+        let root = PathBuf::from(env::var("LIFEOS_P3_141_V2_GATE_TEST_ROOT").expect("explicit v2 gate test root required"));
+        let case = root.join(format!("gate-file-negative-{}", std::process::id()));
+        let _ = fs::remove_dir_all(&case);
+        fs::create_dir_all(&case).unwrap();
+        let regular = case.join("regular.json");
+        fs::write(&regular, b"{}\n").unwrap();
+        fs::set_permissions(&regular, fs::Permissions::from_mode(0o400)).unwrap();
+        assert_eq!(readonly_regular(&regular, MAX_RECEIPT_BYTES, "regular"), b"{}\n");
+        let link = case.join("linked.json");
+        symlink(&regular, &link).unwrap();
+        rejected(|| { readonly_regular(&link, MAX_RECEIPT_BYTES, "linked"); });
+        rejected(|| { readonly_regular(&case, MAX_RECEIPT_BYTES, "directory"); });
+        let real_parent = case.join("real-parent");
+        fs::create_dir(&real_parent).unwrap();
+        let linked_parent = case.join("linked-parent");
+        symlink(&real_parent, &linked_parent).unwrap();
+        assert!(!no_linked_ancestor(&linked_parent.join("receipt.json")));
+        fs::remove_dir_all(&case).unwrap();
+    }
+}
## src/runtime.rs
--- /private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1/base-runtime.rs	2026-08-30 18:14:03
+++ candidate/src/runtime.rs	2026-08-30 18:09:28
@@ -21,9 +21,9 @@
 const ROOT: Option<&str> = option_env!("LIFEOS_RUNTIME_ROOT");
 const MODE: Option<&str> = option_env!("LIFEOS_INPUT_MODE");
 // build.rs creates this only after it has verified a committed, review-owned
-// Phase B Pass asset. Synthetic review builds get no binding at all; an
+// Revision-2 independent Pass asset. Synthetic review builds get no binding at all; an
 // arbitrary environment string can never enter the real-mode branch.
-include!(concat!(env!("OUT_DIR"), "/phase_b_receipt_binding.rs"));
+include!(concat!(env!("OUT_DIR"), "/phase_c_v2_receipt_binding.rs"));
 const IPC: [&str; 20] = ["capture_record", "get_today", "runtime_status", "confirm_capture_context", "get_context_recovery", "get_context_next_action", "decide_context_next_action", "record_action_result", "assemble_global_ai_context", "get_evidence_backed_understanding", "decide_understanding_feedback", "get_ai_provider_settings", "save_ai_provider_settings", "set_ai_provider_session_credential", "test_ai_provider_connection", "set_ai_provider_enabled", "upsert_durable_memory", "update_current_state", "resolve_request_context", "get_context_disclosure_receipt"];
 const CONTEXT: &str = "ctx:project:local-work-self-use";
 const PROJECT: &str = "local-work-self-use";
@@ -64,7 +64,7 @@
     fn limit(self) -> i64 { if self == Self::Real { 14 } else { 2 } }
     fn idempotency_prefix(self) -> &'static str { if self == Self::Real { "p3-141-real-ui-" } else { "p3-141-" } }
 }
-fn mode() -> Result<InputMode, Error> { match (COMPILED_BUILD_MODE, MODE, VALIDATED_PHASE_B_RECEIPT_SHA256) { ("synthetic_review", Some("synthetic"), None) => Ok(InputMode::Synthetic), ("phase_c_real", Some("real_self_use"), Some(binding)) if binding.len() == 64 => Ok(InputMode::Real), ("phase_c_real", Some("real_self_use"), _) => Err(Error::blocked("phase_b_independent_pass_required", "真实模式需要已验证的独立 Phase B Pass receipt；没有探测真实根。")), _ => Err(Error::blocked("input_mode_rejected", "构建模式与输入模式必须明确且匹配。")) } }
+fn mode() -> Result<InputMode, Error> { match (COMPILED_BUILD_MODE, MODE, VALIDATED_PHASE_C_V2_RECEIPT_SHA256) { ("synthetic_review", Some("synthetic"), None) => Ok(InputMode::Synthetic), ("phase_c_real", Some("real_self_use"), Some(binding)) if binding.len() == 64 => Ok(InputMode::Real), ("phase_c_real", Some("real_self_use"), _) => Err(Error::blocked("phase_c_v2_independent_pass_required", "真实模式需要已验证的独立 Revision-2 Pass receipt；没有探测真实根。")), _ => Err(Error::blocked("input_mode_rejected", "构建模式与输入模式必须明确且匹配。")) } }
 
 #[derive(Debug, Serialize)] struct Error { status: &'static str, code: &'static str, message: &'static str }
 impl Error { fn blocked(code: &'static str, message: &'static str) -> Self { eprintln!("ipc_result status=blocked code={code}"); Self { status: "blocked", code, message } } }
## added gate test
// Compile build.rs as a test module so its Revision-2 gate tests exercise the
// same schema, duplicate-key parser and file-boundary helpers as the build gate.
#[path = "../build.rs"]
mod revision_2_gate;
