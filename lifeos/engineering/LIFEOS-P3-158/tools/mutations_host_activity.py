"""D0670 offline mutations in fresh disposable copies; never edit the candidate.
Only a compiled failing assertion kills a mutant. No GUI, keychain, provider or network.
"""
from pathlib import Path
import os,subprocess,json,shutil,uuid,re,datetime,hashlib
os.umask(0o077)
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-158-main-chain-v1')
assert json.loads((root/'.owner.json').read_text())==dict(task='P3-158',root=str(root),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
run='D0672-host-mutations-'+str(uuid.uuid4());w=root/'build'/run;w.mkdir();(w/'.owner.json').write_text(json.dumps({'task':'P3-158','purpose':'offline source mutations','root':str(w)}))
e=b/'evidence'/run;e.mkdir()
cargo='/Users/xxe/.cargo/bin/cargo';node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
base='src/health_conversation_host/'
variants=[
 ('host-crash-reservation',base+'coordination/activity.rs','let total = used.saturating_add(reserved).min(180000);','let total = used.min(180000);'),
 ('host-commit-budget',base+'coordination/activity.rs','if elapsed > stage.reserved\n            || used.saturating_add(elapsed).saturating_add(reserved) > 180000','if false'),
 ('host-durable-before-work',base+'coordination/activity.rs','"state":"active","activeStage":"host"','"state":"settled","activeStage":"host"'),
]

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()}
results=[]
for name,rel,old,new in variants:
 m=w/name;shutil.copytree(b/'candidate',m/'candidate');shutil.copytree(b/'tests',m/'tests');p=m/'candidate'/rel;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))
 frontend=name=='frontend-success-receipt'
 cmd=[node,'--test',str(m/'tests/coordination_receipt.mjs')] if frontend else [cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(m/'candidate/Cargo.toml'),'coordination::tests','--','--test-threads=1']
 env=dict(os.environ,LIFEOS_P3_158_MODE='synthetic',CARGO_TARGET_DIR=str(root/'build/mutations'),TMPDIR=str(root/'offline/tmp'),CARGO_NET_OFFLINE='true')
 with (e/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 log=(e/(name+'.log')).read_text();valid=('test result: FAILED.' in log and 'error[E' not in log and 'panicked at' in log) if not frontend else bool(re.search(r'(?:fail |failed )[1-9]',log)) and ('AssertionError' in log or 'ERR_ASSERTION' in log)
 item=dict(name=name,changedFile=rel,beforeSha256=before[rel],afterSha256=sha(p),exitCode=r.returncode,validMutation=valid,killed=r.returncode!=0 and valid,log=str(e/(name+'.log')));results.append(item);print(json.dumps(item),flush=True)
 (e/'results.json').write_text(json.dumps({'run':run,'results':results,'completed':len(results)==len(variants),'allKilled':len(results)==len(variants) and all(x['killed'] for x in results)},indent=2)+'\n')
after={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()};assert before==after,'candidate changed during mutation run; results not positive evidence'
(e/'candidate-preservation.json').write_text(json.dumps({'unchanged':True,'candidateFiles':before,'disposableRoot':str(w)},indent=2)+'\n')
assert all(x['killed'] for x in results)
