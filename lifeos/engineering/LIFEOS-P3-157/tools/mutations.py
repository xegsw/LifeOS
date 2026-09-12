"""Bounded synthetic guard mutations; never run a real-mode process."""
from pathlib import Path
import json,os,subprocess,shutil,uuid
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-157-real-actions-v1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())['task']=='P3-157'
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo';env=dict(os.environ,LIFEOS_P3_157_MODE='synthetic',CARGO_TARGET_DIR=str(root/'target'),TMPDIR=str(root/'tmp'),CARGO_NET_OFFLINE='true')
workspace=root/'mutations';workspace.mkdir(mode=0o700);evidence=b/'evidence/mutations';evidence.mkdir();results=[]
variants=[
 ('allow-missing-existing-file','src/health_conversation_host/existing_schema.rs','if fresh&&existing_only{return Err(error("store_contract_rejected"))}','', 'rust'),
 ('skip-feedback-schema','src/health_conversation_host/existing_schema.rs','for table in TABLES.into_iter().chain(["meta","requests","audit"]) {','for table in TABLES.into_iter().chain(["meta","requests","audit"]).filter(|t|*t!="feedback") {','rust'),
 ('skip-column-contract','src/health_conversation_host/existing_schema.rs','if columns.len()!=expected.len()||columns.iter().zip(expected).any','if false && (columns.len()!=expected.len()||columns.iter().zip(expected).any','column'),
 ('hide-real-actions','ui/controlled_conversation.js','const legacy = await super.read();','const legacy = await super.read(); if(legacy.mode === "real")return legacy;','js'),
 ('bypass-local-action-route','ui/controlled_conversation.js',"if (await this.actions.submit(d, current)) return {",'if (false) return {','js')]
for name,rel,old,new,kind in variants:
 m=workspace/name;m.mkdir();shutil.copytree(b/'candidate',m/'candidate');shutil.copytree(b/'tests',m/'tests');p=m/'candidate'/rel;s=p.read_text();assert s.count(old)==1,(name,s.count(old));s=s.replace(old,new,1)
 if kind=='column':s=s.replace('*pk!=ep){return Err(error("store_contract_rejected"))}','*pk!=ep)){return Err(error("store_contract_rejected"))}',1)
 p.write_text(s)
 if kind in ['rust','column']:cmd=[cargo,'test','--locked','--offline','--features','synthetic-driver','--bin','lifeos-p3-152','--manifest-path',str(m/'candidate/Cargo.toml'),'existing_schema::tests::','--','--test-threads=1']
 else:cmd=[node,'--test',str(m/'tests/real_local_routing.mjs')]
 with (evidence/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 log=(evidence/(name+'.log')).read_text();valid=('test result: FAILED.' in log and 'error[E' not in log) if kind in ['rust','column'] else ('fail 1' in log or 'fail 2' in log)
 result={'name':name,'exitCode':r.returncode,'validMutation':valid,'killed':r.returncode!=0 and valid};results.append(result);print(result,flush=True)
(evidence/'results.json').write_text(json.dumps({'results':results,'allKilled':all(v['killed'] for v in results)},indent=2)+'\n');assert all(v['killed'] for v in results)
