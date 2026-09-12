import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parents[1];E=D.parent
m=json.loads((D/'synthetic-baseline/FINAL_MANIFEST.json').read_text())
for n,h in m['files'].items():
 assert hashlib.sha256((E/n).read_bytes()).hexdigest()==h,n
 assert hashlib.sha256((D/'synthetic-baseline'/n).read_bytes()).hexdigest()==h,n
for n,h in m['external_reports'].items():assert hashlib.sha256(Path(n).read_bytes()).hexdigest()==h,n
print(json.dumps({'status':'pass','synthetic_files':len(m['files']),'reports':len(m['external_reports'])}))
