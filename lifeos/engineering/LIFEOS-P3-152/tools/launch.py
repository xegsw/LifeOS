# coding: utf-8
import os,sys,json,subprocess,shutil,plistlib,hashlib,time,stat
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-152-health-conversation-v1');ENGINE=Path(__file__).resolve().parents[1]
assert not ROOT.is_symlink() and stat.S_IMODE(ROOT.stat().st_mode)==0o700
marker=ROOT/'.owner.json';assert not marker.is_symlink() and stat.S_IMODE(marker.stat().st_mode)==0o600
m=json.loads(marker.read_text());assert m['task']=='P3-152' and m['root']==str(ROOT)
os.umask(0o077)
app=ROOT/'LifeOS P3-152 Synthetic.app';binary=app/'Contents/MacOS/lifeos-p3-152';receipt=ENGINE/'evidence/synthetic-launch.json'
if '--restart' in sys.argv:
 r=json.loads(receipt.read_text());assert r['mode']=='synthetic' and r['binary']==str(binary)
 assert hashlib.sha256(binary.read_bytes()).hexdigest()==r['binary_sha256']
 p=subprocess.run(['/bin/ps','-p',str(r['pid']),'-o','comm='],capture_output=True,text=True)
 assert p.returncode!=0,'Close the verified synthetic instance before restart'
 if '--update' in sys.argv:shutil.copy2(ROOT/'target/debug/lifeos-p3-152',binary)
else:
 app.mkdir(exist_ok=False);binary.parent.mkdir(parents=True)
 shutil.copy2(ROOT/'target/debug/lifeos-p3-152',binary)
 (app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-152.synthetic',CFBundleName='LifeOS Synthetic Conversation',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
log=ROOT/('startup-'+str(time.time_ns())+'.json')
with log.open('xb') as out:p=subprocess.Popen([str(binary)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(ROOT/'tmp')})
for _ in range(100):
 time.sleep(.1)
 if log.stat().st_size:break
assert log.stat().st_size<1024
status=json.loads(log.read_text());assert status=={'status':'synthetic_conversation_started'}
r=dict(pid=p.pid,app=str(app),binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),startup=status,mode='synthetic')
receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
