"""A-only semantic mutations in new task-owned copies; canonical candidate is read-only."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,argparse
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())==dict(task='P3-159',root=str(root),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(path):return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file()}
candidate=b/'candidate';before=hashes(candidate);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');out=b/'evidence'/('A-mutations-'+stamp);out.mkdir();workspace=root/'offline'/'mutations'/stamp;workspace.mkdir(parents=True)
cases=[
 ('suppression-bypass','src/health_conversation_host/proactive.rs','fn suppressed(c: &Connection, subjects: &[String], at: i64) -> R<bool> {','fn suppressed(c: &Connection, subjects: &[String], at: i64) -> R<bool> { return Ok(false);','proactive_control_history_never_hides_permanent_suppression'),
 ('conversation-revocation-bypass','src/health_conversation_host/proactive.rs','if !enabled(c,"conversation")? {return Ok(None)}','if false {return Ok(None)}','proactive_due_action_rechecks_completed_cancelled_expired_and_revoked_after_reopen'),
 ('real-cache-mode-bypass','src/health_conversation_host/coordination.rs','real_local::validate(&t,false)?;','/* A mutation: omitted persisted mode validation */','real_local_old_synthetic_receipt_cannot_replay_resume_or_project'),
 ('late-constraint-bypass','src/health_conversation_host/proactive.rs','if plan["constraintSnapshot"]!=json!(current_constraints(c,&subjects,at)?){return Err(error("proactive_context_stale"))}','if false{return Err(error("proactive_context_stale"))}','proactive_response_rechecks_changed_current_constraints')]
cases += [
 ('credential-native-grant-bypass','src/credential_recovery.rs','if self.state!="awaiting_user"||self.token!=token{return false}','if false{return false}','credential_check_native_grant_is_single_use_and_cannot_be_forged'),
 ('credential-late-binding-bypass','src/credential_recovery.rs','if self.binding!=*binding{self.cancel("binding_changed");return}','if false{self.cancel("binding_changed");return}','credential_check_cancel_timeout_and_changed_binding_discard_late_result')]
cases.append(('credential-raw-profile-regression','src/credential_recovery.rs','let p=s.provider_view()?;','let p=crate::provider_store::settings(&s.fixture())?;','credential_check_binds_effective_lifecycle_not_raw_legacy_enabled_field'))
cases += [
 ('credential-worker-diagnostic-loss','src/host_gateway.rs','let diagnostic=crate::secure_credentials::ReadDiagnostic::capture();','let diagnostic=crate::secure_credentials::ReadDiagnostic::new("configuration_binding",None);','proactive_credential_worker_diagnostic_reaches_noncontent_receipt'),
 ('credential-interaction-status-loss','src/secure_credentials.rs','if status == -25308 {CredentialFailure::KeychainInteractionRequired}','if status == -25308 {read_stage("configuration_binding",None);CredentialFailure::KeychainInteractionRequired}','credential_diagnostic_records_interaction_and_other_os_failures'),
 ('credential-receipt-diagnostic-loss','src/health_conversation_host/proactive.rs','r["credentialDiagnostic"]=d.value();','let _=d;','proactive_credential_worker_diagnostic_reaches_noncontent_receipt')]
cases += [
 ('voice-joint-session-recheck-loss','src/health_conversation_host/voice_host.rs','self.store.voice_session(&b.session_id,b.generation,b.policy_revision).map_err(|_|"voice_session_not_authorized")?;','/* mutation omits current session recheck */','voice_joint_registry_rechecks_cancel_transport_and_retain_budget'),
 ('voice-joint-final-handoff-loss','src/health_conversation_host/voice_host.rs','crate::voice::gateway::Outcome::Final(text)=>self.voice_final_turn(id,&text).map(Some)','crate::voice::gateway::Outcome::Final(_text)=>Ok(None)','voice_joint_only_complete_gateway_final_enters_one_existing_preview')]
cases += [
 ('voice-speech-visibility-loss','src/health_conversation_host/voice_speech.rs','if !visible_now{return Err(error("speech_projection_stale"))}','if false{return Err(error("speech_projection_stale"))}','proactive_speech_requires_current_surface_visibility_and_rechecks_before_sink'),
 ('voice-speech-cancel-asr-regression','src/health_conversation_host/voice_speech.rs','g.cancel(Purpose::Tts,net);','g.cancel_all(net);','voice_speech_interrupt_preserves_concurrent_asr_and_stale_stop_cannot_cancel_new_output'),
 ('voice-speech-eof-completion-regression','src/health_conversation_host/voice_speech.rs','self.voice_speech_state(id,"draining")?;Ok(Outcome::Complete)','self.voice_speech_state(id,"complete")?;Ok(Outcome::Complete)','voice_speech_pcm_rechecked_at_sink_and_eof_is_not_playback_completion')]
cases += [
 ('voice-playback-stale-feedback-regression','src/health_conversation_host/voice_playback.rs','if f.generation!=self.native_epoch{continue}','if false{continue}','voice_playback_old_feedback_revocation_and_overflow_cannot_complete_current'),
 ('voice-playback-early-seal-regression','src/health_conversation_host/voice_playback.rs','self.eof&&self.local.queued()==0&&!self.sealed','self.eof&&!self.sealed','voice_playback_backpressure_delays_seal_until_all_local_pcm_is_accepted')]
parser=argparse.ArgumentParser();parser.add_argument('--cases');args=parser.parse_args()
if args.cases:
 wanted=set(args.cases.split(','));assert wanted <= {c[0] for c in cases};cases=[c for c in cases if c[0] in wanted]
(out/'design.json').write_text(json.dumps({'source':before,'cases':[{'id':x[0],'file':x[1],'test':x[4]} for x in cases],'expected':'baseline passes; each mutation must fail assertion, not compilation; no network'},indent=2)+'\n')
env=dict(os.environ,LIFEOS_P3_159_MODE='synthetic',CARGO_TARGET_DIR=str(root/'build/mutation-check'),TMPDIR=str(root/'offline/tmp'),CARGO_NET_OFFLINE='true')
results=[]
for label,file,old,new,test in cases:
 dest=workspace/label/'candidate';shutil.copytree(candidate,dest);(dest.parent/'tests').mkdir();shutil.copy2(b/'tests/interaction_v1_fixtures.json',dest.parent/'tests/interaction_v1_fixtures.json');p=dest/file;s=p.read_text();assert old in s;s=s.replace(old,new,1);p.write_text(s)
 command=['/Users/xxe/.cargo/bin/cargo','test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(dest/'Cargo.toml'),test,'--','--test-threads=1']
 log=out/(label+'.log')
 with log.open('w') as f:r=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 text=log.read_text();killed=r.returncode!=0 and 'test result: FAILED' in text and 'panicked at' in text and 'could not compile' not in text
 results.append({'id':label,'test':test,'exitCode':r.returncode,'killedByAssertion':killed,'log':str(log),'mutatedSha256':sha(p)});print(label,killed,flush=True)
assert hashes(candidate)==before
(out/'results.json').write_text(json.dumps({'results':results,'canonicalUnchanged':True,'runtime':'offline synthetic only'},indent=2)+'\n')
raise SystemExit(not all(r['killedByAssertion'] for r in results))
