"""Bootstrap the exact approved synthetic root, refusing foreign existing markers."""
from pathlib import Path
import json, os, stat
ROOT=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1')
THREAD='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
os.umask(0o077)
def directory(p):
    try:p.mkdir(mode=0o700)
    except FileExistsError:pass
    m=p.lstat()
    assert stat.S_ISDIR(m.st_mode) and stat.S_IMODE(m.st_mode)==0o700 and m.st_uid==os.getuid()
    assert p.resolve()==p
def marker(p,expected):
    try:
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    except FileExistsError:
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd) as f:
            m=os.fstat(f.fileno());assert stat.S_ISREG(m.st_mode) and m.st_nlink==1 and stat.S_IMODE(m.st_mode)==0o600 and m.st_uid==os.getuid()
            assert json.load(f)==expected
    else:
        with os.fdopen(fd,'w') as f:json.dump(expected,f);f.write('\n')
directory(ROOT)
marker(ROOT/'.owner.json',dict(task='P3-159',root=str(ROOT),owner=THREAD))
directory(ROOT/'build')
root=ROOT/'offline';directory(root)
marker(root/'.owner.json',dict(task='P3-159',root=str(root),owner=THREAD,mode='synthetic'))
for n in ['synthetic','tmp','source-engine']:directory(root/n)
marker(root/'source-engine/.owner.json',dict(task='P3-159',root=str(root/'source-engine'),owner=THREAD,kind='synthetic-source-engine'))
print('P3-159 offline root verified')
