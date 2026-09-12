"""A-only disposable source mutations; no network or real paths."""
from pathlib import Path
import os,subprocess,json,shutil,uuid,re
os.umask(0o077);b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-158-main-chain-v1');w=root/'offline'/('mutations-'+str(uuid.uuid4()));w.mkdir();e=b/'evidence/mutations';e.mkdir();cargo='/Users/xxe/.cargo/bin/cargo';node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
variants=[
('request-binding','src/health_conversation_host/operations.rs','if v["requestId"]!=d.request_id||v["revision"]!=d.expected_preview_revision','if false'),
('strict-candidate-fields','src/health_conversation_host/operations.rs','contract::fields(c,fields,&[])?;','let _=fields;'),
('topic-binding','src/health_conversation_host/operations.rs','if !overlap(raw,target["confirmedContent"].as_str().unwrap())','if false && !overlap(raw,target["confirmedContent"].as_str().unwrap())'),
('conditional-authority','src/health_conversation_host/operations.rs','&&caution(v["question"].as_str().unwrap())','&&false'),
('late-deadline','src/health_conversation_host/operations.rs','if dispatched&&v["deadline"]','if false&&dispatched&&v["deadline"]'),
('receipt-binding','ui/action_domain.js',"if (!result || result.requestId !== preview.requestId", "if (false && (!result || result.requestId !== preview.requestId")]
results=[]
for name,rel,old,new in variants:
 m=w/name;shutil.copytree(b/'candidate',m/'candidate');shutil.copytree(b/'tests',m/'tests');p=m/'candidate'/rel;s=p.read_text();assert s.count(old)==1,(name,s.count(old));s=s.replace(old,new)
 if name=='receipt-binding':s=s.replace('result.previewId !== preview.previewId) throw','result.previewId !== preview.previewId)) throw')
 p.write_text(s)
 cmd=[node,'--test',str(m/'tests/operation_flow.mjs')] if name=='receipt-binding' else [cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(m/'candidate/Cargo.toml'),'operations::tests','--','--test-threads=1']
 env=dict(os.environ,LIFEOS_P3_158_MODE='synthetic',CARGO_TARGET_DIR=str(root/'build/mutations'),TMPDIR=str(root/'offline/tmp'))
 with (e/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 log=(e/(name+'.log')).read_text();valid=('test result: FAILED.' in log and 'error[E' not in log) if name!='receipt-binding' else bool(re.search(r'fail [1-9]',log)) and 'AssertionError' in log
 v=dict(name=name,exitCode=r.returncode,validMutation=valid,killed=r.returncode!=0 and valid);results.append(v);print(v,flush=True)
(e/'results.json').write_text(json.dumps(dict(results=results,allKilled=all(x['killed'] for x in results)),indent=2)+'\n');assert all(x['killed'] for x in results)
