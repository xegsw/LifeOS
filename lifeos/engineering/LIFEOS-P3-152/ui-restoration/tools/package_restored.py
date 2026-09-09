import os,json,hashlib,shutil,plistlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
m=json.loads((R/'.owner.json').read_text());assert m['task']=='P3-152' and m['owner']=='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
assert '44 passed; 0 failed' in (D/'evidence/host-tests.log').read_text()
assert json.loads((D/'evidence/integration-tests.json').read_text())['passed']==10
assert 'Finished' in (D/'evidence/real-build.log').read_text()
os.umask(0o077)
app=R/'LifeOS P3-152 Restored.app';binary=app/'Contents/MacOS/lifeos-p3-152'
app.mkdir(exist_ok=False);binary.parent.mkdir(parents=True)
shutil.copy2(R/'real-target/debug/lifeos-p3-152',binary)
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-152.restored',CFBundleName='LifeOS Restored',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
r={'app':str(app),'binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'source':str(D/'candidate'),'build_feature':'controlled-real','launched':False,'existing_real_pid_25223_untouched':True}
(D/'evidence/restored-bundle.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
