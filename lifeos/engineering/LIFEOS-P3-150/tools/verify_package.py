import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1];manifest=json.loads((p/'FINAL_MANIFEST.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name,h in manifest['files'].items():
 rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts;assert sha(p/rel)==h,name
report=p.parents[1]/'deliverables/LIFEOS-P3-150_health_import_readonly_view.md';assert sha(report)==manifest['report_sha256']
assert json.loads((p/'evidence/real-launch.json').read_text())['startup']==dict(status='readonly_view_started',mode='real')
print(json.dumps(dict(status='pass',files=len(manifest['files']),report=True,real_receipt='fixed_status_only')))
