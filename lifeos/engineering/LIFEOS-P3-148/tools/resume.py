"""Verify this task's checkpoint before resuming an affected synthetic phase."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
from verify_design_contract import run,BASE
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
run();checkpoint=BASE/'evidence/checkpoint.json';c=json.loads(checkpoint.read_text())
assert c['task_id']=='LIFEOS-P3-148' and c['safe_to_resume'] and not c['prohibited_boundary_contact']
files={str(f.relative_to(BASE/'candidate')):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((BASE/'candidate').rglob('*')) if f.is_file()}
assert hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()==c['candidate_sha256'],'candidate_changed: reconcile checkpoint; do not erase earlier evidence'
sys.path.insert(0,str(BASE/'candidate/tools'));from task_root import verify
verify()
for f in (BASE/'evidence').glob('launch-*.json'):
 pid=json.loads(f.read_text())['pid']
 try:os.kill(pid,0)
 except ProcessLookupError:continue
 raise SystemExit('owned launch PID exists; inspect it before resuming')
phase=c['resume_from'];print(json.dumps({'verified':True,'resume_from':phase,'no_real_access':True}))
if not args.check:
 if phase not in ['contracts','build','storage','credentials_mock','transport_mock','restart']:raise SystemExit('This boundary requires the recorded GUI or PM step; no automatic real activation.')
 raise SystemExit(subprocess.call([sys.executable,'-B',str(BASE/'tools/verify_source_conversation.py'),'--phase',phase]))
