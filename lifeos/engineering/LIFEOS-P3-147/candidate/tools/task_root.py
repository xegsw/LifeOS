"""Exclusive task-owned synthetic root only. No path overrides."""
from pathlib import Path
import os,sys,json,stat,shutil,datetime
ROOT=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1')
MARKER={"task":"LIFEOS-P3-147","owner":"01a07f0e-dbbd-7d23-9e6d-68f2152f9484","schema":"lifeos.p3-147.root.v1","root":str(ROOT)}
NAME='.lifeos-p3-147-owner.json'
def verify():
 s=ROOT.lstat();m=(ROOT/NAME).lstat()
 assert stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode)==0o700 and s.st_uid==os.getuid()
 assert stat.S_ISREG(m.st_mode) and stat.S_IMODE(m.st_mode)==0o600 and m.st_uid==os.getuid()
 assert ROOT.resolve()==ROOT and json.loads((ROOT/NAME).read_text())==MARKER
 return True
if __name__=='__main__':
 action=sys.argv[1]
 if action=='init':
  if os.path.lexists(ROOT):verify()
  else:
   ROOT.mkdir(mode=0o700)
   fd=os.open(ROOT/NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   with os.fdopen(fd,'w') as f:json.dump(MARKER,f)
  for name in ['tmp','fixtures','initial-build-cache']: (ROOT/name).mkdir(mode=0o700,exist_ok=True)
  print('owned synthetic root ready')
 elif action=='verify': print(verify())
 elif action=='cleanup':
  verify()
  base=Path(__file__).resolve().parents[2]
  pids={json.loads(f.read_text())['pid'] for f in (base/'evidence').glob('launch-*.json')}
  # Fail closed if any recorded launch PID still exists; never signal it automatically.
  for pid in pids:
   try:os.kill(pid,0)
   except ProcessLookupError:continue
   raise SystemExit('recorded PID still exists; do not clean: '+str(pid))
  assert not any(ROOT.rglob('*.sqlite-wal')), 'unclosed SQLite WAL requires inspection'
  shutil.rmtree(ROOT)
  assert not os.path.lexists(ROOT)
  result={'root':str(ROOT),'marker_verified':True,'writers_stopped':True,'known_app_pids_stopped':sorted(pids),'removed':True,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  out=base/'evidence'/('cleanup-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'.json')
  out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
 else:raise SystemExit('expected init, verify, or cleanup')
