"""Exclusive task-owned synthetic root only. No path overrides."""
from pathlib import Path
import os,sys,json,stat,shutil,datetime,subprocess
PROFILES=json.loads((Path(__file__).resolve().parents[1]/'root_profiles.json').read_text())
PROFILE=os.environ.get('LIFEOS_P3_149_BUILD_PROFILE')
if PROFILE not in ('engineering',): raise SystemExit('explicit build profile required')
for key in ['LIFEOS_RUNTIME_ROOT','LIFEOS_P3_145_ROOT_PROFILE','LIFEOS_P3_149_ROOT','LIFEOS_P3_149_ROOT_PROFILE']:
 if key in os.environ:raise SystemExit('profile_rejected')
if os.environ.get('LIFEOS_P3_149_PROFILE','synthetic')!='synthetic':raise SystemExit('profile_rejected')
SPEC=PROFILES[PROFILE];ROOT=Path(SPEC['root']);MARKER=SPEC['marker'];NAME='.lifeos-p3-149-owner.json'
CHILDREN=['tmp','fixtures','.runtime','artifacts','initial-build-cache']
def directory(p):
 s=p.lstat()
 assert stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode)==0o700 and s.st_uid==os.getuid() and p.resolve()==p, 'root_rejected'
def verify(children=True):
 directory(ROOT)
 fd=os.open(ROOT/NAME,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
 with os.fdopen(fd) as f:
  m=os.fstat(f.fileno())
  assert stat.S_ISREG(m.st_mode) and stat.S_IMODE(m.st_mode)==0o600 and m.st_uid==os.getuid() and m.st_size<=4096, 'marker_rejected'
  assert json.load(f)==MARKER, 'marker_rejected'
 if children:
  for name in CHILDREN:directory(ROOT/name)
 return True
def verify_binary(binary):
 result=subprocess.run([str(binary),'--profile-info'],check=True,capture_output=True,text=True)
 assert json.loads(result.stdout)=={'profile':PROFILE,'root':str(ROOT)}, 'binary_profile_mismatch'
 return True
if __name__=='__main__':
 action=sys.argv[1]
 if action=='cleanup':raise SystemExit('S2 retention: cleanup not authorized')
 if action=='init':
  if os.path.lexists(ROOT):verify(children=False)
  else:
   ROOT.mkdir(mode=0o700)
   fd=os.open(ROOT/NAME,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   with os.fdopen(fd,'w') as f:json.dump(MARKER,f)
  for name in CHILDREN:
   p=ROOT/name
   if not os.path.lexists(p):p.mkdir(mode=0o700)
   directory(p)
  verify()
  print('owned synthetic root ready')
 elif action=='verify': print(verify())
 elif action=='describe': print(json.dumps({'profile':PROFILE,**SPEC}))
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
