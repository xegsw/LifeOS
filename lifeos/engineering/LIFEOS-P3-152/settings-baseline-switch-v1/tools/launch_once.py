from pathlib import Path
import os,json,hashlib,subprocess,time
D=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
os.umask(0o077)
assert json.loads((D/'evidence/normal-quit.json').read_text())['exited']
instances=json.loads(subprocess.check_output([str(R/'settings-switch-identity'),'inspect'],text=True))
assert not instances['instances'],'an exact instance remains; stop'
known={str(R/(name+'.app')/'Contents/MacOS/lifeos-p3-152') for name in ['LifeOS P3-152 Controlled','LifeOS P3-152 Unified Real','LifeOS P3-152 Credential Fix','LifeOS P3-152 Model Settings Restored']}
for line in subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True).splitlines():
 parts=line.strip().split(None,1)
 assert len(parts)!=2 or parts[1] not in known,'an exact known same-root executable remains'
binary=R/'LifeOS P3-152 Model Settings Restored.app/Contents/MacOS/lifeos-p3-152'
digest=hashlib.sha256(binary.read_bytes()).hexdigest();assert digest=='3a0f72dfca5caa27c013b1ae91a7aa455c45910c282acaff82c69e48df0127c4'
with (D/'evidence/launch-claim.json').open('x') as f:json.dump({'binary':str(binary),'sha256':digest,'time':time.time(),'single_attempt':True},f)
log=R/('settings-restored-start-'+str(time.time_ns())+'.json')
with log.open('xb') as out:
 p=subprocess.Popen([str(binary)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(R/'tmp')})
for _ in range(100):
 if log.stat().st_size or p.poll() is not None:break
 time.sleep(.1)
assert log.stat().st_size<=1024,'fixed startup metadata bound exceeded'
status=json.loads(log.read_text()) if log.stat().st_size else {'status':'startup_unconfirmed'}
receipt={'pid':p.pid,'binary':str(binary),'binary_sha256':digest,'startup':status,'running':p.poll() is None,'single_attempt':True,'shared_conversation_lock':'unchanged mandatory exclusive Store lease before started status','window_title_from_candidate':'LifeOS P3-152 - Controlled Conversation','real_AX_screenshot_or_content_read':False,'agent_scan_import_save_key_or_send':False}
with (D/'evidence/launch.json').open('x') as f:json.dump(receipt,f,indent=2)
print(json.dumps(receipt))
assert status=={'status':'controlled_conversation_started'} and p.poll() is None,'startup not confirmed; no automatic retry'
activation=subprocess.run([str(R/'settings-switch-identity'),'activate',str(p.pid)],capture_output=True,text=True)
with (D/'evidence/activation.json').open('x') as f:f.write(activation.stdout)
print(activation.stdout);assert activation.returncode==0,'activation identity not confirmed'
