"""Package already-built B app; no launch, network or credentials. Signing is separate."""
from pathlib import Path
import datetime,hashlib,json,os,plistlib,shutil,subprocess,argparse
parser=argparse.ArgumentParser();parser.add_argument("--evidence-name",default="B-package-unsigned.json");args=parser.parse_args();assert "/" not in args.evidence_name and args.evidence_name.endswith(".json")
b=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1');os.umask(0o077)
assert json.loads((r/'.owner.json').read_text())==dict(task='P3-159',root=str(r),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()}
receipt=json.loads((b/'evidence/offline-verification.json').read_text());assert receipt['exitCode']==0 and receipt['sourceStableDuringRun'] and receipt['sourceAfter']==files
build=json.loads(sorted((b/'evidence').glob('A-mode-build-*.json'))[-1].read_text());online=next(row for row in build if row['mode']=='online-synthetic');assert online['exitCode']==0 and online['sourceFiles']==files
binary=Path(online['binary']);assert sha(binary)==online['binarySha256']
stage=r/'build'/('B-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'));stage.mkdir(mode=0o700);app=stage/'LifeOS Online Synthetic.app'
(app/'Contents/MacOS').mkdir(parents=True);(app/'Contents/Resources').mkdir();shutil.copy2(binary,app/'Contents/MacOS/lifeos-p3-152')
config=json.loads((b/'candidate/tauri.conf.json').read_text());(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier=config['identifier'],CFBundleName='LifeOS Online Synthetic',CFBundlePackageType='APPL',CFBundleVersion=config['version'],CFBundleShortVersionString=config['version'],NSHighResolutionCapable=True)))
helper=app/'Contents/Resources/alias_metadata';subprocess.run(['/usr/bin/xcrun','swiftc',str(b/'candidate/tools/alias_metadata.swift'),'-o',str(helper)],check=True)
manifest=dict(task='P3-159',mode='online-synthetic',app=str(app),unsignedBinarySha256=sha(binary),sourceFiles=files,bundleFiles={str(p.relative_to(app)):sha(p) for p in sorted(app.rglob('*')) if p.is_file()},signed=False,launched=False,actualPosts=0)
(stage/'unsigned-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(b/'evidence'/args.evidence_name).write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'app':str(app),'unsignedBinarySha256':sha(binary),'launched':False}))
