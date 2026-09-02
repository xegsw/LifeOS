mod independent_rereview_3_probes {
    use super::*;
    use std::fs;
    use std::os::unix::fs::{symlink, PermissionsExt};
    use std::path::{Path, PathBuf};

    const RUN_ID: &str = "rereview3-20260902";
    const ROOT_LITERAL: &str = "/private/tmp/lifeos-p3-143-independent-review-rereview3-20260902";

    fn authority(root: &Path) -> RootAuthority {
        RootAuthority {
            profile: "independent-review".into(),
            parent: "/private/tmp".into(),
            basename: root.file_name().unwrap().to_string_lossy().into_owned(),
            root: root.to_string_lossy().into_owned(),
            marker_schema: "lifeos.p3-143.independent-review-root.v1".into(),
            marker_task: "LIFEOS-P3-143".into(),
            marker_owner: "lifeos-p3-143-independent-review".into(),
            run_id: RUN_ID.into(),
            marker_run_id: Some(RUN_ID.into()),
        }
    }

    fn marker_path(root: &Path) -> PathBuf { root.join(MARKER) }

    fn restore_marker(root: &Path, auth: &RootAuthority) {
        let marker = marker_path(root);
        let _ = fs::remove_file(&marker);
        fs::write(&marker, serde_json::to_vec(&expected_marker(auth)).unwrap()).unwrap();
        fs::set_permissions(&marker, fs::Permissions::from_mode(0o600)).unwrap();
    }

    fn remove_runtime_and_db(root: &Path) {
        let runtime = root.join(RUNTIME_CHILD);
        let database = root.join(DB);
        if fs::symlink_metadata(&runtime).is_ok() {
            if fs::symlink_metadata(&runtime).unwrap().file_type().is_dir() { fs::remove_dir(&runtime).unwrap(); } else { fs::remove_file(&runtime).unwrap(); }
        }
        if fs::symlink_metadata(&database).is_ok() { fs::remove_file(&database).unwrap(); }
    }

    fn assert_refusal_state(root: &Path, sentinel: &Path) {
        assert_eq!(fs::read(sentinel).unwrap(), b"review-owned-sentinel\n");
        assert!(fs::symlink_metadata(root.join(RUNTIME_CHILD)).is_err());
        assert!(fs::symlink_metadata(root.join(DB)).is_err());
    }

    fn marker_gated_cleanup(root: &Path, auth: &RootAuthority) {
        let marker = marker_path(root);
        let meta = fs::symlink_metadata(&marker).unwrap();
        assert!(meta.file_type().is_file() && !meta.file_type().is_symlink());
        assert_eq!(meta.permissions().mode() & 0o777, 0o600);
        let observed: RootMarker = serde_json::from_slice(&fs::read(&marker).unwrap()).unwrap();
        assert_eq!(observed, expected_marker(auth));
        fs::remove_dir_all(root).unwrap();
        assert!(fs::symlink_metadata(root).is_err());
    }

    #[test]
    fn review_owned_single_root_authority_matrix() {
        let root = PathBuf::from(ROOT_LITERAL);
        assert!(fs::symlink_metadata(&root).is_err(), "review root must start absent");
        let auth = authority(&root);
        assert!(compiled_authority_is_valid(&auth));
        assert!(valid_review_run_id(RUN_ID));
        assert!(valid_review_run_id("secondrun-20260902"));
        for invalid in ["short", "Aupper-20260902", "slash/20260902", "dot..20260902", "-leading-20260902", "trailing-", "/absolute-20260902", "unknown_profile"] {
            assert!(!valid_review_run_id(invalid));
        }
        assert!(!valid_review_run_id(&"a".repeat(49)));

        assert_eq!(verify_authorized_root(&auth).unwrap(), root);
        let sentinel = root.join("sentinel.txt");
        fs::write(&sentinel, b"review-owned-sentinel\n").unwrap();
        assert!(root.join(RUNTIME_CHILD).is_dir());
        assert!(fs::symlink_metadata(root.join(DB)).is_err());

        remove_runtime_and_db(&root);
        fs::remove_file(marker_path(&root)).unwrap();
        assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_missing");
        assert_refusal_state(&root, &sentinel);

        restore_marker(&root, &auth);
        fs::write(marker_path(&root), b"{\"schema\":\"wrong\"}\n").unwrap();
        fs::set_permissions(marker_path(&root), fs::Permissions::from_mode(0o600)).unwrap();
        assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_rejected");
        assert_refusal_state(&root, &sentinel);

        restore_marker(&root, &auth);
        fs::remove_file(marker_path(&root)).unwrap();
        symlink(&sentinel, marker_path(&root)).unwrap();
        assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_type_rejected");
        assert_refusal_state(&root, &sentinel);

        restore_marker(&root, &auth);
        fs::set_permissions(marker_path(&root), fs::Permissions::from_mode(0o640)).unwrap();
        assert_eq!(verify_authorized_root(&auth).unwrap_err().code, "task_marker_type_rejected");
        assert_refusal_state(&root, &sentinel);

        restore_marker(&root, &auth);
        let mut wrong_parent = auth.clone();
        wrong_parent.parent = "/private/var".into();
        assert_eq!(verify_authorized_root(&wrong_parent).unwrap_err().code, "compiled_root_authority_rejected");
        let mut traversal = auth.clone();
        traversal.basename = "..".into(); traversal.root = "/private/tmp/..".into();
        assert_eq!(verify_authorized_root(&traversal).unwrap_err().code, "compiled_root_authority_rejected");
        let mut mixed_profile = auth.clone();
        mixed_profile.profile = "engineering".into();
        assert_eq!(verify_authorized_root(&mixed_profile).unwrap_err().code, "compiled_root_authority_rejected");
        let mut unknown_profile = auth.clone();
        unknown_profile.profile = "unknown".into();
        assert_eq!(verify_authorized_root(&unknown_profile).unwrap_err().code, "compiled_root_authority_rejected");
        assert_refusal_state(&root, &sentinel);

        assert!(verify_runtime_child(&root).is_ok());
        fs::remove_dir(root.join(RUNTIME_CHILD)).unwrap();
        symlink(&sentinel, root.join(RUNTIME_CHILD)).unwrap();
        assert_eq!(verify_runtime_child(&root).unwrap_err().code, "runtime_child_type_rejected");
        fs::remove_file(root.join(RUNTIME_CHILD)).unwrap();
        fs::create_dir(root.join(RUNTIME_CHILD)).unwrap();
        fs::set_permissions(root.join(RUNTIME_CHILD), fs::Permissions::from_mode(0o755)).unwrap();
        assert_eq!(verify_runtime_child(&root).unwrap_err().code, "runtime_child_type_rejected");
        fs::remove_dir(root.join(RUNTIME_CHILD)).unwrap();
        assert!(verify_runtime_child(&root).is_ok());

        assert_eq!(database_path(&root).unwrap(), root.join(DB));
        symlink(&sentinel, root.join(DB)).unwrap();
        assert_eq!(database_path(&root).unwrap_err().code, "database_path_rejected");
        fs::remove_file(root.join(DB)).unwrap();
        initialize_store(&root).unwrap();
        assert_eq!(database_path(&root).unwrap(), root.join(DB));

        let symlink_name = PathBuf::from("/private/tmp/lifeos-p3-143-independent-review-rereview3-link");
        assert!(fs::symlink_metadata(&symlink_name).is_err());
        symlink(&sentinel, &symlink_name).unwrap();
        let link_auth = RootAuthority { basename: "lifeos-p3-143-independent-review-rereview3-link".into(), root: symlink_name.to_string_lossy().into_owned(), run_id: "rereview3-link".into(), marker_run_id: Some("rereview3-link".into()), ..auth.clone() };
        assert_eq!(verify_authorized_root(&link_auth).unwrap_err().code, "task_root_type_rejected");
        fs::remove_file(&symlink_name).unwrap();
        assert_eq!(fs::read(&sentinel).unwrap(), b"review-owned-sentinel\n");

        std::env::set_var("LIFEOS_RUNTIME_ROOT", "/private/tmp/injected-root");
        std::env::set_var("LIFEOS_P3_143_ROOT_PROFILE", "engineering");
        std::env::set_var("LIFEOS_P3_143_REVIEW_RUN_ID", "injected-run-id");
        let compiled = compiled_root_authority();
        assert_eq!(compiled.profile, "independent-review");
        assert_eq!(compiled.run_id, RUN_ID);
        assert_eq!(compiled.root, ROOT_LITERAL);
        assert!(verify_authorized_root(&auth).is_ok());

        marker_gated_cleanup(&root, &auth);
        println!("{{\"result\":\"PASS\",\"root\":\"{}\",\"run_ids\":[\"{}\",\"secondrun-20260902\"],\"network_requests\":0}}", ROOT_LITERAL, RUN_ID);
    }
}
