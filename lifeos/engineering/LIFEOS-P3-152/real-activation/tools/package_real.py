from pathlib import Path
import os,json,hashlib,shutil,plistlib,subprocess
D=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
assert '65 passed; 0 failed' in (D/'evidence/host-tests-authority.log').read_text()
for name,count in [('integration-final.json',12),('combined-final.json',11)]:
 v=json.loads((D/'evidence'/name).read_text());assert v['passed']==v['total']==count
assert 'pass 17' in (D/'evidence/ui-final.log').read_text() and 'fail 0' in (D/'evidence/ui-final.log').read_text()
assert 'Finished' in (D/'evidence/real-build.log').read_text()
assert json.loads((D/'evidence/old-instance-normal-quit.json').read_text())['exited']
os.umask(0o077);app=R/'LifeOS P3-152 Unified Real.app';app.mkdir(exist_ok=False)
binary=app/'Contents/MacOS/lifeos-p3-152';binary.parent.mkdir(parents=True);shutil.copy2(R/'real-target/debug/lifeos-p3-152',binary)
resources=app/'Contents/Resources';resources.mkdir();subprocess.run(['/usr/bin/swiftc',str(D/'candidate/source-engine/tools/alias_metadata.swift'),'-o',str(resources/'alias_metadata')],check=True)
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-152.unified-real',CFBundleName='LifeOS',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
v={'app':str(app),'binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'alias_helper_sha256':hashlib.sha256((resources/'alias_metadata').read_bytes()).hexdigest(),'candidate':str(D/'candidate'),'mode':'real','launched':False}
(D/'evidence/real-bundle.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
