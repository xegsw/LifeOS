from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for p,h in m['files'].items():assert sha(b/p)==h,p
assert sha(Path(m['reportPath']))==m['reportSha256']
base=json.loads((b/'baseline.json').read_text());parent=Path(base['parentRoot'])
assert sha(parent/'FINAL_MANIFEST.json')==base['manifestSha256']
for p,h in base['files'].items():assert sha(parent/p)==h,p
assert sha(Path(base['reportPath']))==base['reportSha256']
for p,h in json.loads((b/'design/fixed-inputs.json').read_text()).items():assert sha(Path(p))==h,p
v=json.loads((b/'evidence/real-bundle.json').read_text())
for p,h in v['candidateFiles'].items():assert sha(b/'candidate'/p)==h,p
assert len(v['candidateFiles'])==166 and not v['launched']
inputs=json.loads((b/'evidence/delivery-regression/replay-inputs.json').read_text())
for p,h in inputs.items():
 if p.startswith('candidate/'):assert sha(b/p)==h,p
assert all(r['exitCode']==0 for r in json.loads((b/'evidence/delivery-regression/rerun-results.json').read_text()))
assert json.loads((b/'evidence/rust-mutations/results.json').read_text())['allKilled']
assert all(v['killed'] for v in json.loads((b/'evidence/flow-mutations.json').read_text()))
assert all(v['killed'] for v in json.loads((b/'evidence/diagnostic-mutations.json').read_text())['results'])
assert json.loads((b/'evidence/source-isolation-mutation.json').read_text())['killed']
cp=json.loads((b/'checkpoint.json').read_text());assert not cp['prohibited_boundary_contact']
print(json.dumps({'files':len(m['files']),'candidateFiles':166,'baselinePreserved':len(base['files']),'checks':208,'mutations':13,'status':m['status'],'resume_from':cp['resume_from'],'realSwitched':False,'visualPass':False}))
