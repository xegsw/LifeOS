from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((D/'FINAL_MANIFEST.json').read_text())
actual={str(p.relative_to(D)) for p in D.rglob('*') if p.is_file() and p!=D/'FINAL_MANIFEST.json'}
assert actual==set(m['files'])
for name,h in m['files'].items():
 p=D/name;assert p.resolve().is_relative_to(D) and not p.is_symlink();assert sha(p)==h,name
for name,h in m['external_reports'].items():
 p=Path(name);assert p==D.parents[2]/'deliverables/LIFEOS-P3-152_final_closeout.md';assert sha(p)==h
history=json.loads((D/'evidence/history-preservation.json').read_text())
for row in history['packages']:
 p=Path(row['manifest']);assert p.resolve().is_relative_to(D.parent);assert sha(p)==row['sha256'];old=json.loads(p.read_text())
 for name,h in old['files'].items():
  f=p.parent/name;assert f.resolve().is_relative_to(D.parent) and not f.is_symlink();assert sha(f)==h,name
 for name,h in old.get('external_reports',{}).items():
  f=Path(name);assert f.resolve().is_relative_to(D.parents[2]/'deliverables');assert sha(f)==h
print(json.dumps({'status':'pass','closeout_files':len(actual),'historic_file_entries':history['total']}))
