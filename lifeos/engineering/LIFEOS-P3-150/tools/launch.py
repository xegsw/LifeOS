import os, sys, json, subprocess, shutil, plistlib, hashlib, time
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-150-health-view-v1')
ENGINE=Path(__file__).resolve().parents[1]
mode=sys.argv[1]; assert mode in ('synthetic','real')
marker=json.loads((ROOT/'.owner.json').read_text()); assert marker['task']=='P3-150' and marker['root']==str(ROOT)
assert ROOT.stat().st_mode & 0o777==0o700 and (ROOT/'.owner.json').stat().st_mode&0o777==0o600
os.umask(0o077)
app=ROOT/('LifeOS P3-150 '+mode.title()+'.app'); app.mkdir(exist_ok=False)
mac=app/'Contents/MacOS';mac.mkdir(parents=True)
binary=mac/'lifeos-p3-150';shutil.copy2(ROOT/f'target-{mode}/debug/lifeos-p3-150',binary)
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-150',CFBundleIdentifier='local.lifeos.p3-150.'+mode,CFBundleName='LifeOS Health View',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
receipt=ENGINE/'evidence'/f'{mode}-launch.json'
log=ROOT/f'{mode}-startup.json'
with log.open('xb') as out:
 p=subprocess.Popen([str(binary)],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(ROOT/'tmp')})
for _ in range(100):
 time.sleep(.1)
 if log.stat().st_size: break
assert log.stat().st_size<1024
status=json.loads(log.read_text())
assert set(status)<= {'status','mode','code'}
data=dict(pid=p.pid,app=str(app),binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),startup=status,mode=mode)
receipt.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data))
