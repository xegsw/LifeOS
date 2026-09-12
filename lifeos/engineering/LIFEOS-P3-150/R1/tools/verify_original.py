import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parents[1];b=r.parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for name,h in m['files'].items():assert sha(b/name)==h,name
assert sha(b.parents[1]/'deliverables/LIFEOS-P3-150_health_import_readonly_view.md')==m['report_sha256']
print(json.dumps(dict(status='pass',original_files=len(m['files']),report=True)))
