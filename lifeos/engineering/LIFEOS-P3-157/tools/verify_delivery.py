"""Read only workspace evidence and code. Never inspect live real assets."""
from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for rel,h in m['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 assert sha(b/p)==h,rel
assert sha(Path(m['reportPath']))==m['reportSha256']
snapshot=json.loads((b/'baseline-snapshot.json').read_text());parent=Path(snapshot['parentRoot']);assert sha(parent/'FINAL_MANIFEST.json')==snapshot['manifestSha256']
for rel,h in snapshot['files'].items():assert sha(parent/rel)==h,rel
assert sha(Path(snapshot['reportPath']))==snapshot['reportSha256']
for rel,h in snapshot['candidateFiles'].items():assert sha(parent/'candidate'/rel)==h,rel
v=json.loads((b/'evidence/real-bundle.json').read_text())
for rel,h in v['candidateFiles'].items():assert sha(b/'candidate'/rel)==h,rel
assert len(v['candidateFiles'])==174
s=json.loads((b/'evidence/check-summary.json').read_text());assert sum(x['passed'] for x in s['suites'])+len(s['buildModeGuards'])==s['checks']==254
assert all(x['passed']==x['total'] for x in s['suites']) and all(x['passed'] for x in s['buildModeGuards'])
for suite in s['suites']:assert sha(b/suite['log'])==suite['sha256']
mut=json.loads((b/'evidence/mutations/results.json').read_text());assert mut['allKilled'] and len(mut['results'])==5 and all(x['validMutation'] and x['killed'] for x in mut['results'])
claim=json.loads((b/'evidence/launch-claim.json').read_text());launch=json.loads((b/'evidence/launch.json').read_text());quit=json.loads((b/'evidence/normal-quit.json').read_text());after=json.loads((b/'evidence/identity-after.json').read_text());assert claim['singleAttempt'] and launch['singleAttempt'];assert claim['binarySha256']==launch['binarySha256']==v['binarySha256'];assert launch['startup']=={'status':'controlled_conversation_started'} and launch['directPidMatched'] and launch['running'];assert quit['exited'];assert len(after['instances'])==1 and after['instances'][0]['pid']==launch['pid'] and after['instances'][0]['bundleId']=='local.lifeos.p3-157.real-actions'
assert not json.loads((b/'evidence/candidate-diff.json').read_text())['removed']
print(json.dumps({'manifestFiles':len(m['files']),'candidateFiles':174,'parent156Preserved':244,'checks':254,'validMutationsKilled':5,'switchReceiptVerified':True,'pidAtReceipt':launch['pid'],'userAccepted':False,'independentPass':False}))
