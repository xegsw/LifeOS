from pathlib import Path
import os,json,hashlib,shutil,plistlib,subprocess
b=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-155-source-update-v1');os.umask(0o077)
assert json.loads((r/'.owner.json').read_text())['task']=='P3-155'
assert 'Finished' in (b/'evidence/real-build-delivery.log').read_text()
assert all(v['exitCode']==0 for v in json.loads((b/'evidence/delivery-regression/rerun-results.json').read_text()))
assert json.loads((b/'evidence/rust-mutations/results.json').read_text())['allKilled']
a=r/'LifeOS P3-155 Source Update.app';a.mkdir();p=a/'Contents/MacOS/lifeos-p3-152';p.parent.mkdir(parents=True);shutil.copy2(r/'real-target/debug/lifeos-p3-152',p)
resources=a/'Contents/Resources';resources.mkdir();subprocess.run(['/usr/bin/swiftc',str(b/'candidate/source-engine/tools/alias_metadata.swift'),'-o',str(resources/'alias_metadata')],check=True)
(a/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-155.source-update',CFBundleName='LifeOS',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(x.relative_to(b/'candidate')):sha(x) for x in sorted((b/'candidate').rglob('*')) if x.is_file()}
v={'app':str(a),'binary':str(p),'binarySha256':sha(p),'bundleFiles':{str(x.relative_to(a)):sha(x) for x in sorted(a.rglob('*')) if x.is_file()},'candidateFiles':files,'mode':'real','launched':False}
(b/'evidence/real-bundle.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['app','binarySha256','mode','launched']}))
