#[path = "../../../../../engineering/LIFEOS-P3-143/candidate/src/deepseek.rs"]
mod deepseek;
#[path = "../../../../../engineering/LIFEOS-P3-143/candidate/src/secure_credentials.rs"]
mod secure_credentials;

mod runtime {
    include!("../../../../../engineering/LIFEOS-P3-143/candidate/src/runtime.rs");

    #[cfg(test)]
    mod independent_rereview4_probes {
        use super::*;
        use std::fs;
        use std::os::unix::fs::{symlink, PermissionsExt};
        use std::path::{Path, PathBuf};

        const RUN_ID: &str = "finalgui-20260902";
        const ROOT_LITERAL: &str = "/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902";

        fn authority() -> RootAuthority {
            RootAuthority {
                profile: "independent-review".into(),
                parent: "/private/tmp".into(),
                basename: "lifeos-p3-143-independent-review-finalgui-20260902".into(),
                root: ROOT_LITERAL.into(),
                marker_schema: "lifeos.p3-143.independent-review-root.v1".into(),
                marker_task: "LIFEOS-P3-143".into(),
                marker_owner: "lifeos-p3-143-independent-review".into(),
                run_id: RUN_ID.into(),
                marker_run_id: Some(RUN_ID.into()),
            }
        }

        fn marker(root: &Path) -> PathBuf { root.join(MARKER) }

        fn remove_runtime_db(root: &Path) {
            for item in [root.join(RUNTIME_CHILD), root.join(DB)] {
                if let Ok(meta) = fs::symlink_metadata(&item) {
                    if meta.file_type().is_dir() && !meta.file_type().is_symlink() {
                        fs::remove_dir(&item).unwrap();
                    } else {
                        fs::remove_file(&item).unwrap();
                    }
                }
            }
        }

        fn restore_marker(root: &Path, auth: &RootAuthority) {
            let target = marker(root);
            let _ = fs::remove_file(&target);
            fs::write(&target, serde_json::to_vec(&expected_marker(auth)).unwrap()).unwrap();
            fs::set_permissions(&target, fs::Permissions::from_mode(0o600)).unwrap();
        }

        fn assert_prewrite_invariants(root: &Path, sentinel: &Path) {
            assert_eq!(fs::read(sentinel).unwrap(), b"finalgui-review-sentinel\n");
            assert!(fs::symlink_metadata(root.join(RUNTIME_CHILD)).is_err());
            assert!(fs::symlink_metadata(root.join(DB)).is_err());
        }

        #[test]
        fn review_owned_finalgui_root_authority_matrix() {
            let root = PathBuf::from(ROOT_LITERAL);
            assert!(fs::symlink_metadata(&root).is_err(), "sealed root starts absent");
            let auth = authority();
            assert!(compiled_authority_is_valid(&auth));
            assert_eq!(compiled_root_authority().root, ROOT_LITERAL);
            assert_eq!(compiled_root_authority().profile, "independent-review");
            assert_eq!(compiled_root_authority().run_id, RUN_ID);
            assert!(valid_review_run_id(RUN_ID));

            let runtime = verify_authorized_root(&auth).unwrap();
            assert_eq!(runtime, root);
            let sentinel = root.join("review-owned-sentinel.txt");
            fs::write(&sentinel, b"finalgui-review-sentinel\n").unwrap();
            remove_runtime_db(&root);

            fs::remove_file(marker(&root)).unwrap();
            assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_missing");
            assert_prewrite_invariants(&root, &sentinel);

            restore_marker(&root, &auth);
            fs::write(marker(&root), b"{\"schema\":\"wrong\"}\n").unwrap();
            fs::set_permissions(marker(&root), fs::Permissions::from_mode(0o600)).unwrap();
            assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_rejected");
            assert_prewrite_invariants(&root, &sentinel);

            restore_marker(&root, &auth);
            fs::remove_file(marker(&root)).unwrap();
            symlink(&sentinel, marker(&root)).unwrap();
            assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_type_rejected");
            assert_prewrite_invariants(&root, &sentinel);

            restore_marker(&root, &auth);
            fs::set_permissions(marker(&root), fs::Permissions::from_mode(0o640)).unwrap();
            assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_type_rejected");
            assert_prewrite_invariants(&root, &sentinel);

            restore_marker(&root, &auth);
            let mut wrong_parent = auth.clone();
            wrong_parent.parent = "/private/var".into();
            assert_eq!(verify_authorized_root(&wrong_parent).unwrap_err().code, "compiled_root_authority_rejected");
            let mut wrong_profile = auth.clone();
            wrong_profile.profile = "engineering".into();
            assert_eq!(verify_authorized_root(&wrong_profile).unwrap_err().code, "compiled_root_authority_rejected");
            let mut wrong_run_id = auth.clone();
            wrong_run_id.run_id = "invalid-run".into();
            wrong_run_id.marker_run_id = Some("invalid-run".into());
            assert_eq!(verify_authorized_root(&wrong_run_id).unwrap_err().code, "compiled_root_authority_rejected");
            assert_prewrite_invariants(&root, &sentinel);

            assert!(verify_runtime_child(&root).is_ok());
            fs::remove_dir(root.join(RUNTIME_CHILD)).unwrap();
            symlink(&sentinel, root.join(RUNTIME_CHILD)).unwrap();
            assert_eq!(verify_runtime_child(&root).unwrap_err().code, "runtime_child_type_rejected");
            fs::remove_file(root.join(RUNTIME_CHILD)).unwrap();
            assert!(verify_runtime_child(&root).is_ok());
            fs::remove_dir(root.join(RUNTIME_CHILD)).unwrap();
            assert!(database_path(&root).is_ok());
            symlink(&sentinel, root.join(DB)).unwrap();
            assert_eq!(database_path(&root).unwrap_err().code, "database_path_rejected");
            fs::remove_file(root.join(DB)).unwrap();
            initialize_store(&root).unwrap();
            assert!(database_path(&root).is_ok());

            std::env::set_var("LIFEOS_RUNTIME_ROOT", "/private/tmp/injected-root");
            std::env::set_var("LIFEOS_P3_143_ROOT_PROFILE", "engineering");
            std::env::set_var("LIFEOS_P3_143_REVIEW_RUN_ID", "attempted-injection");
            let compiled = compiled_root_authority();
            assert_eq!(compiled.root, ROOT_LITERAL);
            assert_eq!(compiled.profile, "independent-review");
            assert_eq!(compiled.run_id, RUN_ID);

            println!("{{\"result\":\"PASS\",\"literal_root\":\"{}\",\"profile\":\"independent-review\",\"run_id\":\"{}\",\"root_cases\":12,\"network_requests\":0}}", ROOT_LITERAL, RUN_ID);
        }
    }
}
