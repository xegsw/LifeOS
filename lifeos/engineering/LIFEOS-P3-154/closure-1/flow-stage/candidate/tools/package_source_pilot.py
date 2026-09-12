"""Compile and package the fixed real profile inside the engineering root. Never launch it."""
from pathlib import Path
import os,subprocess,json,hashlib,plistlib,shutil,datetime
from task_root import ROOT,PROFILE,verify
assert PROFILE=='engineering'
verify()
BASE=Path(__file__).resolve().parents[2]
out=BASE/'evidence'/('pilot-package-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir()
env={**os.environ,'LIFEOS_P3_147_BUILD_PROFILE':'source-pilot-1','CARGO_TARGET_DIR':str(ROOT/'pilot-build-cache'),'TMPDIR':str(ROOT/'tmp')}
env.pop('LIFEOS_P3_147_PROFILE',None)
with (out/'build.log').open('xb') as log:
 code=subprocess.run(['/Users/xxe/.cargo/bin/cargo','build','--locked','--offline','--manifest-path',str(BASE/'candidate/Cargo.toml')],env=env,stdout=log,stderr=subprocess.STDOUT).returncode
assert code==0,'pilot build failed; preserved build.log'
app=ROOT/'LifeOS Local Source.app';contents=app/'Contents';binary=contents/'MacOS/lifeos-p3-147'
binary.parent.mkdir(parents=True,exist_ok=True);resources=contents/'Resources';resources.mkdir(exist_ok=True)
shutil.copy2(ROOT/'pilot-build-cache/debug/lifeos-p3-147',binary)
shutil.copy2(BASE/'candidate/tools/parse_source.py',resources/'parse_source.py')
shutil.copy2(ROOT/'alias_metadata',resources/'alias_metadata')
with (contents/'Info.plist').open('wb') as f:plistlib.dump({'CFBundleIdentifier':'local.lifeos.source-pilot-1','CFBundleName':'LifeOS Local Source','CFBundleExecutable':'lifeos-p3-147','CFBundlePackageType':'APPL','NSHighResolutionCapable':True},f)
with (out/'codesign.log').open('xb') as log:
 subprocess.run(['/usr/bin/codesign','--force','--deep','--sign','-',str(app)],stdout=log,stderr=subprocess.STDOUT,check=True)
files={str(p.relative_to(app)):hashlib.sha256(p.read_bytes()).hexdigest() for p in app.rglob('*') if p.is_file()}
result={'profile':'source-pilot-1','build_exit_code':code,'app':str(app),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'app_files':files,'launched':False,'real_path_contact':False,'cache_scope':'engineering root only','independent_security':'User-directed review waiver / No Independent Pass'}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':str(out/'result.json'),'app':str(app),'binary_sha256':result['binary_sha256'],'launched':False}))
