from pathlib import Path
import sys,subprocess,os,shutil,json,hashlib,datetime,plistlib
from task_root import verify
verify()
r=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1');base=Path(__file__).resolve().parents[2];label=sys.argv[1];assert label.isalnum();viewport=sys.argv[2] if len(sys.argv)>2 else 'desktop';assert viewport in ['desktop','narrow']
marker=json.loads((r/'.lifeos-p3-147-owner.json').read_text());assert marker['task']=='LIFEOS-P3-147' and marker['root']==str(r)
binary=r/'initial-build-cache/debug/lifeos-p3-147';dest=r/'LifeOS P3-147.app/Contents/MacOS/lifeos-p3-147'
dest.parent.mkdir(parents=True,exist_ok=True)
info={'CFBundleIdentifier':'local.lifeos.p3-147.synthetic','CFBundleName':'LifeOS P3-147','CFBundleExecutable':'lifeos-p3-147','CFBundlePackageType':'APPL','NSHighResolutionCapable':True}
with open(dest.parents[1]/'Info.plist','wb') as f:plistlib.dump(info,f)
shutil.copy2(binary,dest)
env=os.environ.copy();env.update(TMPDIR=str(r/'tmp'),LIFEOS_P3_147_PROFILE='synthetic',LIFEOS_P3_147_VIEWPORT=viewport)
p=subprocess.Popen([str(dest)],env=env,stdout=open(r/('app-'+label+'.stdout'),'w'),stderr=open(r/('app-'+label+'.stderr'),'w'),start_new_session=True)
files={str(f.relative_to(base/'candidate')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (base/'candidate').rglob('*') if f.is_file()}
record={'pid':p.pid,'executable':str(dest),'binary_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'viewport':viewport,'source_files':files}
out=base/'evidence'/('launch-'+label+'.json');assert not out.exists();out.write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k!='source_files'}))
