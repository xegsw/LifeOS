"""Synthetic checks only; preserves every run. No GUI/network/credentials/cleanup."""
from pathlib import Path
import os,sys,subprocess,datetime,json
base=Path(__file__).resolve().parents[2];candidate=base/'candidate'
root=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1')
node=Path('/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
python=Path('/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3')
cargo=Path('/Users/xxe/.cargo/bin/cargo')
subprocess.run([sys.executable,'-B',str(candidate/'tools/task_root.py'),'init'],check=True)
run=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=base/'evidence'/('checks-'+run);out.mkdir()
env={**os.environ,'TMPDIR':str(root/'tmp'),'CARGO_TARGET_DIR':str(root/'initial-build-cache'),'LIFEOS_P3_147_PROFILE':'synthetic','PYTHONDONTWRITEBYTECODE':'1'}
steps=[('format',[str(cargo),'fmt','--manifest-path',str(candidate/'Cargo.toml'),'--','--check']),('build',[str(cargo),'build','--locked','--offline','--manifest-path',str(candidate/'Cargo.toml')]),('rust',[str(cargo),'test','--locked','--offline','--manifest-path',str(candidate/'Cargo.toml'),'--','--test-threads=1']),('parser',[str(python),'-B',str(candidate/'tests/parsers.py')]),('web',[str(node),'--test',str(candidate/'tests/web_source.mjs')]),('inherited',[str(node),'--test',str(candidate/'tests/integration.mjs')])]
results=[]
for name,args in steps:
 with (out/(name+'.log')).open('xb') as log:code=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
 results.append({'name':name,'exit_code':code})
 (out/'results.json').write_text(json.dumps({'scope':'internal synthetic checks; public IPC pending approval; not full engineering Pass','steps':results},indent=2))
 if code:sys.exit(code)
print(str(out/'results.json'))
