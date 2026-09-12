from pathlib import Path
import os,json,subprocess,shutil,re,uuid
b=Path(__file__).resolve().parents[1]; root=Path('/private/tmp/lifeos-p3-157-real-actions-v1/closure-1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())['owner']=='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo'
w=root/('closure-mutations-'+str(uuid.uuid4()));w.mkdir(mode=0o700);e=b/'evidence/mutations';e.mkdir();results=[]
variants=[
('unsupported-to-chat','ui/action_application.js',"kind: 'unsupported',\n            notice: classification.notice","kind: 'chat',\n            notice: classification.notice",'js'),
('empty-model-to-chat','ui/action_application.js',"if (!c) return {\n            kind: 'unsupported',","if (!c) return {\n            kind: 'chat',",'js'),
('verb-whitelist-restored','ui/action_domain.js','const body = frameBody(s),','const body = undefined,','js'),
('nonunique-cancel','ui/action_domain.js','if (found.length === 1) {','if (found.length >= 1) {','js'),
('unsupported-false-success','ui/controlled_conversation.js',"this.notice = out.notice || '这句还没有记入安排。';","this.notice = '已记下'; this.draft = this.newDraft();",'js'),
('host-candidate-bypass','src/health_conversation_host/actions.rs','if expected!=d.candidate{return Err(error("action_candidate_rejected"))}','if false && expected!=d.candidate{return Err(error("action_candidate_rejected"))}','host')]
for name,rel,old,new,kind in variants:
 m=w/name;m.mkdir();shutil.copytree(b/'candidate',m/'candidate');shutil.copytree(b/'tests',m/'tests');p=m/'candidate'/rel;s=p.read_text();assert old in s,(name,old);p.write_text(new.join(s.rsplit(old,1)) if name=='nonunique-cancel' else s.replace(old,new,1))
 env=dict(os.environ,LIFEOS_P3_157_MODE='synthetic',CARGO_TARGET_DIR=str(root/'mutation-target'),TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
 if kind=='host':
  with (e/(name+'-build.log')).open('w') as f:r=subprocess.run([cargo,'build','--locked','--offline','--features','synthetic-driver','--bin','synthetic-driver','--manifest-path',str(m/'candidate/Cargo.toml')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  assert r.returncode==0
  p=m/'tests/actions.mjs';p.write_text(p.read_text().replace("root+'/target/debug/synthetic-driver'","root+'/mutation-target/debug/synthetic-driver'"))
  cmd=[node,'--test',str(p)]
 else:cmd=[node,'--test',str(m/'tests/closure_cases.mjs')]
 with (e/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 log=(e/(name+'.log')).read_text(); valid=bool(re.search(r'fail [1-9]',log)) and ('AssertionError' in log or 'ERR_ASSERTION' in log)
 v=dict(name=name,exitCode=r.returncode,validMutation=valid,killed=r.returncode!=0 and valid);results.append(v);print(v,flush=True)
(e/'results.json').write_text(json.dumps(dict(results=results,allKilled=all(x['killed'] for x in results)),indent=2)+'\n');assert all(x['killed'] for x in results)
