#[cfg(test)]
mod independent_review_runtime_tests {
    use super::*;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::os::unix::fs::PermissionsExt;
    use std::thread;

    fn settings(mode: ProviderMode, profile: ProviderProfile, base_url: String, model: &str) -> ProviderSettings {
        ProviderSettings { mode, profile, base_url, model: model.into(), temperature_bps: 70, max_output_tokens: 256, timeout_ms: 1_000 }
    }

    fn one_models_fixture() -> (u16, thread::JoinHandle<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let handle = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            let mut request = [0_u8; 8192];
            let received = stream.read(&mut request).unwrap();
            stream.write_all(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 36\r\nConnection: close\r\n\r\n{\"models\":[{\"name\":\"fixture-model\"}]}").unwrap();
            String::from_utf8_lossy(&request[..received]).into_owned()
        });
        (port, handle)
    }

    #[test]
    fn independent_mode_delete_persistence_and_action_separation() {
        let paths = paths().unwrap();
        assert_eq!(paths.mode, InputMode::Synthetic);
        assert_eq!(IPC.len(), 20);
        assert_eq!(provider_profiles(), vec!["openai", "anthropic", "deepseek", "kimi", "cloud_custom_openai_compatible", "ollama", "lm_studio", "local_custom_compatible"]);

        let mut state = load_provider_state(&paths).unwrap();
        let cloud = settings(ProviderMode::Cloud, ProviderProfile::Openai, "https://fixture.lifeos.test:443".into(), "");
        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: cloud.clone() }).unwrap();
        let synthetic_key = "review-synthetic-key-4c8a";
        let after_store = save_provider_credential(&paths, &mut state, SaveProviderCredentialRequest { operation: CredentialOperation::StoreOrUpdate, api_key: Some(synthetic_key.into()) }).unwrap();
        assert!(after_store.credential.present);
        assert_eq!(after_store.credential.storage, "encrypted_sqlite");
        let bytes_after_store = fs::read(&paths.db).unwrap();
        assert!(!bytes_after_store.windows(synthetic_key.len()).any(|window| window == synthetic_key.as_bytes()));
        let count_after_store: i64 = read(&paths).unwrap().query_row("SELECT count(*) FROM encrypted_provider_credentials", [], |row| row.get(0)).unwrap();
        assert_eq!(count_after_store, 1);
        let key = paths.root.parent().unwrap().join("keys").join(CREDENTIAL_KEY_FILE);
        assert!(key.is_file() && key != paths.db && fs::metadata(&key).unwrap().permissions().mode() & 0o777 == 0o600);

        let local = settings(ProviderMode::Local, ProviderProfile::Ollama, "http://127.0.0.1:19091".into(), "");
        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: local }).unwrap();
        assert_eq!(state.settings.mode, ProviderMode::Local);
        let before_stale_delete = fs::read(&paths.db).unwrap();
        let stale = save_provider_credential(&paths, &mut state, SaveProviderCredentialRequest { operation: CredentialOperation::Delete, api_key: None }).unwrap_err();
        assert_eq!(stale.code, "credential_mode_rejected");
        assert_eq!(before_stale_delete, fs::read(&paths.db).unwrap());
        let cloud_view = get_provider_settings(&paths, &state, GetProviderSettingsRequest { mode: Some(ProviderMode::Cloud) }).unwrap();
        let local_view = get_provider_settings(&paths, &state, GetProviderSettingsRequest { mode: Some(ProviderMode::Local) }).unwrap();
        assert!(cloud_view.credential.present);
        assert!(!local_view.credential.present);

        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: cloud }).unwrap();
        let after_delete = save_provider_credential(&paths, &mut state, SaveProviderCredentialRequest { operation: CredentialOperation::Delete, api_key: None }).unwrap();
        assert!(!after_delete.credential.present);
        let count_after_delete: i64 = read(&paths).unwrap().query_row("SELECT count(*) FROM encrypted_provider_credentials", [], |row| row.get(0)).unwrap();
        assert_eq!(count_after_delete, 0);
        let restarted = load_provider_state(&paths).unwrap();
        assert_eq!(restarted.settings.mode, ProviderMode::Cloud);
        assert!(!credential_status(&paths, &restarted.settings).unwrap().present);

        let (port, server) = one_models_fixture();
        let local = settings(ProviderMode::Local, ProviderProfile::Ollama, format!("http://127.0.0.1:{port}"), "");
        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: local.clone() }).unwrap();
        assert_eq!(set_provider_enabled(&paths, &mut state, SetProviderEnabledRequest { enabled: true }).unwrap_err().code, "provider_enablement_rejected");
        let tested = test_provider_connection(&paths, &mut state, TestProviderConnectionRequest { cancel: None }).unwrap();
        assert_eq!(tested.models, vec!["fixture-model"]);
        assert!(server.join().unwrap().starts_with("GET /api/tags HTTP/1.1"));
        let selected = ProviderSettings { model: "fixture-model".into(), ..local };
        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: selected }).unwrap();
        let enabled = set_provider_enabled(&paths, &mut state, SetProviderEnabledRequest { enabled: true }).unwrap();
        assert!(enabled.enabled);
        assert_eq!(enabled.model_request_count, 0, "save/test/select/enable must not send");
    }
}
