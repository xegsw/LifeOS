from pathlib import Path
import os,shutil,json,hashlib,plistlib
b=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-158-main-chain-v1');os.umask(0o077)
assert json.loads((r/'.owner.json').read_text())==dict(task='P3-158',root=str(r),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
checks=json.loads((b/'evidence/D0670-regression-results.json').read_text());assert all(x['exitCode']==0 for x in checks);assert any(x['step']=='build' for x in checks)
a=r/'LifeOS P3-158 v8 Offline.app';a.mkdir();(a/'Contents/MacOS').mkdir(parents=True);(a/'Contents/Resources').mkdir();shutil.copy2(r/'build/offline/debug/lifeos-p3-152',a/'Contents/MacOS/lifeos-p3-152');shutil.copy2(r/'offline/source-engine/alias_metadata',a/'Contents/Resources/alias_metadata')
(a/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-158.v8-offline',CFBundleName='LifeOS P3-158 v8 Offline',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(app=str(a),mode='synthetic',binary=str(a/'Contents/MacOS/lifeos-p3-152'),binarySha256=sha(a/'Contents/MacOS/lifeos-p3-152'),candidateFiles={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()});(b/'evidence/D0672-v8-offline-bundle.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(app=str(a),binarySha256=v['binarySha256'],candidateFiles=len(v['candidateFiles']))))
