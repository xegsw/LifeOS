#!/usr/bin/env python3
"""P3-153 offline regression, only the already-owned contract runtime."""
from pathlib import Path
import os,json,subprocess,stat,sys,shutil,uuid,hashlib
base=Path(__file__).resolve().parents[1]
root=Path('/private/tmp/lifeos-p3-153-continuous-understanding-v1')
os.umask(0o077)
if '--init' in sys.argv:
 # Exclusive creation. An existing root is never read or overwritten by init.
 root.mkdir(mode=0o700)
 owner={'task':'P3-153','root':str(root),'owner':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484','mode':'synthetic'}
 with (root/'.owner.json').open('x') as f:json.dump(owner,f)
 for name in ['synthetic','tmp','target','source-engine']:(root/name).mkdir(mode=0o700)
 with (root/'source-engine/.owner.json').open('x') as f:json.dump({'task':'P3-153','root':str(root/'source-engine'),'owner':owner['owner'],'kind':'synthetic-source-engine'},f)
m=root.lstat();assert stat.S_ISDIR(m.st_mode) and stat.S_IMODE(m.st_mode)==0o700 and m.st_uid==os.getuid()
p=root/'.owner.json';m=p.lstat();assert stat.S_ISREG(m.st_mode) and stat.S_IMODE(m.st_mode)==0o600 and m.st_nlink==1
owner=json.loads(p.read_text());assert owner['task']=='P3-153' and owner['root']==str(root)
# Replay from a fresh task-owned copy; final candidate and Evidence remain read-only.
source_base=base
replays=root/'reruns';replays.mkdir(mode=0o700,exist_ok=True)
assert replays.is_dir() and not replays.is_symlink()
base=replays/str(uuid.uuid4());base.mkdir(mode=0o700)
for name in ['candidate','tools','tests']:
 for p in (source_base/name).rglob('*'):assert not p.is_symlink(), 'symlink in replay input'
 shutil.copytree(source_base/name,base/name)
(base/'evidence').mkdir(mode=0o700)
input_hashes={str(p.relative_to(source_base)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['candidate','tools','tests'] for p in (source_base/name).rglob('*') if p.is_file()}
(base/'evidence/replay-inputs.json').write_text(json.dumps(input_hashes,sort_keys=True,indent=2)+'\n')
print('Replay output: '+str(base),flush=True)
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
cargo='/Users/xxe/.cargo/bin/cargo';env=dict(os.environ,LIFEOS_P3_153_MODE='synthetic',CARGO_TARGET_DIR=str(root/'target'),TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
manifest=str(base/'candidate/Cargo.toml')
steps=[('fixtures',['python3',str(base/'tools/prepare_fixtures.py')]),('ui-build',[node,str(base/'tools/build_ui.mjs')]),('build',[cargo,'build','--locked','--offline','--features','synthetic-driver','--manifest-path',manifest]),('rust',[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',manifest,'--','--test-threads=1']),('ui',[node,'--test',*[str(base/'tools'/n) for n in ['settings_tests.mjs','health_view_tests.mjs','sources_ui_tests.mjs']]]),('integration',[node,str(base/'tools/integration_tests.mjs')]),('combined',[node,str(base/'tools/combined_tests.mjs')]),('continuity',[node,str(base/'tests/continuity.mjs')])]
steps.append(('clarification-ui',[node,'--test',str(base/'tests/clarification_ui.mjs')]))
steps.append(('freshness',[node,str(base/'tests/freshness.mjs')]))
if '--affected' in sys.argv:
 steps=[step for step in steps if step[0] in ['ui-build','build','integration','continuity','freshness']+(['fixtures'] if '--init' in sys.argv else [])]
 insert=next(i for i,step in enumerate(steps) if step[0]=='build')+1
 steps[insert:insert]=[(name,[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',manifest,scope,'--','--test-threads=1']) for name,scope in [('rust-host','health_conversation_host::tests::'),('rust-disclosure','health_conversation_host::controlled_tests::')]]
results=[]
for name,cmd in steps:
 ext='json' if name in ['integration','combined','continuity','freshness'] else 'log'
 with (base/f'evidence/{name}.{ext}').open('w') as out,(base/f'evidence/{name}.stderr').open('w') as err:
  done=subprocess.run(cmd,env=env,stdout=out,stderr=err,timeout=300)
 results.append({'step':name,'exitCode':done.returncode});print(name,done.returncode,flush=True)
 if done.returncode:break
(base/('evidence/affected-rerun-results.json' if '--affected' in sys.argv else 'evidence/rerun-results.json')).write_text(json.dumps(results,indent=2)+'\n')
assert all(hashlib.sha256((source_base/p).read_bytes()).hexdigest()==h for p,h in input_hashes.items()), 'original input changed'
raise SystemExit(any(r['exitCode'] for r in results))
