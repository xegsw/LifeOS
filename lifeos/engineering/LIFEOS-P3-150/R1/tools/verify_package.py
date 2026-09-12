import json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[1];m=json.loads((r/'FINAL_MANIFEST.json').read_text())
for name,h in m['files'].items():
 p=Path(name);assert not p.is_absolute() and '..' not in p.parts;assert hashlib.sha256((r/p).read_bytes()).hexdigest()==h,name
print(json.dumps(dict(status='pass',files=len(m['files']))))
