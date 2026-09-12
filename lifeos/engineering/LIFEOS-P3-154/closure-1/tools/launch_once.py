#!/usr/bin/env python3
from pathlib import Path
import os,json,hashlib,subprocess,time,re
b=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-154-real-continuity-v1');os.umask(0o077)
assert json.loads((b/'evidence/normal-quit.json').read_text())['exited']
assert not json.loads(subprocess.check_output([str(r/'c1-app-identity'),'inspect'],text=True))['instances']
v=json.loads((b/'evidence/real-bundle.json').read_text());binary=Path(v['binary']);assert hashlib.sha256(binary.read_bytes()).hexdigest()==v['binarySha256']
for p,h in v['candidateFiles'].items():assert hashlib.sha256((b/'candidate'/p).read_bytes()).hexdigest()==h,p
with (b/'evidence/launch-claim.json').open('x') as f:json.dump({'binarySha256':v['binarySha256'],'time':time.time(),'singleAttempt':True},f)
log=r/'c1-startup-fixed.json'
with log.open('xb') as f:p=subprocess.Popen([str(binary)],stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(r/'tmp')})
for _ in range(100):
 if log.stat().st_size or p.poll() is not None:break
 time.sleep(.1)
assert log.stat().st_size<=1024
s=json.loads(log.read_text()) if log.stat().st_size else {'status':'startup_unconfirmed'}
assert set(s)<= {'status','code'} and all(isinstance(x,str) and re.fullmatch('[a-z_]+',x) for x in s.values())
v={'pid':p.pid,'binarySha256':v['binarySha256'],'startup':s,'running':p.poll() is None,'singleAttempt':True,'realContentCollected':False}
(b/'evidence/launch.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
assert s=={'status':'controlled_conversation_started'} and p.poll() is None,'Startup failed; no automatic retry'
a=subprocess.run([str(r/'c1-app-identity'),'activate',str(p.pid)],capture_output=True,text=True);(b/'evidence/activation.json').write_text(a.stdout);print(a.stdout);assert a.returncode==0
