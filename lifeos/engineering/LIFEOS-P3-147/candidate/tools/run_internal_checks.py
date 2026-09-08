"""Synthetic checks only; preserves every run. No GUI/network/credentials/cleanup."""
from pathlib import Path
import os,sys,subprocess,datetime,json
base=Path(__file__).resolve().parents[2];candidate=base/'candidate'
from task_root import ROOT as root,PROFILE
node=Path('/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
python=Path('/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3')
cargo=Path('/Users/xxe/.cargo/bin/cargo')
subprocess.run([sys.executable,'-B',str(candidate/'tools/task_root.py'),'init'],check=True)
if not (root/'fixtures/app-source').exists():subprocess.run([sys.executable,'-B',str(candidate/'tools/seed_source_fixture.py')],check=True)
run=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=base/'evidence'/('checks-'+run);out.mkdir()
env={**os.environ,'TMPDIR':str(root/'tmp'),'CARGO_TARGET_DIR':str(root/'initial-build-cache'),'LIFEOS_P3_147_PROFILE':'synthetic','PYTHONDONTWRITEBYTECODE':'1'}
steps=[('ui_build',[str(node),str(candidate/'tools/build_ui.mjs')]),('alias_helper',['/usr/bin/swiftc','-module-cache-path',str(root/'swift-cache'),str(candidate/'tools/alias_metadata.swift'),'-o',str(root/'alias_metadata')]),('alias_fixture',['/usr/bin/swiftc','-module-cache-path',str(root/'swift-cache'),str(candidate/'tests/create_alias.swift'),'-o',str(root/'create_test_alias')]),('format',[str(cargo),'fmt','--manifest-path',str(candidate/'Cargo.toml'),'--','--check']),('build',[str(cargo),'build','--locked','--offline','--manifest-path',str(candidate/'Cargo.toml')]),('real_entry_ui',[str(node),str(candidate/'tests/real_entry_ui.mjs')]),('entry_flow',[str(node),str(candidate/'tests/source_entry.mjs')]),('rust',[str(cargo),'test','--locked','--offline','--manifest-path',str(candidate/'Cargo.toml'),'--','--test-threads=1']),('parser',[str(python),'-B',str(candidate/'tests/parsers.py')]),('web',[str(node),'--test',str(candidate/'tests/web_source.mjs')]),('inherited',[str(node),'--test',str(candidate/'tests/integration.mjs')]),('target_boundaries',[str(python),'-B',str(candidate/'tools/test_target_boundaries.py')]),('root_profiles',[str(python),'-B',str(candidate/'tools/test_root_profiles.py')]),('public_api',[str(python),'-B',str(candidate/'tools/test_source_api.py')])]
if len(sys.argv)>1:
 selected=set(sys.argv[1].split(','));assert selected<=set(n for n,_ in steps);steps=[(n,a) for n,a in steps if n in selected]
results=[]
for name,args in steps:
 with (out/(name+'.log')).open('xb') as log:code=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
 results.append({'name':name,'exit_code':code})
 (out/'results.json').write_text(json.dumps({'scope':'approved synthetic engineering checks; independent security and real-user gates separate','steps':results},indent=2))
 if code:sys.exit(code)
print(str(out/'results.json'))
