import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1]
inputs=json.loads((E/'contract-inputs/code-inputs.json').read_text())['files']
for p,h in inputs.items():
 f=Path(p);assert not f.is_symlink();assert hashlib.sha256(f.read_bytes()).hexdigest()==h,p
prior=E.parent/'LIFEOS-P3-151';m=json.loads((prior/'FINAL_MANIFEST.json').read_text())
for p,h in m['files'].items():assert hashlib.sha256((prior/p).read_bytes()).hexdigest()==h,p
for p,h in m['external_reports'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
print(json.dumps({'status':'pass','code_inputs':len(inputs),'prior_files':len(m['files']),'prior_reports':len(m['external_reports'])}))

fixture=json.loads((E/"contract-inputs/synthetic-fixture.json").read_text())
f=Path(fixture["path"]);assert str(f)=="/private/tmp/lifeos-p3-152-health-conversation-v1/synthetic/health-conversation.sqlite"
assert not f.is_symlink() and hashlib.sha256(f.read_bytes()).hexdigest()==fixture["sha256"]
