from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parents[1];m=json.loads((D/'FINAL_MANIFEST.json').read_text())
actual={str(p.relative_to(D)) for p in D.rglob('*') if p.is_file() and p!=D/'FINAL_MANIFEST.json'}
assert actual==set(m['files'])
for n,h in m['files'].items():
 p=D/n;assert not p.is_symlink();assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
print(json.dumps({'status':'pass','files':len(actual)}))

for n,h in m.get('external_reports',{}).items():
 p=Path(n);assert p==D.parents[2]/'deliverables/LIFEOS-P3-152_credential_save_fix.md';assert not p.is_symlink();assert hashlib.sha256(p.read_bytes()).hexdigest()==h
