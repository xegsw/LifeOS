"""Rebuild and test only P3-156 under its exact pre-owned synthetic root."""
from pathlib import Path
import os,json,subprocess,stat,uuid
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-156-next-action-v1');os.umask(0o077)
assert stat.S_IMODE(root.lstat().st_mode)==0o700 and not root.is_symlink()
assert json.loads((root/'.owner.json').read_text())=={'task':'P3-156','root':str(root),'thread':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484'}
out=root/'reruns'/str(uuid.uuid4());out.mkdir(parents=True,mode=0o700)
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo';env=dict(os.environ,LIFEOS_P3_156_MODE='synthetic',CARGO_TARGET_DIR=str(root/'target'),TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
steps=[('build',[cargo,'build','--locked','--offline','--features','synthetic-driver','--manifest-path',str(b/'candidate/Cargo.toml')]),('rust',[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(b/'candidate/Cargo.toml'),'--','--test-threads=1']),('actions',[node,'--test',str(b/'tests/actions.mjs')]),('ui',[node,'--test',*[str(b/'tools'/n) for n in ['settings_tests.mjs','health_view_tests.mjs','sources_ui_tests.mjs']]]),('integration',[node,str(b/'tools/integration_tests.mjs')]),('combined',[node,str(b/'tools/combined_tests.mjs')]),('continuity',[node,str(b/'tests/continuity.mjs')]),('freshness',[node,str(b/'tests/freshness.mjs')]),('ui-recovery',[node,'--test',*[str(b/'tests'/n) for n in ['clarification_ui.mjs','error_diagnostics.mjs','flow_races.mjs','source_recovery.mjs','source_process_recovery.mjs']]])]
results=[]
for name,cmd in steps:
 with (out/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 results.append({'step':name,'exitCode':r.returncode});print(name,r.returncode,flush=True)
 if r.returncode:break
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(str(out));raise SystemExit(any(r['exitCode'] for r in results))
