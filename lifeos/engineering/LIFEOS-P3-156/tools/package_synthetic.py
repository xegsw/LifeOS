"""Package only this candidate's offline build. Never inspect another App."""
from pathlib import Path
import json,hashlib,plistlib,shutil,os,stat
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-156-next-action-v1')
owner=json.loads((root/'.owner.json').read_text());assert owner=={'task':'P3-156','root':str(root),'thread':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484'}
assert stat.S_IMODE(root.lstat().st_mode)==0o700
app=root/'LifeOS P3-156 Synthetic Actions Final.app';app.mkdir(mode=0o700)
contents=app/'Contents';contents.mkdir();(contents/'MacOS').mkdir();(contents/'Resources').mkdir()
binary=contents/'MacOS/lifeos-p3-152';shutil.copy2(root/'target/debug/lifeos-p3-152',binary)
info={'CFBundleIdentifier':'local.lifeos.p3-156.next-action','CFBundleExecutable':'lifeos-p3-152','CFBundleName':'LifeOS P3-156 Synthetic Actions','CFBundleVersion':'1','CFBundleShortVersionString':'0.1.0','CFBundlePackageType':'APPL','NSHighResolutionCapable':True}
(contents/'Info.plist').write_bytes(plistlib.dumps(info))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v={'task':'P3-156','mode':'synthetic','app':str(app),'binary':str(binary),'binarySha256':sha(binary),'bundleFiles':{str(p.relative_to(app)):sha(p) for p in app.rglob('*') if p.is_file()},'candidateFiles':{str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()},'realContact':False}
(b/'evidence/synthetic-bundle-final.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'app':str(app),'binarySha256':v['binarySha256'],'candidateFiles':len(v['candidateFiles'])}))
