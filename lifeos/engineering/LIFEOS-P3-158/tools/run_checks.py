from pathlib import Path
import os,subprocess,json
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-158-main-chain-v1/offline');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())=={'task':'P3-158','root':str(root),'owner':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484','mode':'synthetic'}
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo';env=dict(os.environ,LIFEOS_P3_158_MODE='synthetic',CARGO_TARGET_DIR='/private/tmp/lifeos-p3-158-main-chain-v1/build/offline',TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
steps=[('build',[cargo,'build','--locked','--offline','--features','synthetic-driver','--manifest-path',str(b/'candidate/Cargo.toml')]),('rust',[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(b/'candidate/Cargo.toml'),'--','--test-threads=1']),('actions',[node,'--test',str(b/'tests/actions.mjs')]),('operation-flow',[node,'--test',str(b/'tests/operation_flow.mjs')]),('operation-ipc',[node,'--test',str(b/'tests/operation_ipc.mjs')]),('closure-cases',[node,'--test',str(b/'tests/closure_cases.mjs')]),('real-local',[node,'--test',str(b/'tests/real_local_routing.mjs')]),('ui',[node,'--test',*[str(b/'tools'/n) for n in ['settings_tests.mjs','health_view_tests.mjs','sources_ui_tests.mjs']]]),('integration',[node,str(b/'tools/integration_tests.mjs')]),('combined',[node,str(b/'tools/combined_tests.mjs')]),('continuity',[node,str(b/'tests/continuity.mjs')]),('clarification-ui',[node,'--test',str(b/'tests/clarification_ui.mjs')]),('error-diagnostics',[node,'--test',str(b/'tests/error_diagnostics.mjs')]),('flow-races',[node,'--test',str(b/'tests/flow_races.mjs')]),('source-recovery',[node,'--test',str(b/'tests/source_recovery.mjs'),str(b/'tests/source_process_recovery.mjs')]),('freshness',[node,str(b/'tests/freshness.mjs')])]
results=[]
for name,cmd in steps:
 with (b/f'evidence/{name}-final.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 results.append({'step':name,'exitCode':r.returncode});print(name,r.returncode,flush=True)
 if r.returncode:break
(b/'evidence/regression-results.json').write_text(json.dumps(results,indent=2)+'\n');raise SystemExit(any(r['exitCode'] for r in results))
