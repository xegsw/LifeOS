"""Authorized local semantic preflight. Only fixed category counts leave the process."""
import os,stat,json,importlib.util
from pathlib import Path
s=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_parser',s/'candidate/tools/apple_health_source.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
fds=[];chain=[];result=None
try:
 d=os.open('/',os.O_RDONLY|os.O_DIRECTORY);fds.append(d)
 for n in ['Users','xxe','Downloads']:
  q=os.open(n,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=d);chain.append((d,n,q));fds.append(q);d=q
 fd=os.open('导出.zip',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=d);fds.append(fd);before=os.fstat(fd)
 if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_uid!=os.getuid():raise ValueError()
 def consume(v):
  global result
  if v['event']=='end':result={k:v[k] for k in ['supported','unsupported','skipped','skipReasons','unprojected','compatibility','attachments']}
 with os.fdopen(os.dup(fd),'rb') as f:parser.run(f,dict(parser.DEFAULTS),consume)
 for parent,n,child in chain:
  a=os.stat(n,dir_fd=parent,follow_symlinks=False);b=os.fstat(child)
  if not stat.S_ISDIR(a.st_mode) or (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError()
 after=os.stat('导出.zip',dir_fd=d,follow_symlinks=False)
 identity=lambda m:(m.st_dev,m.st_ino,m.st_size,m.st_mtime_ns,m.st_ctime_ns)
 if identity(before)!=identity(after):raise ValueError()
 if result is None:raise ValueError()
 result['status']='preflight_complete';result['scanned']=result['supported']+result['unsupported']+result['skipped'];result['database_written']=False
except Exception as e:
 code=str(e) if isinstance(e,parser.Rejected) and str(e).startswith('health_') and all(c in 'abcdefghijklmnopqrstuvwxyz_' for c in str(e)) else 'preflight_failed'
 result={'status':'failed','code':code,'database_written':False}
finally:
 for fd in reversed(fds):os.close(fd)
with (s/'evidence/semantic-preflight.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
