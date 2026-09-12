import os,json,hashlib,shutil,subprocess,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
assert json.loads((R/'.owner.json').read_text())['task']=='P3-152'
out=R/('mutations-'+str(time.time_ns()));out.mkdir(mode=0o700)
rel='src/health_conversation_host/controlled.rs'
mutations=[('expiry','v["expiresAt"].as_i64().unwrap_or(0)<=now()','false','expired_preview_or_client_supplied_body_cannot_be_confirmed'),('confirmation','v["revision"]!=d.expected_preview_revision||v["confirmationToken"]!=d.confirmation_token','false','forged_confirmation_token_never_dispatches'),('secret-echo','!secret.is_empty()&&response.text.contains(secret)','false','remote_key_echo_is_never_persisted_or_returned')]
results=[]
for name,old,new,test in mutations:
 target=out/name;shutil.copytree(E/'candidate',target)
 f=target/rel;s=f.read_text();assert s.count(old)==1;f.write_text(s.replace(old,new))
 log=out/(name+'.log');env={**os.environ,'LIFEOS_P3_152_MODE':'synthetic','CARGO_TARGET_DIR':str(R/'target'),'TMPDIR':str(R/'tmp')}
 with log.open('w') as stream:r=subprocess.run(['/Users/xxe/.cargo/bin/cargo','test','--locked','--offline','--bin','lifeos-p3-152','--manifest-path',str(target/'Cargo.toml'),test],env=env,stdout=stream,stderr=subprocess.STDOUT)
 text=log.read_text();killed=r.returncode!=0 and 'test result: FAILED. 0 passed; 1 failed' in text and 'error[E' not in text
 results.append(dict(name=name,test=test,killed=killed,exit_code=r.returncode,mutation_file=rel,old=old,new=new,log=str(log),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
report={'candidate_modified':False,'network':False,'results':results,'passed':sum(x['killed'] for x in results),'total':len(results),'run_root':str(out)}
print(json.dumps(report,indent=2));assert report['passed']==report['total']
