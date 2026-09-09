import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1]
d=json.loads((E/'FINAL_MANIFEST.json').read_text())
for p,h in d['files'].items():
 f=E/p;assert not f.is_symlink();assert hashlib.sha256(f.read_bytes()).hexdigest()==h,p
for p,h in d['external_reports'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
print(json.dumps({'verified_files':len(d['files']),'external_reports':len(d['external_reports']),'status':'pass'}))
