#!/usr/bin/env python3
"""Mutate fresh 155 copies only. Expected tests must compile, execute, and fail."""
from pathlib import Path
import os,json,shutil,subprocess,uuid,hashlib
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-155-source-update-v1')
assert json.loads((root/'.owner.json').read_text())['task']=='P3-155'
os.umask(0o077);out=root/'mutations'/str(uuid.uuid4());out.mkdir(parents=True)
env=dict(os.environ,LIFEOS_P3_155_MODE='synthetic',CARGO_TARGET_DIR=str(root/'target'),TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
cases=[
 ('content-reuse','source-engine/src/source_worker.rs','hash == &fingerprint','false','source_update_unchanged_metadata_changed_missing_pause_restart_idempotency_and_revoke'),
 ('late-worker-error','source-engine/src/source_api.rs',"AND epoch=?2 AND state='active'", "AND ?2 IS NOT NULL AND state='active'", 'source_restart_status_and_late_worker_error_are_owned'),
 ('missing-status-migration','source-engine/src/apple_health_api.rs','fn status_table(c:&rusqlite::Connection)->Result<(),Error>{','fn status_table(c:&rusqlite::Connection)->Result<(),Error>{c.execute_batch("CREATE TABLE IF NOT EXISTS health_import_status(id INTEGER PRIMARY KEY,value TEXT)")?;','import_status_missing_schema_is_not_migrated'),
 ('confirmation-token','src/health_conversation_host/controlled.rs','||v["confirmationToken"]!=d.confirmation_token','','forged_confirmation_token_never_dispatches'),
 ('state-expiry','src/health_conversation_host.rs','s["validUntil"].as_i64().unwrap_or(0)<=now()','false','c1_expired_state_blocks_confirm_before_adapter_call'),
 ('remote-key-echo','src/health_conversation_host/controlled.rs','!secret.is_empty()&&response.text.contains(secret)','false','remote_key_echo_is_never_persisted_or_returned'),
 ('existing-root','src/runtime_root.rs','for n in ["conversation.sqlite","provider.sqlite"]','for n in ["conversation.sqlite"]','missing_existing_database_is_never_rebuilt'),
 ('legacy-account','src/secure_credentials.rs','reference_has_exact_generated_suffix(reference, P3_145_REFERENCE_PREFIX)','reference_has_exact_generated_suffix(reference, P3_145_REFERENCE_PREFIX) || reference_has_exact_generated_suffix(reference, P3_144_REFERENCE_PREFIX)','legacy_and_malformed_accounts_never_reach_keychain'),
]
results=[]
for name,file,old,new,test in cases:
 c=out/name;shutil.copytree(b/'candidate',c);p=c/file;s=p.read_text();assert old in s,(name,'mutation target absent');p.write_text(s.replace(old,new,1))
 cmd=['/Users/xxe/.cargo/bin/cargo','test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(c/'Cargo.toml'),test,'--','--test-threads=1']
 r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=600);(out/f'{name}.stdout').write_text(r.stdout);(out/f'{name}.stderr').write_text(r.stderr)
 killed=r.returncode!=0 and 'test result: FAILED' in r.stdout and '1 failed' in r.stdout
 results.append({'mutation':name,'test':test,'killed':killed,'exitCode':r.returncode});print(name,killed,flush=True)
 if not killed:break
(out/'results.json').write_text(json.dumps({'results':results,'allKilled':len(results)==len(cases) and all(r['killed'] for r in results)},indent=2)+'\n');print(out)
raise SystemExit(not(len(results)==len(cases) and all(r['killed'] for r in results)))
