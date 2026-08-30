#[cfg(test)]
mod attempt4_independent_runtime_tests {
    use super::super::*;
    use super::super::memory_context;
    use std::fs;
    use std::os::unix::fs::symlink;
    use std::path::Path;

    fn fixture_paths(base: &Path, name: &str) -> Paths {
        let root = base.join(name);
        Paths { db: root.join(DB), root, mode: InputMode::Real }
    }

    fn table_count(conn: &Connection, table: &str) -> i64 {
        let exists: i64 = conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?1", [table], |row| row.get(0)).unwrap();
        if exists == 0 { 0 } else { conn.query_row(&format!("SELECT count(*) FROM {table}"), [], |row| row.get(0)).unwrap() }
    }

    fn counts(paths: &Paths) -> (i64, i64, i64, i64, i64, i64, i64) {
        let conn = read(paths).unwrap();
        (
            table_count(&conn, "captures"), table_count(&conn, "work_trial_days"),
            table_count(&conn, "durable_memories"), table_count(&conn, "current_state_events"),
            table_count(&conn, "context_requests"), table_count(&conn, "context_receipt_items"),
            table_count(&conn, "audit"),
        )
    }

    fn work(paths: &Paths, key: &str) -> Result<CaptureResponse, Error> {
        capture(paths, &CaptureRequest {
            text: "Synthetic Attempt-4 Work fixture.".into(),
            key: key.into(),
        })
    }

    fn memory(id: &str) -> memory_context::DurableMemoryRequest {
        memory_context::DurableMemoryRequest {
            operation: memory_context::MemoryOperation::Create,
            memory_id: id.into(), replacement_id: None,
            statement: Some(format!("Synthetic Attempt-4 confirmed preference {id}.")),
            memory_type: Some("preference".into()),
            source_refs: Some(vec!["source:synthetic:controlled-fixture".into()]),
            observed_at_ms: None, domain: memory_context::Domain::Person,
            scope: "person".into(), expected_generation: None,
            idempotency_key: format!("p3-141-real-ui-attempt4-memory-{id}"),
        }
    }

    fn confirm_memory(paths: &Paths, id: &str, generation: i64) {
        memory_context::upsert(paths, memory_context::DurableMemoryRequest {
            operation: memory_context::MemoryOperation::Confirm,
            memory_id: id.into(), replacement_id: None, statement: None,
            memory_type: None, source_refs: None, observed_at_ms: None,
            domain: memory_context::Domain::Person, scope: "person".into(),
            expected_generation: Some(generation),
            idempotency_key: format!("p3-141-real-ui-attempt4-confirm-{id}"),
        }).unwrap();
    }

    fn health(id: &str, sleep: memory_context::SleepDurationRange, energy: u8, pain: bool, load: memory_context::TrainingLoad, time: memory_context::AvailableTime) -> memory_context::CurrentStateRequest {
        memory_context::CurrentStateRequest {
            operation: memory_context::StateOperation::Set,
            state_id: id.into(), replacement_id: None,
            state_key: Some("health_fitness_structured_v1".into()), value: None,
            domain: memory_context::Domain::Health,
            source_refs: Some(vec!["source:synthetic:controlled-fixture".into()]),
            expires_at_ms: Some(now().unwrap() + 86_400_000), expected_generation: None,
            idempotency_key: format!("p3-141-real-ui-attempt4-health-{id}"),
            structured_health: Some(memory_context::StructuredHealthState {
                sleep_duration_range: sleep, energy, soreness_or_pain: pain,
                training_load: load, available_time: time,
            }),
        }
    }

    #[test]
    fn attempt4_unreceipted_real_mode_fails_before_fixture_root_access() {
        assert_eq!(mode().unwrap_err().code, "phase_b_independent_pass_required");
    }

    #[test]
    fn attempt4_receipted_real_matrix() {
        let configured = paths().unwrap();
        assert_eq!(configured.mode, InputMode::Real);
        assert!(metadata(&configured.root).unwrap().is_none());
        let fixture_base = configured.root.parent().unwrap().join("attempt4-fixtures-r5");
        fs::create_dir(&fixture_base).unwrap();

        let daily = fixture_paths(&fixture_base, "attempt4-daily");
        work(&daily, "p3-141-real-ui-attempt4-daily-one").unwrap();
        let before_daily = counts(&daily);
        assert_eq!(work(&daily, "p3-141-real-ui-attempt4-daily-two").unwrap_err().code, "daily_work_limit_rejected");
        assert_eq!(before_daily, counts(&daily));
        drop(read(&daily).unwrap());
        assert_eq!(before_daily, counts(&daily));

        let total = fixture_paths(&fixture_base, "attempt4-total");
        work(&total, "p3-141-real-ui-attempt4-total-zero").unwrap();
        write(&total, |conn| {
            for number in 1..14 {
                let key = format!("p3-141-real-ui-attempt4-total-{number}");
                conn.execute("INSERT INTO captures(id,content,created_at_ms,source,source_id,artifact_version,idem_key) VALUES(?1,?2,?3,'local_capture',?4,?5,?6)", rusqlite::params![format!("capture:p3-141:real:{key}"), "Synthetic Attempt-4 Work fixture.", now()? + number, InputMode::Real.source(), InputMode::Real.artifact(), key]).map_err(sql)?;
            }
            Ok(())
        }).unwrap();
        let before_total = counts(&total);
        assert_eq!(work(&total, "p3-141-real-ui-attempt4-total-fifteen").unwrap_err().code, "input_limit_rejected");
        assert_eq!(before_total, counts(&total));

        let memories = fixture_paths(&fixture_base, "attempt4-memory");
        for number in 1..=3 {
            let id = format!("memory:p3-141:real:attempt4-{number}");
            let created = memory_context::upsert(&memories, memory(&id)).unwrap();
            confirm_memory(&memories, &id, created.generation);
        }
        let before_memory = counts(&memories);
        assert_eq!(memory_context::upsert(&memories, memory("memory:p3-141:real:attempt4-four")).unwrap_err().code, "durable_memory_limit_rejected");
        assert_eq!(before_memory, counts(&memories));
        drop(read(&memories).unwrap());
        assert_eq!(before_memory, counts(&memories));

        let health_paths = fixture_paths(&fixture_base, "attempt4-health");
        let sleeps = [memory_context::SleepDurationRange::UnderFiveHours, memory_context::SleepDurationRange::FiveToSevenHours, memory_context::SleepDurationRange::SevenToNineHours, memory_context::SleepDurationRange::OverNineHours];
        let loads = [memory_context::TrainingLoad::Low, memory_context::TrainingLoad::Medium, memory_context::TrainingLoad::High];
        let times = [memory_context::AvailableTime::UnderThirtyMinutes, memory_context::AvailableTime::ThirtyToSixtyMinutes, memory_context::AvailableTime::SixtyToOneHundredTwentyMinutes, memory_context::AvailableTime::OverOneHundredTwentyMinutes];
        let mut index = 0usize;
        let mut previous: Option<(String, i64)> = None;
        for sleep in sleeps { for energy in 1..=5 { for pain in [false, true] { for load in loads { for time in times {
            let id = format!("state:p3-141:real:attempt4-{index}");
            let mut request = health(&id, sleep, energy, pain, load, time);
            if let Some((previous_id, generation)) = previous {
                request.operation = memory_context::StateOperation::Correct;
                request.state_id = previous_id;
                request.replacement_id = Some(id);
                request.expected_generation = Some(generation);
            }
            let response = memory_context::update_state(&health_paths, request).unwrap();
            previous = Some((response.state_id, response.generation));
            index += 1;
        }}}}}
        assert_eq!(index, 480);
        let before_health = counts(&health_paths);
        assert_eq!(memory_context::update_state(&health_paths, health("state:p3-141:real:attempt4-invalid", memory_context::SleepDurationRange::SevenToNineHours, 0, false, memory_context::TrainingLoad::Low, memory_context::AvailableTime::UnderThirtyMinutes)).unwrap_err().code, "health_schema_rejected");
        let free_text = r#"{"operation":"set","state_id":"state:p3-141:real:attempt4-free","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:synthetic:controlled-fixture"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"p3-141-real-ui-attempt4-free","structured_health":{"sleep_duration_range":"seven_to_nine_hours","energy":3,"soreness_or_pain":false,"training_load":"low","available_time":"under_thirty_minutes","free_text":"forbidden"}}"#;
        assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(free_text).is_err());
        let missing_field = r#"{"operation":"set","state_id":"state:p3-141:real:attempt4-missing","replacement_id":null,"state_key":"health_fitness_structured_v1","value":null,"domain":"health","source_refs":["source:synthetic:controlled-fixture"],"expires_at_ms":4102444800000,"expected_generation":null,"idempotency_key":"p3-141-real-ui-attempt4-missing","structured_health":{"sleep_duration_range":"seven_to_nine_hours","energy":3,"soreness_or_pain":false,"training_load":"low"}}"#;
        assert!(serde_json::from_str::<memory_context::CurrentStateRequest>(missing_field).is_err());
        assert_eq!(before_health, counts(&health_paths));
        let conn = read(&health_paths).unwrap();
        let states: i64 = conn.query_row("SELECT count(*) FROM structured_health_states", [], |row| row.get(0)).unwrap();
        assert_eq!(states, 480);

        assert_eq!(provider_profiles(), vec!["openai", "anthropic", "ollama", "lm_studio"]);
        assert!(serde_json::from_str::<ProviderProfile>("\"custom_openai_compatible\"").is_err());
        let mut locked = default_provider_state();
        locked.locked_profile = Some(ProviderProfile::Openai);
        let settings = ProviderSettings { mode: ProviderMode::Cloud, profile: ProviderProfile::Anthropic, base_url: "https://api.example.test/v1".into(), model: "fixture-model".into(), temperature_bps: 0, max_output_tokens: 10, timeout_ms: 1_000 };
        assert_eq!(save_provider_settings(&health_paths, &mut locked, SaveProviderSettingsRequest { settings }).unwrap_err().code, "provider_locked_after_first_send");

        let no_receipt = memory_context::receipt(&health_paths, memory_context::ReceiptRequest { request_id: "request:synthetic:attempt4-missing".into() }).unwrap_err();
        assert_eq!(no_receipt.code, "receipt_not_found");
        let before_resolver = counts(&health_paths);
        let rejected = memory_context::resolve(&health_paths, memory_context::ResolveRequest { request_id: "request:synthetic:attempt4-rejected".into(), task_type: memory_context::TaskType::Work, query_text: "planning".into(), authorization_id: "AUTH-SYN-REVOKED".into(), health_necessary: false, removed_domains: None, top_k: Some(3), token_budget: Some(256) }).unwrap_err();
        assert_eq!(rejected.code, "authorization_rejected");
        assert_eq!(before_resolver, counts(&health_paths));
    }

    #[test]
    fn attempt4_real_root_shapes_and_owned_restart() {
        let base = paths().unwrap().root.parent().unwrap().join("attempt4-root-shapes-r3");
        fs::create_dir(&base).unwrap();

        let fresh = Paths { root: base.join("fresh-missing"), db: base.join("fresh-missing").join(DB), mode: InputMode::Real };
        work(&fresh, "p3-141-real-ui-attempt4-fresh").unwrap();
        let fresh_before = counts(&fresh);
        let repeat = work(&fresh, "p3-141-real-ui-attempt4-fresh").unwrap();
        assert_eq!(repeat.status, "idempotent_repeat");
        let fresh_after = counts(&fresh);
        assert_eq!(fresh_before.0, fresh_after.0);
        assert_eq!(fresh_before.1, fresh_after.1);
        drop(read(&fresh).unwrap());
        assert_eq!(fresh_after.0, counts(&fresh).0);
        assert_eq!(fresh_after.1, counts(&fresh).1);

        let empty = fixture_paths(&base, "existing-empty");
        fs::create_dir(&empty.root).unwrap();
        assert_eq!(work(&empty, "p3-141-real-ui-attempt4-empty").unwrap_err().code, "real_root_ownership_missing");
        assert!(std::fs::symlink_metadata(&empty.db).is_err());

        let file = fixture_paths(&base, "existing-file");
        std::fs::File::create(&file.root).unwrap();
        assert_eq!(work(&file, "p3-141-real-ui-attempt4-file").unwrap_err().code, "runtime_root_type_rejected");

        let link_target = base.join("link-target");
        fs::create_dir(&link_target).unwrap();
        let link = fixture_paths(&base, "existing-link");
        symlink(&link_target, &link.root).unwrap();
        assert_eq!(work(&link, "p3-141-real-ui-attempt4-link").unwrap_err().code, "runtime_root_type_rejected");

        let ancestor_target = base.join("ancestor-target");
        fs::create_dir(&ancestor_target).unwrap();
        let ancestor_link = base.join("ancestor-link");
        symlink(&ancestor_target, &ancestor_link).unwrap();
        let ancestor_root = ancestor_link.join("child");
        assert_eq!(root_shape(&ancestor_root).unwrap_err().code, "path_symlink_rejected");
        assert_eq!(root_shape(&base.join("noncanonical/../noncanonical")).unwrap_err().code, "runtime_root_noncanonical");

        let unowned_db = fixture_paths(&base, "unowned-db");
        fs::create_dir(&unowned_db.root).unwrap();
        std::fs::File::create(&unowned_db.db).unwrap();
        assert_eq!(work(&unowned_db, "p3-141-real-ui-attempt4-unowned-db").unwrap_err().code, "real_root_ownership_missing");

        let unknown = fixture_paths(&base, "unknown-content");
        fs::create_dir(&unknown.root).unwrap();
        std::fs::File::create(unknown.root.join("unknown")).unwrap();
        assert_eq!(work(&unknown, "p3-141-real-ui-attempt4-unknown").unwrap_err().code, "real_root_not_empty");

        let sidecar = fixture_paths(&base, "sidecar");
        fs::create_dir(&sidecar.root).unwrap();
        std::fs::File::create(sidecar.root.join("capture.sqlite-wal")).unwrap();
        assert_eq!(work(&sidecar, "p3-141-real-ui-attempt4-sidecar").unwrap_err().code, "database_sidecar_rejected");
    }

    #[test]
    fn attempt4_today_feedback_and_context_budget_fail_closed() {
        let base = paths().unwrap().root.parent().unwrap().join("attempt4-feedback-budget-r3");
        fs::create_dir(&base).unwrap();
        let paths = fixture_paths(&base, "today");
        let initial = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
            scenario: Some("normal".into()), counterfactual_case: None,
            request_id: Some("p3-140:attempt4-feedback-base".into()),
            health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()),
            feedback: None, expected_generation: None, fault: None,
        }).unwrap();
        let target = initial.results[0].result_id.clone();
        let feedback = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
            scenario: Some("normal".into()), counterfactual_case: None,
            request_id: Some("p3-140:attempt4-feedback-correct".into()),
            health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()),
            feedback: Some(today_intelligence::TodayFeedback { result_id: target.clone(), decision: today_intelligence::FeedbackDecision::Correct, detail: Some("Synthetic Attempt-4 scope correction.".into()) }),
            expected_generation: Some(initial.snapshot_generation), fault: None,
        }).unwrap();
        assert_eq!(feedback.feedback.decision.as_deref(), Some("correct"));
        let conn = read(&paths).unwrap();
        let stale: i64 = conn.query_row("SELECT count(*) FROM p3140_results WHERE result_id=?1 AND state='stale'", [target], |row| row.get(0)).unwrap();
        let feedback_count: i64 = conn.query_row("SELECT count(*) FROM p3140_feedback", [], |row| row.get(0)).unwrap();
        assert_eq!((stale, feedback_count), (1, 1));
        drop(conn);

        let before = counts(&paths);
        let fault = today_intelligence::respond(&paths, &today_intelligence::TodayRequest {
            scenario: Some("normal".into()), counterfactual_case: None,
            request_id: Some("p3-140:attempt4-budget-fault".into()),
            health_included: Some(true), authorization: Some("p3-140-synthetic-cross-domain-granted".into()),
            feedback: None, expected_generation: None, fault: Some("over_budget".into()),
        }).unwrap_err();
        assert_eq!(fault.code, "context_budget_rejected");
        assert_eq!(before, counts(&paths));

        let budget_paths = fixture_paths(&base, "resolver");
        write(&budget_paths, |_| Ok(())).unwrap();
        let resolver_before = counts(&budget_paths);
        let error = memory_context::resolve(&budget_paths, memory_context::ResolveRequest {
            request_id: "request:synthetic:attempt4-budget-minimum".into(),
            task_type: memory_context::TaskType::Work, query_text: "planning".into(),
            authorization_id: "AUTH-SYN-PERSON-GRANTED".into(), health_necessary: false,
            removed_domains: None, top_k: Some(3), token_budget: Some(31),
        }).unwrap_err();
        assert_eq!(error.code, "context_budget_rejected");
        assert_eq!(resolver_before, counts(&budget_paths));
    }

    #[test]
    fn attempt4_today_health_ui_payload_rejects_in_controlled_fixture_mode() {
        // This mirrors the actual Today UI's real-mode payload.  In the
        // receipt-enabled fixture mode used for Phase B, the runtime requires
        // source:synthetic:controlled-fixture while the UI sends
        // source:local:user-confirmed.  Validation occurs before any root or
        // database write.
        let base = paths().unwrap().root.parent().unwrap().join("attempt4-ui-health-payload-r1");
        fs::create_dir(&base).unwrap();
        let paths = fixture_paths(&base, "today-ui");
        let request = memory_context::CurrentStateRequest {
            operation: memory_context::StateOperation::Set,
            state_id: "state:p3-141:real:health-ui-attempt4".into(), replacement_id: None,
            state_key: Some("health_fitness_structured_v1".into()), value: None,
            domain: memory_context::Domain::Health,
            source_refs: Some(vec!["source:local:user-confirmed".into()]),
            expires_at_ms: Some(now().unwrap() + 86_400_000), expected_generation: None,
            idempotency_key: "p3-141-real-ui-health-attempt4".into(),
            structured_health: Some(memory_context::StructuredHealthState {
                sleep_duration_range: memory_context::SleepDurationRange::SevenToNineHours,
                energy: 3, soreness_or_pain: false,
                training_load: memory_context::TrainingLoad::Medium,
                available_time: memory_context::AvailableTime::ThirtyToSixtyMinutes,
            }),
        };
        assert_eq!(memory_context::update_state(&paths, request).unwrap_err().code, "source_refs_rejected");
        assert!(std::fs::symlink_metadata(&paths.root).is_err());
    }
}
