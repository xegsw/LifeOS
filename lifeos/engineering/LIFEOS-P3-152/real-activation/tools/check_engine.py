from pathlib import Path
import json,stat,os,hashlib
D=Path(__file__).resolve().parents[1];m=json.loads((D/'design/fixture-identity.json').read_text());R=Path(m['root'])
assert not R.is_symlink() and R.resolve()==R and stat.S_IMODE(R.stat().st_mode)==0o700
owner=R/'.owner.json';assert not owner.is_symlink() and stat.S_IMODE(owner.stat().st_mode)==0o600
assert json.loads(owner.read_text())=={'task':'P3-152','owner':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484','root':str(R),'kind':'synthetic-source-engine'}
for name,h in m['files'].items():
 p=R/name;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
print('synthetic fixture identity verified')
