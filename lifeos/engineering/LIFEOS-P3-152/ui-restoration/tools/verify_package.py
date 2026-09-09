import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];m=json.loads((D/'FINAL_MANIFEST.json').read_text())
for n,h in m['files'].items():
 p=D/n;assert not p.is_symlink();assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
assert {str(p.relative_to(D)) for p in D.rglob('*') if p.is_file() and p!=D/'FINAL_MANIFEST.json'}==set(m['files'])
print(json.dumps({'status':'pass','files':len(m['files'])}))
