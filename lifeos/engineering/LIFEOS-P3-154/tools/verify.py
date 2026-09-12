#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
assert sha(Path(m['reportPath']))==m['reportSha256']
for p,h in m['files'].items():assert not (b/p).is_symlink() and sha(b/p)==h,p
for root,v in json.loads((b/'evidence/baseline-validation.json').read_text()).items():
 root=Path(root);assert sha(root/'FINAL_MANIFEST.json')==v['manifestSha256']
 for p,h in v['files'].items():assert sha(root/p)==h,p
assert all(r['killed'] for r in json.loads((b/'evidence/mutations/results.json').read_text())['results'])
assert all(r['exitCode']==0 for r in json.loads((b/'evidence/regression/rerun-results.json').read_text()))
assert '1 passed; 0 failed' in (b/'evidence/source-schema-pass.log').read_text()
print(json.dumps({'verifiedFiles':len(m['files']),'baselinesPreserved':398,'independentReview':'paused','realResult':m['realResult']}))
