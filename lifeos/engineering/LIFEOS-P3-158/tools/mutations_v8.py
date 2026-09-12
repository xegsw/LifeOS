"""D0670 offline mutations in fresh disposable copies; never edit the candidate.
Only a compiled failing assertion kills a mutant. No GUI, keychain, provider or network.
"""
from pathlib import Path
import os,subprocess,json,shutil,uuid,re,datetime,hashlib
os.umask(0o077)
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-158-main-chain-v1')
assert json.loads((root/'.owner.json').read_text())==dict(task='P3-158',root=str(root),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
run='D0670-mutations-'+str(uuid.uuid4());w=root/'build'/run;w.mkdir();(w/'.owner.json').write_text(json.dumps({'task':'P3-158','purpose':'offline source mutations','root':str(w)}))
e=b/'evidence'/run;e.mkdir()
cargo='/Users/xxe/.cargo/bin/cargo';node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
base='src/health_conversation_host/'
variants=[
 ('condition-record-only',base+'coordination/commit.rs','if truth=="true"&&apply','if truth=="true"'),
 ('condition-false-not-true',base+'coordination/commit.rs','if truth=="true"&&apply','if (truth=="true"||truth=="false")&&apply'),
 ('condition-current-version',base+'coordination.rs','if latest["condition"] != *bound {','if false {'),
 ('credential-wait-cancel',base+'coordination.rs','if cancelled(t) {','if false {'),
 ('preview-expiry',base+'coordination.rs','|| t["sendPreview"]["expiresAt"].as_i64().unwrap_or(0) <= now()','|| false'),
 ('query-result-contract',base+'coordination/fixtures.rs','fn result_contract(t: &Value) -> R<()> {','fn result_contract(t: &Value) -> R<()> { return Ok(());'),
 ('late-model-response',base+'coordination.rs','if elapsed > reserved {','if false {'),
 ('transport-budget','src/host_gateway.rs','port.generate_diagnosed_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,remaining,','port.generate_diagnosed_with_receipt(plan.preview["exactBody"].as_str().unwrap(),&plan.key,120000,'),
 ('frontend-success-receipt','ui/controlled_conversation.js','const r = validateCoordinationReceipt(t, v.requestId);','const r = t.receipt;'),
]
selected=os.environ.get('P158_MUTATIONS','')
if selected:
 names=set(selected.split(','));assert names.issubset({v[0] for v in variants});variants=[v for v in variants if v[0] in names]
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
