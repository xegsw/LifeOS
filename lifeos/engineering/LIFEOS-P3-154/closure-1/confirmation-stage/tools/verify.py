from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for p,h in m['files'].items():assert sha(b/p)==h,p
assert sha(Path(m['reportPath']))==m['reportSha256']
s=json.loads((b/'parent-snapshot.json').read_text());assert sha(b.parent/'FINAL_MANIFEST.json')==s['manifestSha256']
for p,h in s['files'].items():assert sha(b.parent/p)==h,p
assert sha(Path(s['reportPath']))==s['reportSha256']
s2=json.loads((b.parent/'parent-snapshot.json').read_text())
assert sha(b.parent.parent/'FINAL_MANIFEST.json')==s2['manifestSha256']
for p,h in s2['files'].items():assert sha(b.parent.parent/p)==h,p
assert sha(Path(s2['reportPath']))==s2['reportSha256']
assert json.loads((b/'evidence/storage-stage-mutation.json').read_text())['killed']

assert all(v['exitCode']==0 for v in json.loads((b/'evidence/affected/affected-rerun-results.json').read_text()))
assert all(v['killed'] for v in json.loads((b/'evidence/diagnostic-mutations.json').read_text())['results'])
print(json.dumps({'files':len(m['files']),'parentPreserved':len(s['files']),'status':m['status'],'businessFailureClosed':False}))
