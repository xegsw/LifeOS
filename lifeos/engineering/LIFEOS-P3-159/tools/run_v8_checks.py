from pathlib import Path
import os,subprocess,json,datetime,argparse,shutil,sys
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1/offline');os.umask(0o077)
subprocess.run([sys.executable,str(b/'tools/prepare_offline.py')],check=True)
assert json.loads((root/'.owner.json').read_text())=={'task':'P3-159','root':str(root),'owner':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484','mode':'synthetic'}
run_dir=b/'evidence'/('A-run-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'));run_dir.mkdir()
node=shutil.which('node') or '/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo=shutil.which('cargo') or str(Path.home()/'.cargo/bin/cargo');env=dict(os.environ,LIFEOS_P3_159_MODE='synthetic',CARGO_TARGET_DIR='/private/tmp/lifeos-p3-159-unified-proactive-v1/build/offline',TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
steps=[('native-playback',['python3',str(b/'tools/verify_native_playback.py')]),('fixtures',['python3',str(b/'tools/prepare_fixtures.py')]),('ui-build',[node,str(b/'tools/build_ui.mjs')]),('build',[cargo,'build','--locked','--offline','--features','synthetic-driver','--manifest-path',str(b/'candidate/Cargo.toml')]),('rust',[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(b/'candidate/Cargo.toml'),'--','--test-threads=1']),('proactive-ui',[node,'--test',str(b/'tests/proactive_ui.mjs')]),('legacy-import-health',[node,'--test',str(b/'candidate/tools/test_apple_ui.mjs'),str(b/'candidate/tools/test_health_ui.mjs')]),('interaction-ui',[node,'--test',str(b/'tests/interaction.mjs'),str(b/'tests/voice_integration.mjs')]),('actions',[node,'--test',str(b/'tests/actions.mjs')]),('coordination-ipc',[node,'--test',str(b/'tests/coordination_ipc.mjs')]),('coordination-receipt',[node,'--test',str(b/'tests/coordination_receipt.mjs')]),('operation-flow',[node,'--test',str(b/'tests/operation_flow.mjs')]),('operation-ipc',[node,'--test',str(b/'tests/operation_ipc.mjs')]),('closure-cases',[node,'--test',str(b/'tests/closure_cases.mjs')]),('real-local',[node,'--test',str(b/'tests/real_local_routing.mjs')]),('ui',[node,'--test',*[str(b/'tools'/n) for n in ['settings_tests.mjs','health_view_tests.mjs','sources_ui_tests.mjs']]]),('integration',[node,str(b/'tools/integration_tests.mjs')]),('combined',[node,str(b/'tools/combined_tests.mjs')]),('continuity',[node,str(b/'tests/continuity.mjs')]),('clarification-ui',[node,'--test',str(b/'tests/clarification_ui.mjs')]),('error-diagnostics',[node,'--test',str(b/'tests/error_diagnostics.mjs')]),('flow-races',[node,'--test',str(b/'tests/flow_races.mjs')]),('source-recovery',[node,'--test',str(b/'tests/source_recovery.mjs'),str(b/'tests/source_process_recovery.mjs')]),('freshness',[node,str(b/'tests/freshness.mjs')])]
parser=argparse.ArgumentParser();parser.add_argument('--steps',help='Comma-separated affected steps; default is complete offline regression');parser.add_argument('--rust-filter',default='');args=parser.parse_args()
if args.steps:
 selected=args.steps.split(',');unknown=set(selected)-{n for n,_ in steps}
 if unknown:parser.error('unknown step')
 steps=[(n,c) for n,c in steps if n in selected]
if args.rust_filter:
 for n,c in steps:
  if n=='rust':c.insert(c.index('--'),args.rust_filter)
results=[]
for name,cmd in steps:
 with (run_dir/f'{name}.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 results.append({'step':name,'exitCode':r.returncode,'log':str(run_dir/f'{name}.log')});print(name,r.returncode,flush=True)
 if r.returncode:break
(b/'evidence/A-regression-results.json').write_text(json.dumps(results,indent=2)+'\n');raise SystemExit(any(r['exitCode'] for r in results))
