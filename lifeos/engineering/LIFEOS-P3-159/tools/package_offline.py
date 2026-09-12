"""Exclusive complete offline App; no signing identity or real data access."""
from pathlib import Path
import datetime, hashlib, json, os, plistlib, shutil, subprocess,argparse
parser=argparse.ArgumentParser();parser.add_argument("--evidence-name",default="A-package.json");args=parser.parse_args();assert "/" not in args.evidence_name and args.evidence_name.endswith(".json")
b=Path(__file__).resolve().parents[1]
r=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1')
os.umask(0o077)
assert json.loads((r/'.owner.json').read_text()) == dict(task='P3-159',root=str(r),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
receipt=json.loads((b/'evidence/offline-verification.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()}
assert receipt['exitCode']==0 and receipt['sourceAfter']==files
stage=r/'build'/('A-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
stage.mkdir(mode=0o700)
app=stage/'LifeOS Offline.app'
(app/'Contents/MacOS').mkdir(parents=True)
(app/'Contents/Resources').mkdir()
binary=r/'build/offline/debug/lifeos-p3-152'
assert binary.is_file() and not binary.is_symlink()
shutil.copy2(binary,app/'Contents/MacOS/lifeos-p3-152')
config=json.loads((b/'candidate/tauri.conf.json').read_text())
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier=config['identifier'],CFBundleName='LifeOS Offline',CFBundlePackageType='APPL',CFBundleVersion=config['version'],CFBundleShortVersionString=config['version'],NSHighResolutionCapable=True)))
helper=r/'offline/source-engine/alias_metadata'
subprocess.run(['/usr/bin/xcrun','swiftc',str(b/'candidate/tools/alias_metadata.swift'),'-o',str(helper)],check=True)
shutil.copy2(helper,app/'Contents/Resources/alias_metadata')
manifest=dict(task='P3-159',mode='synthetic',app=str(app),binarySha256=sha(binary),sourceFiles=files,bundleFiles={str(p.relative_to(app)):sha(p) for p in sorted(app.rglob('*')) if p.is_file()},signedWithPersistentIdentity=False,launched=False)
(stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(b/'evidence'/args.evidence_name).write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(app=str(app),binarySha256=manifest['binarySha256'])))
