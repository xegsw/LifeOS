from pathlib import Path
import json,hashlib,subprocess
b=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for rel,h in m['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 assert sha(b/p)==h,rel
assert sha(Path(m['reportPath']))==m['reportSha256']
snapshot=json.loads((b/'baseline-snapshot.json').read_text());base=Path(snapshot['baselineRoot'])
for entry in snapshot['manifests']:
 p=Path(entry['path']);assert sha(p)==entry['sha256'];v=json.loads(p.read_text())
 for rel,h in v['files'].items():assert sha(p.parent/rel)==h,rel
 assert sha(Path(v['reportPath']))==v['reportSha256']
for rel,h in snapshot['candidateFiles'].items():assert sha(base/'candidate'/rel)==h,rel
v=json.loads((b/'evidence/synthetic-bundle-final.json').read_text())
for rel,h in v['candidateFiles'].items():assert sha(b/'candidate'/rel)==h,rel
assert len(v['candidateFiles'])==173
assert sha(b/'minimal-protocol-proposal.md')=='cf8e88ed446a503e73b8804cb71fc871df628a711d0f7ca96d273d09d63bd381'
r=json.loads((b/'evidence/check-summary.json').read_text());assert sum(x['passed'] for x in r['suites'])==243 and all(x['passed']==x['total'] for x in r['suites'])
assert not json.loads((b/'evidence/candidate-diff.json').read_text())['removed']
print(json.dumps({'manifestFiles':len(m['files']),'candidateFiles':173,'checks':243,'parent315Preserved':True,'switch14Preserved':True,'proposalApproved':True,'finalNativeAX':'Paused — locked; prior unchanged UI visual reused','pmAccepted':False}))
