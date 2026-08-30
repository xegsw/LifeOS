// Review-owned tests for LIFEOS-P3-141 attempt-6.
// This module is compiled only into an ephemeral copy under the one allowed
// temporary root.  It is deliberately not part of, and never written to, the
// candidate source tree.
use super::*;
use rusqlite::params;

fn review_paths(name: &str) -> Paths {
    let base = paths().unwrap().root.parent().unwrap().to_path_buf();
    let root = base.join(format!("attempt6-{name}-{}", now().unwrap()));
    assert!(!root.exists());
    Paths { db: root.join(DB), root, mode: InputMode::Real }
}

fn remove_owned(paths: &Paths) {
    assert!(paths.root.starts_with("/private/tmp/lifeos-p3-141-controlled-pilot-v1/"));
    if paths.root.exists() { fs::remove_dir_all(&paths.root).unwrap(); }
    assert!(!paths.root.exists());
}

fn counts(paths: &Paths) -> [i64; 6] {
    if !paths.db.exists() { return [0; 6]; }
    let db = read(paths).unwrap();
    let query = |sql: &str| db.query_row(sql, [], |row| row.get::<_, i64>(0)).unwrap_or(0);
    [
        query("SELECT count(*) FROM captures"),
        query("SELECT count(*) FROM feedback"),
        query("SELECT count(*) FROM audit"),
        query("SELECT count(*) FROM durable_memories"),
        query("SELECT count(*) FROM current_state_events"),
        query("SELECT count(*) FROM understandings"),
    ]
}

fn controlled_health(paths: &Paths, id: &str, energy: u8) -> memory_context::CurrentStateRequest {
    memory_context::CurrentStateRequest {
        operation: memory_context::StateOperation::Set,
        state_id: id.into(), replacement_id: None,
        state_key: Some("health_fitness_structured_v1".into()), value: None,
        domain: memory_context::Domain::Health,
        source_refs: Some(vec![memory_context::expected_source_ref(InputMode::Real, controlled_fixture_evidence(paths)).into()]),
        expires_at_ms: Some(now().unwrap() + 86_400_000), expected_generation: None,
        idempotency_key: format!("p3-141-real-ui-{id}"),
        structured_health: Some(memory_context::StructuredHealthState {
            sleep_duration_range: memory_context::SleepDurationRange::SevenToNineHours,
            energy,
            soreness_or_pain: false,
            training_load: memory_context::TrainingLoad::Medium,
            available_time: memory_context::AvailableTime::ThirtyToSixtyMinutes,
        }),
    }
}

#[test]
fn attempt6_ipc_and_provider_are_closed_sets() {
    assert_eq!(IPC.len(), 20);
    assert_eq!(IPC[16], "upsert_durable_memory");
    assert_eq!(IPC[17], "update_current_state");
    assert_eq!(provider_profiles(), vec!["openai", "anthropic", "ollama", "lm_studio"]);
    assert!(serde_json::from_str::<ProviderProfile>("\"custom\"").is_err());
    for profile in [ProviderProfile::Openai, ProviderProfile::Anthropic, ProviderProfile::Ollama, ProviderProfile::LmStudio] {
        let settings = ProviderSettings {
            mode: if matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic) { ProviderMode::Cloud } else { ProviderMode::Local },
            profile,
            base_url: if matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic) { "https://fixture.lifeos.test:443/v1".into() } else { "http://127.0.0.1:9/v1".into() },
            model: "review-fixture".into(), temperature_bps: 0, max_output_tokens: 64, timeout_ms: 1000,
        };
        assert!(validate_provider_settings_for(&settings, InputMode::Synthetic).is_ok());
    }
}

#[test]
fn attempt6_today_health_success_and_all_invalid_forms_are_prewrite() {
    let paths = review_paths("health");
    let legal = memory_context::update_state(&paths, controlled_health(&paths, "state:p3-141:real:attempt6-legal", 4)).unwrap();
    let db = read(&paths).unwrap();
    let fields: (String, i64, i64, String, String) = db.query_row(
        "SELECT sleep_duration_range,energy,soreness_or_pain,training_load,available_time FROM structured_health_states WHERE state_id=?1",
        params![legal.state_id],
        |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?, row.get(3)?, row.get(4)?)),
    ).unwrap();
    drop(db);
    assert_eq!(fields, ("seven_to_nine_hours".into(), 4, 0, "medium".into(), "thirty_to_sixty_minutes".into()));
    let before = counts(&paths);
    let bad_energy = memory_context::update_state(&paths, controlled_health(&paths, "state:p3-141:real:attempt6-energy", 0)).unwrap_err();
    assert_eq!(bad_energy.code, "health_schema_rejected");
    let mut multiple = controlled_health(&paths, "state:p3-141:real:attempt6-source", 3);
    multiple.source_refs = Some(vec![memory_context::expected_source_ref(InputMode::Real, controlled_fixture_evidence(&paths)).into(), "source:other".into()]);
    assert_eq!(memory_context::update_state(&paths, multiple).unwrap_err().code, "source_refs_rejected");
    let missing = r#"{"operation":"set","state_id":"state:p3-141:real:attempt6-missing","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:synthetic:controlled-fixture"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"p3-141-real-ui-attempt6-missing","structured_health":{"energy":3,"soreness_or_pain":false,"training_load":"low","available_time":"under_thirty_minutes"}}"#;
    let free_text = r#"{"operation":"set","state_id":"state:p3-141:real:attempt6-free","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:synthetic:controlled-fixture"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"p3-141-real-ui-attempt6-free","structured_health":{"sleep_duration_range":"seven_to_nine_hours","energy":3,"soreness_or_pain":false,"training_load":"low","available_time":"under_thirty_minutes","free_text":"forbidden"}}"#;
    assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(missing).is_err());
    assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(free_text).is_err());
    assert_eq!(before, counts(&paths));
    remove_owned(&paths);
}

#[test]
fn attempt6_root_and_work_limit_fail_closed_without_reuse() {
    let suite = review_paths("root-and-quota");
    let first = capture(&suite, &CaptureRequest { text: "attempt6 synthetic work".into(), key: "p3-141-real-ui-attempt6-first".into() }).unwrap();
    let before = counts(&suite);
    let second = capture(&suite, &CaptureRequest { text: "attempt6 second work".into(), key: "p3-141-real-ui-attempt6-second".into() }).unwrap_err();
    assert_eq!(second.code, "daily_work_limit_rejected");
    assert_eq!(before, counts(&suite));
    let repeat = capture(&suite, &CaptureRequest { text: "attempt6 synthetic work".into(), key: "p3-141-real-ui-attempt6-first".into() }).unwrap();
    assert_eq!(repeat.status, "idempotent_repeat");
    assert_eq!(repeat.record.id, first.record.id);
    remove_owned(&suite);

    let parent = paths().unwrap().root.parent().unwrap().to_path_buf();
    let file_root = parent.join(format!("attempt6-root-file-{}", now().unwrap()));
    fs::write(&file_root, b"review-controlled-file").unwrap();
    let collision = Paths { db: file_root.join(DB), root: file_root.clone(), mode: InputMode::Real };
    assert_eq!(capture(&collision, &CaptureRequest { text: "attempt6 collision".into(), key: "p3-141-real-ui-attempt6-collision".into() }).unwrap_err().code, "runtime_root_type_rejected");
    fs::remove_file(&file_root).unwrap();
}

#[test]
fn attempt6_stable_viewport_rejects_stale_first_sample() {
    let desktop = ViewportGeometry { inner_width: 1280, inner_height: 949, outer_width: 1280, outer_height: 949, scale_factor: 1.0 };
    let compact = ViewportGeometry { inner_width: 700, inner_height: 760, outer_width: 700, outer_height: 760, scale_factor: 1.0 };
    let narrow = ViewportGeometry { inner_width: 560, inner_height: 640, outer_width: 560, outer_height: 640, scale_factor: 1.0 };
    assert_eq!(stable_viewport_geometry(&[desktop, compact, compact]).unwrap_err().code, "evidence_viewport_unstable");
    assert!(stable_viewport_geometry(&[compact, compact, compact]).unwrap().matches(compact));
    assert!(stable_viewport_geometry(&[narrow, narrow, narrow]).unwrap().matches(narrow));
}
