from pathlib import Path
import os,json,shutil,uuid,subprocess,hashlib
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-157-real-actions-v1/closure-1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())['task']=='P3-157'
r=root/'reruns'/str(uuid.uuid4());r.mkdir(parents=True,mode=0o700)
for name in ['candidate','tools','tests']:shutil.copytree(b/name,r/name)
(r/'evidence').mkdir();print('Replay output: '+str(r),flush=True)
original={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for name in ['candidate','tools','tests'] for p in (b/name).rglob('*') if p.is_file()}
result=subprocess.run(['python3',str(r/'tools/run_checks.py')]);assert all(hashlib.sha256((b/p).read_bytes()).hexdigest()==h for p,h in original.items());raise SystemExit(result.returncode)
