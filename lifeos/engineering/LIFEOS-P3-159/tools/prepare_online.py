"""Prepare only the owned public-synthetic B root. No App, DB, profile or network access."""
from pathlib import Path
import json,os,stat,shutil
root=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1');b=Path(__file__).resolve().parents[1];owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484';os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())==dict(task='P3-159',root=str(root),owner=owner)
def directory(p):
 try:p.mkdir(mode=0o700)
 except FileExistsError:pass
 m=p.lstat();assert stat.S_ISDIR(m.st_mode) and stat.S_IMODE(m.st_mode)==0o700 and m.st_uid==os.getuid() and p.resolve()==p
def marker(p,value):
 try:f=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 except FileExistsError:
  m=p.lstat();assert stat.S_ISREG(m.st_mode) and m.st_nlink==1 and m.st_uid==os.getuid() and stat.S_IMODE(m.st_mode)==0o600
  assert json.loads(p.read_text())==value
 else:
  with os.fdopen(f,'w') as stream:json.dump(value,stream)
r=root/'online-synthetic';directory(r);marker(r/'.owner.json',dict(task='P3-159',root=str(r),owner=owner,mode='online-synthetic'))
for name in ['synthetic','tmp','source-engine']:directory(r/name)
marker(r/'source-engine/.owner.json',dict(task='P3-159',root=str(r/'source-engine'),owner=owner,kind='synthetic-source-engine'))
marker(r/'.test-phase.json',{'phase':'development'})
manifest=json.loads((b/'evidence/B-package-unsigned.json').read_text());source=Path(manifest['app'])/'Contents/Resources/alias_metadata';dest=r/'source-engine/alias_metadata'
if dest.exists():
 import hashlib
 assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(dest.read_bytes()).digest()
else:shutil.copy2(source,dest)
print('B synthetic root prepared; no database/profile/network access; app not launched')
