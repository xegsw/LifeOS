from pathlib import Path
import json,hashlib,os,subprocess,plistlib,shutil
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-157-real-actions-v1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())['task']=='P3-157'
assert all(v['exitCode']==0 for v in json.loads((b/'evidence/regression-results.json').read_text()))
assert json.loads((b/'evidence/mutations/results.json').read_text())['allKilled']
assert 'Finished' in (b/'evidence/real-build.log').read_text()
app=root/'LifeOS P3-157 Real Actions.app';app.mkdir();binary=app/'Contents/MacOS/lifeos-p3-152';binary.parent.mkdir(parents=True);shutil.copy2(root/'real-target/debug/lifeos-p3-152',binary)
resources=app/'Contents/Resources';resources.mkdir();subprocess.run(['/usr/bin/swiftc','-module-cache-path',str(root/'tmp/swift-module-cache'),str(b/'candidate/source-engine/tools/alias_metadata.swift'),'-o',str(resources/'alias_metadata')],check=True,env=dict(os.environ,TMPDIR=str(root/'tmp')))
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-157.real-actions',CFBundleName='LifeOS',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v={'app':str(app),'binary':str(binary),'binarySha256':sha(binary),'bundleFiles':{str(p.relative_to(app)):sha(p) for p in sorted(app.rglob('*')) if p.is_file()},'candidateFiles':{str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()},'mode':'real','launched':False}
(b/'evidence/real-bundle.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'app':str(app),'binarySha256':v['binarySha256'],'candidateFiles':len(v['candidateFiles'])}))
