from pathlib import Path
import os,json,hashlib,subprocess,time
D=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
r=json.loads((D/'evidence/real-bundle.json').read_text());assert r['mode']=='real' and hashlib.sha256(Path(r['binary']).read_bytes()).hexdigest()==r['binary_sha256']
old=json.loads((D/'evidence/old-instance-identity.json').read_text())['expected_binary']
for line in subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True).splitlines():
 f=line.strip().split(None,1)
 if len(f)==2:assert f[1] not in [old,r['binary']],'an exact existing real instance remains'
# Creation of this receipt gate makes the entry point explicitly single-attempt.
claim=D/'evidence/real-launch-attempt.json'
with claim.open('x') as f:json.dump({'mode':'real','time':time.time(),'binary':r['binary'],'automatic_scan_import_send':False},f)
log=R/('unified-real-start-'+str(time.time_ns())+'.json');os.umask(0o077)
with log.open('xb') as out:
 p=subprocess.Popen([r['binary']],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(R/'tmp')})
for _ in range(100):
 if log.stat().st_size or p.poll() is not None:break
 time.sleep(.1)
assert log.stat().st_size<=1024,'startup metadata exceeded bound'
status=json.loads(log.read_text()) if log.stat().st_size else {'status':'startup_unconfirmed'}
v={**r,'launched':True,'pid':p.pid,'startup':status,'running':p.poll() is None,'shared_conversation_lock':'successful startup follows Store::open exclusive lease','real_content_inspected':False,'real_AX_or_screenshot':False,'automatic_scan_import_send':False}
(D/'evidence/real-launch.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
assert status=={'status':'controlled_conversation_started'} and p.poll() is None,'startup did not succeed; no automatic retry'
