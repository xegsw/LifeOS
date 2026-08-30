# P3-141 Provider Restoration semantic source diff
Compared only against the withdrawn P3-141 candidate copied at closure start. The following raw unified diffs document the two Provider-only source changes.
## runtime.rs
--- /Users/xxe/.codex/worktrees/971c/No.2/lifeos/engineering/LIFEOS-P3-141/candidate/src/runtime.rs	2026-08-30 15:28:24
+++ /Users/xxe/.codex/worktrees/971c/No.2/lifeos/engineering/LIFEOS-P3-141/closure-provider-restoration/candidate/src/runtime.rs	2026-08-30 17:26:03
@@ -88,7 +88,7 @@
 fn controlled_fixture_evidence(paths: &Paths) -> bool {
     paths.mode == InputMode::Synthetic
         && std::env::var("LIFEOS_P3_141_SYNTHETIC_FIXTURE_EVIDENCE").ok().as_deref() == Some("1")
-        && paths.root.starts_with("/private/tmp/lifeos-p3-141-controlled-pilot-v1/")
+        && paths.root.starts_with("/private/tmp/lifeos-p3-141-provider-restoration-closure-v1/")
 }
 
 // The platform applies `set_size` asynchronously. Receipt values therefore
@@ -222,7 +222,7 @@
 
 #[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
 #[serde(rename_all = "snake_case")]
-enum ProviderProfile { Openai, Anthropic, Ollama, LmStudio }
+enum ProviderProfile { Openai, Anthropic, Ollama, LmStudio, CustomOpenaiCompatible }
 
 #[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
 #[serde(deny_unknown_fields)]
@@ -312,11 +312,11 @@
 fn default_provider_settings() -> ProviderSettings { ProviderSettings { mode: ProviderMode::Disabled, profile: ProviderProfile::Openai, base_url: String::new(), model: String::new(), temperature_bps: 70, max_output_tokens: 2048, timeout_ms: 60_000 } }
 fn default_provider_state() -> ProviderState { ProviderState { settings: default_provider_settings(), locked_profile: None, enabled: false, credential: None, connection_state: "not_configured", last_test_fingerprint: None, last_tested_at_ms: None, last_latency_ms: None, model_request_count: 0, discovered_models: Vec::new() } }
 fn provider_settings_path(paths: &Paths) -> PathBuf { paths.root.join(PROVIDER_SETTINGS) }
-fn provider_profiles() -> Vec<&'static str> { vec!["openai", "anthropic", "ollama", "lm_studio"] }
+fn provider_profiles() -> Vec<&'static str> { vec!["openai", "anthropic", "ollama", "lm_studio", "custom_openai_compatible"] }
 fn credential_status(credential: &Option<SessionCredential>) -> CredentialStatus { match credential { Some(SessionCredential { value: Some(_), .. }) => CredentialStatus { present: true, source: "session_memory" }, Some(SessionCredential { environment_variable: Some(_), .. }) => CredentialStatus { present: true, source: "environment_variable_name" }, _ => CredentialStatus { present: false, source: "absent" } } }
 fn provider_response(state: &ProviderState) -> ProviderSettingsResponse { ProviderSettingsResponse { status: "ready", settings: state.settings.clone(), enabled: state.enabled, connection_state: state.connection_state, last_tested_at_ms: state.last_tested_at_ms, last_latency_ms: state.last_latency_ms, model_request_count: state.model_request_count, discovered_models: state.discovered_models.clone(), credential: credential_status(&state.credential), persistence: "nonsecret_settings_and_provider_lock_0600", network: "synthetic_loopback_only", locked_provider: state.locked_profile.map(profile_name), selectable_profiles: provider_profiles() } }
-fn profile_name(profile: ProviderProfile) -> &'static str { match profile { ProviderProfile::Openai => "openai", ProviderProfile::Anthropic => "anthropic", ProviderProfile::Ollama => "ollama", ProviderProfile::LmStudio => "lm_studio" } }
-fn profile_matches_mode(profile: ProviderProfile, mode: ProviderMode) -> bool { match mode { ProviderMode::Disabled => true, ProviderMode::Local => matches!(profile, ProviderProfile::Ollama | ProviderProfile::LmStudio), ProviderMode::Cloud => matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic) } }
+fn profile_name(profile: ProviderProfile) -> &'static str { match profile { ProviderProfile::Openai => "openai", ProviderProfile::Anthropic => "anthropic", ProviderProfile::Ollama => "ollama", ProviderProfile::LmStudio => "lm_studio", ProviderProfile::CustomOpenaiCompatible => "custom_openai_compatible" } }
+fn profile_matches_mode(profile: ProviderProfile, mode: ProviderMode) -> bool { match mode { ProviderMode::Disabled => true, ProviderMode::Local => matches!(profile, ProviderProfile::Ollama | ProviderProfile::LmStudio | ProviderProfile::CustomOpenaiCompatible), ProviderMode::Cloud => matches!(profile, ProviderProfile::Openai | ProviderProfile::Anthropic | ProviderProfile::CustomOpenaiCompatible) } }
 fn settings_fingerprint(settings: &ProviderSettings) -> String { format!("{:?}|{:?}|{}|{}|{}|{}|{}", settings.mode, settings.profile, settings.base_url, settings.model, settings.temperature_bps, settings.max_output_tokens, settings.timeout_ms) }
 fn valid_env_name(value: &str) -> bool { let mut chars = value.chars(); matches!(chars.next(), Some('A'..='Z')) && chars.all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_') && value.len() <= 128 }
 fn private_ipv4(value: &str) -> bool { match value.parse::<std::net::Ipv4Addr>() { Ok(ip) => ip.is_loopback() || ip.is_private(), Err(_) => false } }
@@ -634,7 +634,7 @@
         Ok(Feedback{status:"saved".into(),feedback_id,understanding_id:request.understanding_id,decision,feedback_text:request.edited_text,audit_event_count:audit(conn)?.event_count})
     })
 }
-fn status(paths: &Paths) -> Status { Status { status:"ready",input_mode:paths.mode.value(),controlled_synthetic_fixture:controlled_fixture_evidence(paths),offline:true,ai_enabled:false,renderer_direct_capabilities:Vec::new(),ipc_allowlist:IPC.to_vec(),unknown_ipc:"rejected",filesystem:false,raw_database:false,generic_path_api:false,shell:false,process_spawn:false,network:false,vault:false,export:false,sync:false,context_recovery:"request_local_bundle_with_optional_persistent_links",candidate_rule:"explicit_user_decision_required",memory_duplicate_original:false,model_port:"replaceable_provider_explicit_only",model_adapter:"four_profile_explicit_user_enabled_synthetic_loopback_only" } }
+fn status(paths: &Paths) -> Status { Status { status:"ready",input_mode:paths.mode.value(),controlled_synthetic_fixture:controlled_fixture_evidence(paths),offline:true,ai_enabled:false,renderer_direct_capabilities:Vec::new(),ipc_allowlist:IPC.to_vec(),unknown_ipc:"rejected",filesystem:false,raw_database:false,generic_path_api:false,shell:false,process_spawn:false,network:false,vault:false,export:false,sync:false,context_recovery:"request_local_bundle_with_optional_persistent_links",candidate_rule:"explicit_user_decision_required",memory_duplicate_original:false,model_port:"replaceable_provider_explicit_only",model_adapter:"five_profile_explicit_user_enabled_synthetic_loopback_only" } }
 
 fn get_provider_settings(state: &ProviderState) -> ProviderSettingsResponse { provider_response(state) }
 fn save_provider_settings(paths: &Paths, state: &mut ProviderState, request: SaveProviderSettingsRequest) -> Result<ProviderSettingsResponse, Error> { validate_provider_settings_for(&request.settings, paths.mode)?; if let Some(locked) = state.locked_profile { if request.settings.profile != locked { return Err(Error::blocked("provider_locked_after_first_send", "首次发送后 Provider 已锁定；不能切换 Provider。")); } } write_provider_settings(paths, &request.settings, state.locked_profile)?; state.settings = request.settings; state.enabled = false; state.credential = None; state.connection_state = if state.settings.mode == ProviderMode::Disabled { "disabled" } else { "not_tested" }; state.last_test_fingerprint = None; state.last_tested_at_ms = None; state.last_latency_ms = None; state.discovered_models.clear(); Ok(provider_response(state)) }
@@ -663,6 +663,7 @@
 struct AnthropicAdapter;
 struct OllamaAdapter;
 struct LmStudioAdapter;
+struct CustomOpenAiCompatibleAdapter;
 fn protocol_rejected(message: &'static str) -> Error { Error::blocked("provider_protocol_rejected", message) }
 fn valid_model_names(values: Vec<&str>) -> Result<Vec<String>, Error> { let models = values.into_iter().filter(|item| !item.is_empty() && item.len() <= 128 && !item.bytes().any(|byte| byte.is_ascii_control())).map(str::to_string).take(16).collect::<Vec<_>>(); if models.is_empty() { Err(protocol_rejected("Provider 探测没有可用模型。")) } else { Ok(models) } }
 fn openai_models(value: &serde_json::Value) -> Result<Vec<String>, Error> { let data = value.get("data").and_then(|item| item.as_array()).ok_or_else(|| protocol_rejected("OpenAI-compatible 探测响应缺少 data。"))?; valid_model_names(data.iter().filter_map(|item| item.get("id").and_then(|id| id.as_str())).collect()) }
@@ -677,7 +678,8 @@
 impl ModelPort for AnthropicAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{anthropic_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(ProviderWireRequest::post("/v1/messages",serde_json::json!({"model":input.model,"max_tokens":input.max_output_tokens,"temperature":temperature(input),"system":output_instruction(),"messages":[{"role":"user","content":minimal_user_message(input)}]}).to_string()))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{value.get("content").and_then(|item|item.as_array()).and_then(|items|items.first()).and_then(|item|item.get("text")).and_then(|item|item.as_str())} fn credential_header(&self,value:&str)->Option<String>{Some(format!("x-api-key: {value}"))} }
 impl ModelPort for OllamaAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/api/tags") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{ollama_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(ProviderWireRequest::post("/api/chat",serde_json::json!({"model":input.model,"stream":false,"options":{"temperature":temperature(input),"num_predict":input.max_output_tokens},"messages":[{"role":"system","content":output_instruction()},{"role":"user","content":minimal_user_message(input)}]}).to_string()))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{value.get("message").and_then(|item|item.get("content")).and_then(|item|item.as_str())} fn credential_header(&self,_:&str)->Option<String>{None} }
 impl ModelPort for LmStudioAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{openai_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(openai_inference(input))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{openai_text(value)} fn credential_header(&self,value:&str)->Option<String>{Some(format!("Authorization: Bearer {value}"))} }
-fn model_port(profile: ProviderProfile) -> Box<dyn ModelPort> { match profile { ProviderProfile::Openai => Box::new(OpenAiAdapter), ProviderProfile::Anthropic => Box::new(AnthropicAdapter), ProviderProfile::Ollama => Box::new(OllamaAdapter), ProviderProfile::LmStudio => Box::new(LmStudioAdapter) } }
+impl ModelPort for CustomOpenAiCompatibleAdapter { fn build_probe(&self)->ProviderWireRequest { ProviderWireRequest::get("/v1/models") } fn parse_models(&self,value:&serde_json::Value)->Result<Vec<String>,Error>{openai_models(value)} fn build_inference(&self,input:&ProviderInferenceInput<'_>)->Result<ProviderWireRequest,Error>{Ok(openai_inference(input))} fn output_text<'a>(&self,value:&'a serde_json::Value)->Option<&'a str>{openai_text(value)} fn credential_header(&self,value:&str)->Option<String>{Some(format!("Authorization: Bearer {value}"))} }
+fn model_port(profile: ProviderProfile) -> Box<dyn ModelPort> { match profile { ProviderProfile::Openai => Box::new(OpenAiAdapter), ProviderProfile::Anthropic => Box::new(AnthropicAdapter), ProviderProfile::Ollama => Box::new(OllamaAdapter), ProviderProfile::LmStudio => Box::new(LmStudioAdapter), ProviderProfile::CustomOpenaiCompatible => Box::new(CustomOpenAiCompatibleAdapter) } }
 
 fn endpoint_path(value: &str) -> Result<String, Error> { let (_, rest) = value.split_once("://").ok_or_else(|| Error::blocked("provider_endpoint_rejected", "Provider endpoint 必须声明 HTTP(S) 协议。"))?; let path = rest.find('/').map(|index| &rest[index..]).unwrap_or(""); if path.contains('?') || path.contains('#') || path.contains("//") { return Err(Error::blocked("provider_endpoint_rejected", "Provider endpoint 路径不受支持。")); } Ok(if path.is_empty() { String::new() } else { path.trim_end_matches('/').into() }) }
 fn local_socket(settings: &ProviderSettings) -> Result<(SocketAddr, String), Error> { let (_, host, port) = endpoint_parts(&settings.base_url)?; let port = port.ok_or_else(|| Error::blocked("provider_local_endpoint_rejected", "Local Provider 必须声明固定端口。"))?; let ip = if host == "localhost" { IpAddr::from([127, 0, 0, 1]) } else { host.parse::<IpAddr>().map_err(|_| Error::blocked("provider_local_endpoint_rejected", "Local Provider 必须为字面 IP 或 localhost。"))? }; if !local_host(host) { return Err(Error::blocked("provider_local_endpoint_rejected", "Local Provider 目标超出受控地址范围。")); } Ok((SocketAddr::new(ip, port), endpoint_path(&settings.base_url)?)) }
@@ -780,7 +782,7 @@
 
 #[cfg(test)] mod tests { use super::*; use sha2::{Digest,Sha256}; fn test_paths(name:&str)->Paths{let base=paths().unwrap().root;fs::create_dir_all(&base).unwrap();let root=base.join(format!("unit-{name}-{}",now().unwrap()));let _=fs::remove_dir_all(&root);let current=mode().unwrap();if current==InputMode::Synthetic{fs::create_dir(&root).unwrap();}Paths{db:root.join(DB),root,mode:current}} fn clean(p:&Paths){let _=fs::remove_dir_all(&p.root);} fn hash(p:&Path)->String{let mut h=Sha256::new();h.update(fs::read(p).unwrap());format!("{:x}",h.finalize())}
 #[test] fn real_preexisting_database_is_rejected_before_write(){if mode().unwrap()!=InputMode::Real{return;}let p=test_paths("real-existing-db");fs::create_dir(&p.root).unwrap();fs::write(&p.db,b"not-a-sqlite-db").unwrap();let before=hash(&p.db);let error=capture(&p,&CaptureRequest{text:"安全测试".into(),key:"p3-141-real-ui-existing-db".into()}).unwrap_err();assert_eq!(error.code,"database_unavailable");assert_eq!(before,hash(&p.db));clean(&p);}
-#[test] fn status_is_closed_to_the_p3_139_twenty_ipc(){let p=paths().unwrap();let s=status(&p);assert_eq!(s.ipc_allowlist,IPC);assert_eq!(IPC.len(),20);assert!(!s.ai_enabled&&!s.filesystem&&!s.raw_database&&!s.generic_path_api&&!s.shell&&!s.process_spawn&&!s.network&&!s.vault&&!s.export&&!s.sync);assert_eq!(s.model_port,"replaceable_provider_explicit_only");assert_eq!(s.model_adapter,"four_profile_explicit_user_enabled_synthetic_loopback_only");assert_eq!(provider_profiles(),vec!["openai","anthropic","ollama","lm_studio"]);}
+#[test] fn status_is_closed_to_the_p3_139_twenty_ipc(){let p=paths().unwrap();let s=status(&p);assert_eq!(s.ipc_allowlist,IPC);assert_eq!(IPC.len(),20);assert!(!s.ai_enabled&&!s.filesystem&&!s.raw_database&&!s.generic_path_api&&!s.shell&&!s.process_spawn&&!s.network&&!s.vault&&!s.export&&!s.sync);assert_eq!(s.model_port,"replaceable_provider_explicit_only");assert_eq!(s.model_adapter,"five_profile_explicit_user_enabled_synthetic_loopback_only");assert_eq!(provider_profiles(),vec!["openai","anthropic","ollama","lm_studio","custom_openai_compatible"]);}
 #[test] fn receipt_geometry_requires_post_set_size_stability_and_never_reuses_another_viewport(){
     let desktop=ViewportGeometry{inner_width:1280,inner_height:949,outer_width:1280,outer_height:949,scale_factor:1.0};
     let compact=ViewportGeometry{inner_width:700,inner_height:760,outer_width:700,outer_height:760,scale_factor:1.0};
@@ -821,7 +823,7 @@
 }
 #[test] fn receipt_enabled_real_mode_requires_fresh_root_and_reopens_without_write(){if MODE != Some("real_self_use"){return;}assert_eq!(mode().unwrap(),InputMode::Real);let configured=paths().unwrap();assert!(metadata(&configured.root).unwrap().is_none());assert!(metadata(&configured.db).unwrap().is_none());let captured=capture(&configured,&CaptureRequest{text:"receipt-enabled synthetic fixture".into(),key:"p3-141-real-ui-receipt-enabled".into()}).unwrap();assert!(captured.record.id.starts_with(InputMode::Real.capture_prefix()));validate_existing_real_root(&configured).unwrap();let before=fs::read(&configured.db).unwrap();drop(read(&configured).unwrap());assert_eq!(before,fs::read(&configured.db).unwrap());fs::remove_dir_all(&configured.root).unwrap();}
 #[test] fn provider_settings_are_nonsecret_atomic_and_session_only(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-settings");let mut state=default_provider_state();let settings=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://api.example.test/v1".into(),model:"fixture-model".into(),temperature_bps:70,max_output_tokens:512,timeout_ms:30_000};let saved=save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:settings.clone()}).unwrap();assert!(!saved.enabled&&!saved.credential.present);set_provider_session_credential(&mut state,SessionCredentialRequest{credential:Some("SESSION_SECRET_DO_NOT_PERSIST".into()),environment_variable:None}).unwrap();let file=provider_settings_path(&p);let raw=fs::read_to_string(&file).unwrap();assert!(!raw.contains("SESSION_SECRET_DO_NOT_PERSIST"));let meta=fs::symlink_metadata(&file).unwrap();assert_eq!(meta.permissions().mode()&0o777,0o600);let reloaded=load_provider_state(&p).unwrap();assert_eq!(reloaded.settings,settings);assert!(!credential_status(&reloaded.credential).present);clean(&p);}
-#[test] fn provider_rejects_unsafe_endpoints_unsupported_profile_and_never_enables_stale_config(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-negative");let mut state=default_provider_state();for url in ["http://169.254.1.9/v1","http://224.0.0.1/v1","file:///tmp/not-allowed","https://user:pass@api.example.test/v1"]{let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:url.into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&settings).is_err());}let cloud_ip=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://127.0.0.1/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&cloud_ip).is_err());assert!(serde_json::from_str::<ProviderProfile>("\"custom_openai_compatible\"").is_err());let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:"http://127.0.0.1:11434/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings}).unwrap();assert_eq!(set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap_err().code,"provider_enablement_rejected");assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_connection_failed");assert!(!state.enabled);clean(&p);}
+#[test] fn provider_rejects_unsafe_endpoints_and_never_enables_stale_config(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-negative");let mut state=default_provider_state();for url in ["http://169.254.1.9/v1","http://224.0.0.1/v1","file:///tmp/not-allowed","https://user:pass@api.example.test/v1"]{let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:url.into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&settings).is_err());}let cloud_ip=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Openai,base_url:"https://127.0.0.1/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert!(validate_provider_settings(&cloud_ip).is_err());assert_eq!(serde_json::from_str::<ProviderProfile>("\"custom_openai_compatible\"").unwrap(),ProviderProfile::CustomOpenaiCompatible);let wrong_mode=ProviderSettings{mode:ProviderMode::Cloud,profile:ProviderProfile::Ollama,base_url:"https://api.example.test/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};assert_eq!(validate_provider_settings(&wrong_mode).unwrap_err().code,"provider_profile_mode_rejected");let settings=ProviderSettings{mode:ProviderMode::Local,profile:ProviderProfile::Ollama,base_url:"http://127.0.0.1:11434/v1".into(),model:"fixture-model".into(),temperature_bps:0,max_output_tokens:10,timeout_ms:1_000};save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings}).unwrap();assert_eq!(set_provider_enabled(&mut state,SetProviderEnabledRequest{enabled:true}).unwrap_err().code,"provider_enablement_rejected");assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_connection_failed");assert!(!state.enabled);clean(&p);}
 #[test] fn provider_understanding_requires_explicit_successful_enablement(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-understanding");let capture=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();let mut state=default_provider_state();let request=UnderstandingRequest{context_id:"request-local".into(),page:Page::Today,selection_ref:Some(capture.record.id),removed_context_kinds:None,request_id:"p3-137-test-explicit".into(),include_related_personal_content:None,additional_context_confirmed:None};assert!(provider_understanding(&p,&mut state,&request).unwrap().understanding_id.is_empty());assert_eq!(state.model_request_count,0);clean(&p);}
 #[test] fn disabled_provider_is_a_persisted_non_network_state(){if mode().unwrap()!=InputMode::Synthetic{return;}let p=test_paths("provider-disabled");let mut state=default_provider_state();let saved=save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:default_provider_settings()}).unwrap();assert_eq!(saved.connection_state,"disabled");assert_eq!(test_provider_connection(&p,&mut state,TestProviderConnectionRequest{cancel:None}).unwrap_err().code,"provider_disabled");assert_eq!(load_provider_state(&p).unwrap().connection_state,"disabled");clean(&p);}
 #[test] fn synthetic_lifecycle_and_no_write_rejection(){if mode().unwrap()==InputMode::Real{return;}let p=test_paths("synthetic");let c=capture(&p,&CaptureRequest{text:SYN_TEXT.into(),key:SYN_KEY.into()}).unwrap();assert_eq!(c.record_count,1);assert!(next(&p,&ContextRequest{context_id:CONTEXT.into()}).unwrap().candidates.is_empty());confirm(&p,&ConfirmRequest{capture_id:c.record.id,context_id:CONTEXT.into(),decision:LinkDecision::Confirm,idempotency_key:"p3-141-link-001".into()}).unwrap();let candidate=next(&p,&ContextRequest{context_id:CONTEXT.into()}).unwrap().candidates.remove(0);decide(&p,&NextRequest{candidate_id:candidate.candidate_id,decision:NextDecision::Accept,edited_text:None,idempotency_key:"p3-141-accept-001".into()}).unwrap();assert_eq!(today(&p).unwrap().confirmed_actions.len(),1);let before=hash(&p.db);assert_eq!(capture(&p,&CaptureRequest{text:"bad".into(),key:"bad".into()}).unwrap_err().code,"argument_schema_rejected");assert_eq!(before,hash(&p.db));clean(&p);}
@@ -872,6 +874,80 @@
 
     #[test]
     fn settings_link_temp_and_failure_preserve_db_sentinel() { use std::os::unix::fs::symlink; let p=test_paths("settings-boundary"); let mut state=default_provider_state(); let setting=settings(19001,ProviderProfile::Ollama); save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting.clone()}).unwrap(); let settings_file=provider_settings_path(&p); let original=fs::read(&settings_file).unwrap(); let sentinel=p.root.join("db-sentinel"); fs::write(&sentinel,b"p3-136 synthetic sentinel").unwrap(); let sentinel_before=fs::read(&sentinel).unwrap(); let temporary=p.root.join(".ai-provider-settings.tmp"); fs::write(&temporary,b"unexpected temp").unwrap(); assert_eq!(save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting.clone()}).unwrap_err().code,"provider_settings_file_rejected"); assert_eq!(original,fs::read(&settings_file).unwrap()); assert_eq!(sentinel_before,fs::read(&sentinel).unwrap()); fs::remove_file(&temporary).unwrap(); fs::remove_file(&settings_file).unwrap(); let target=p.root.join("not-a-settings-file"); fs::write(&target,b"synthetic").unwrap(); symlink(&target,&settings_file).unwrap(); assert_eq!(save_provider_settings(&p,&mut state,SaveProviderSettingsRequest{settings:setting}).unwrap_err().code,"provider_settings_file_rejected"); assert_eq!(sentinel_before,fs::read(&sentinel).unwrap()); fs::remove_dir_all(&p.root).unwrap(); }
+}
+
+#[cfg(test)]
+mod provider_restoration_tests {
+    use super::*;
+    use std::net::TcpListener;
+    use std::thread;
+
+    fn fixture(replies: Vec<String>) -> (u16, thread::JoinHandle<Vec<String>>) {
+        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
+        let port = listener.local_addr().unwrap().port();
+        let handle = thread::spawn(move || {
+            let mut requests = Vec::new();
+            for reply in replies {
+                let (mut stream, _) = listener.accept().unwrap();
+                let mut raw = vec![0_u8; 16_384];
+                let count = stream.read(&mut raw).unwrap();
+                requests.push(String::from_utf8_lossy(&raw[..count]).into_owned());
+                stream.write_all(reply.as_bytes()).unwrap();
+            }
+            requests
+        });
+        (port, handle)
+    }
+
+    fn reply(body: &str) -> String {
+        format!("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", body.len())
+    }
+
+    #[test]
+    fn custom_openai_compatible_loopback_is_protocol_bound_and_first_send_locks() {
+        if mode().unwrap() != InputMode::Synthetic { return; }
+        let base = paths().unwrap().root;
+        let root = base.join(format!("provider-restoration-custom-{}", now().unwrap()));
+        fs::create_dir(&root).unwrap();
+        let paths = Paths { db: root.join(DB), root, mode: InputMode::Synthetic };
+        let capture = capture(&paths, &CaptureRequest { text: SYN_TEXT.into(), key: SYN_KEY.into() }).unwrap();
+        let evidence_ref = format!("capture:{}", capture.record.id);
+        let inner = serde_json::json!({"kind":"suggestion","summary":"synthetic custom provider result","uncertainty":"synthetic_fixture","evidence_refs":[evidence_ref]}).to_string().replace('"', "\\\"");
+        let response = format!(r#"{{"choices":[{{"message":{{"content":"{inner}"}}}}]}}"#);
+        let (port, handle) = fixture(vec![
+            reply(r#"{"object":"list","data":[{"id":"fixture-model"}]}"#),
+            reply(&response),
+        ]);
+        let custom = ProviderSettings { mode: ProviderMode::Local, profile: ProviderProfile::CustomOpenaiCompatible, base_url: format!("http://127.0.0.1:{port}/fixture"), model: "fixture-model".into(), temperature_bps: 70, max_output_tokens: 256, timeout_ms: 1_000 };
+        let mut state = default_provider_state();
+        save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: custom.clone() }).unwrap();
+        assert_eq!(test_provider_connection(&paths, &mut state, TestProviderConnectionRequest { cancel: None }).unwrap().provider, "custom_openai_compatible");
+        set_provider_enabled(&mut state, SetProviderEnabledRequest { enabled: true }).unwrap();
+        let request = UnderstandingRequest { context_id: "request-local".into(), page: Page::Today, selection_ref: Some(capture.record.id), removed_context_kinds: None, request_id: "p3-137-provider-restoration-custom".into(), include_related_personal_content: None, additional_context_confirmed: None };
+        assert!(provider_understanding(&paths, &mut state, &request).unwrap().suggestion.is_some());
+        assert_eq!(state.locked_profile, Some(ProviderProfile::CustomOpenaiCompatible));
+        let switched = ProviderSettings { profile: ProviderProfile::LmStudio, ..custom };
+        assert_eq!(save_provider_settings(&paths, &mut state, SaveProviderSettingsRequest { settings: switched }).unwrap_err().code, "provider_locked_after_first_send");
+        let requests = handle.join().unwrap();
+        assert_eq!(requests.len(), 2);
+        assert!(requests[0].contains("GET /fixture/v1/models"));
+        assert!(requests[1].contains("POST /fixture/v1/chat/completions"));
+        assert_eq!(state.model_request_count, 1);
+        fs::remove_dir_all(&paths.root).unwrap();
+    }
+
+    #[test]
+    fn custom_profile_rejects_wrong_envelope_response_mode_and_credential_order() {
+        let custom = ProviderProfile::CustomOpenaiCompatible;
+        let port = model_port(custom);
+        assert_eq!(port.parse_models(&serde_json::json!({"models":["fixture-model"]})).unwrap_err().code, "provider_protocol_rejected");
+        assert_eq!(parse_provider_output(custom, br#"{"message":{"content":"wrong"}}"#).unwrap_err().code, "provider_protocol_mismatch");
+        let wrong_mode = ProviderSettings { mode: ProviderMode::Cloud, profile: ProviderProfile::Ollama, base_url: "https://fixture.lifeos.test:1/v1".into(), model: "fixture-model".into(), temperature_bps: 0, max_output_tokens: 1, timeout_ms: 1_000 };
+        assert_eq!(validate_provider_settings_for(&wrong_mode, InputMode::Synthetic).unwrap_err().code, "provider_profile_mode_rejected");
+        let mut state = default_provider_state();
+        let disabled = set_provider_enabled(&mut state, SetProviderEnabledRequest { enabled: true }).unwrap_err();
+        assert_eq!(disabled.code, "provider_enablement_rejected");
+    }
 }
 
 #[cfg(test)]
## ui/runtime-adapter.js
--- /Users/xxe/.codex/worktrees/971c/No.2/lifeos/engineering/LIFEOS-P3-141/candidate/ui/runtime-adapter.js	2026-08-30 13:33:28
+++ /Users/xxe/.codex/worktrees/971c/No.2/lifeos/engineering/LIFEOS-P3-141/closure-provider-restoration/candidate/ui/runtime-adapter.js	2026-08-30 17:23:59
@@ -263,7 +263,7 @@
     const displayMode = setting.mode === "local" ? "local" : "cloud";
     const cloudMode = displayMode === "cloud";
     const option = (value, label) => `<option value="${value}" ${setting.profile === value ? "selected" : ""}>${label}</option>`;
-    const profiles = cloudMode ? `${option("openai", "OpenAI")}${option("anthropic", "Anthropic")}` : `${option("ollama", "Ollama")}${option("lm_studio", "LM Studio")}`;
+    const profiles = cloudMode ? `${option("openai", "OpenAI")}${option("anthropic", "Anthropic")}${option("custom_openai_compatible", "DeepSeek、Kimi 或 OpenAI-compatible 服务")}` : `${option("ollama", "Ollama")}${option("lm_studio", "LM Studio")}${option("custom_openai_compatible", "本地兼容服务")}`;
     const stateLabel = ({ not_configured: "未配置", not_tested: "未测试", not_tested_after_restart: "需要重新测试", testing: "测试中", connected: "已连接", failed: "失败", disabled: "已停用" })[provider.connection_state] || "未测试";
     const models = Array.isArray(provider.discovered_models) ? provider.discovered_models : [];
     const selectedModel = models.includes(runtime.pendingModel) ? runtime.pendingModel : models.includes(setting.model) ? setting.model : "";
@@ -277,7 +277,7 @@
     const modelAction = active ? '<button class="button model-current-action" type="button" disabled>✓ 当前正在使用</button>' : selectedModel ? '<button class="button primary" type="button" data-action="provider:model-select">启用此模型</button>' : '<button class="button" type="button" disabled>先测试并选择模型</button>';
     const credential = cloudMode ? `<label class="span-2 credential-field">API Key<input name="provider-credential" type="password" autocomplete="new-password" placeholder="${keyPresent ? "本次会话 API Key 已提供；输入可更新" : "输入 API Key"}"></label>` : '<div class="span-2 local-connection-note"><strong>本地模型不需要 API Key</strong><span>仅连接到你选择的 loopback 或私有局域网模型服务。</span></div>';
     root.innerHTML = `<header class="page-header provider-header"><div><h1>模型设置</h1><p>配置 LifeOS 使用的云端或本地模型。</p></div></header>
-      <section class="panel provider-panel provider-mode-panel"><div class="settings-card-head"><div><span class="section-label">运行模式</span><p>先选择连接方式，再配置并测试。</p></div></div><div class="mode-cards" role="radiogroup" aria-label="运行模式">${modeCard("cloud", "☁", "云端模型", "OpenAI 或 Anthropic")}${modeCard("local", "▣", "本地模型", "Ollama 或 LM Studio")}</div></section>
+      <section class="panel provider-panel provider-mode-panel"><div class="settings-card-head"><div><span class="section-label">运行模式</span><p>先选择连接方式，再配置并测试。</p></div></div><div class="mode-cards" role="radiogroup" aria-label="运行模式">${modeCard("cloud", "☁", "云端模型", "OpenAI、Anthropic、DeepSeek、Kimi 或 OpenAI-compatible 服务")}${modeCard("local", "▣", "本地模型", "Ollama、LM Studio 或本地兼容服务")}</div></section>
       <div class="provider-layout"><div class="provider-left stack"><section class="panel provider-panel provider-connection-card"><div class="settings-card-head"><div><span class="section-label">连接配置</span><p>填写连接信息后手动测试；测试不发送个人 Context。</p></div><span class="mode-chip">${cloudMode ? "云端" : "本地"}</span></div><div class="provider-grid"><label>Provider<select name="provider-profile">${profiles}</select></label><label>接口地址<input name="provider-base-url" value="${clean(setting.base_url)}" autocomplete="off" spellcheck="false" placeholder="${cloudMode ? "https://api.example.com" : "http://127.0.0.1:11434"}"></label>${credential}</div><p class="session-boundary-note"><span aria-hidden="true">✓</span>${cloudMode ? (keyPresent ? "API Key 仅保留在本次会话，可随时清除。" : "API Key 仅保留在本次会话，关闭应用即删除。") : "本地连接不会索取或保存 API Key。"}</p><div class="actions"><button class="button primary" type="button" data-action="provider:setup-test">保存并测试连接</button>${cloudMode && keyPresent ? '<button class="button danger-quiet" type="button" data-action="provider:clear-credential">清除本次会话 API Key</button>' : ""}</div></section>
         <section class="panel provider-panel connection-status" data-provider-state="${clean(provider.connection_state)}"><div class="settings-card-head"><div><span class="section-label">连接状态</span><p>手动测试后显示可用模型。</p></div></div><div class="connection-metrics"><div><span>状态</span><strong class="${provider.connection_state === "connected" ? "status-ok" : ""}">${stateLabel}</strong></div><div><span>延迟</span><strong>${provider.last_latency_ms == null ? "—" : `${provider.last_latency_ms} ms`}</strong></div><div><span>最近检查</span><strong>${checkedAt}</strong></div></div><p class="tiny">连接测试不发送个人 Context。</p></section></div>
         <aside class="stack"><section class="panel provider-panel current-model-card"><div class="settings-card-head"><div><span class="section-label">当前启用模型</span><p>从刚刚测试成功的接口返回结果中选择。</p></div>${active ? '<span class="pill mint">正在使用</span>' : ""}</div><div class="active-model-display"><span>${active ? `${clean(setting.model)} · ${clean(setting.profile)}` : "尚未选择模型"}</span>${active ? '<span class="pill mint">正在使用</span>' : '<span class="pill">未启用</span>'}</div><label class="model-input">可用模型<select name="provider-model" ${models.length ? "" : "disabled"}>${modelOptions}</select></label><div class="actions model-enable-action">${modelAction}</div></section><details class="panel provider-panel advanced-settings"><summary><span>高级参数</span><small>可选</small></summary><div class="advanced-grid"><label>温度<input name="provider-temperature" type="number" min="0" max="2" step="0.01" value="${(setting.temperature_bps / 100).toFixed(2)}"><input name="provider-temperature-range" type="range" min="0" max="2" step="0.01" value="${(setting.temperature_bps / 100).toFixed(2)}"></label><label>最大输出 Token<input name="provider-max-tokens" type="number" min="1" max="8192" step="1" value="${setting.max_output_tokens}"><input name="provider-max-tokens-range" type="range" min="1" max="8192" step="1" value="${setting.max_output_tokens}"></label><label>请求超时时间<input name="provider-timeout" type="number" min="1" max="120" step="1" value="${Math.round(setting.timeout_ms / 1000)}"><input name="provider-timeout-range" type="range" min="1" max="120" step="1" value="${Math.round(setting.timeout_ms / 1000)}"></label></div></details></aside></div>`;
