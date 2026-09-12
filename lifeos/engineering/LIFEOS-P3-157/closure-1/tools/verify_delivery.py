"""Read only evidence and source files, never live real data or UI."""
from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for rel,h in m['files'].items():
 q=Path(rel);assert not q.is_absolute() and '..' not in q.parts;assert sha(b/q)==h,rel
assert sha(Path(m['reportPath']))==m['reportSha256']
h=json.loads((b/'history-snapshot.json').read_text());parent=Path(h['parentRoot']);assert sha(parent/'FINAL_MANIFEST.json')==h['manifestSha256']
for rel,v in h['files'].items():assert sha(parent/rel)==v,rel
assert sha(Path(h['reportPath']))==h['reportSha256']
s=json.loads((b/'evidence/check-summary.json').read_text());assert sum(x['passed'] for x in s['suites'])==279 and s['checks']==281
for x in s['suites']:assert x['passed']==x['total'] and x['exitCode']==0 and sha(b/x['log'])==x['sha256']
assert len(s['buildModeGuards'])==2 and all(x['passed'] for x in s['buildModeGuards'])
v=json.loads((b/'evidence/mutations/results.json').read_text());assert len(v['results'])==6 and v['allKilled'] and all(x['validMutation'] and x['killed'] for x in v['results'])
v=json.loads((b/'evidence/real-bundle.json').read_text());assert len(v['candidateFiles'])==174
for rel,h in v['candidateFiles'].items():assert sha(b/'candidate'/rel)==h,rel
launch=json.loads((b/'evidence/launch.json').read_text());after=json.loads((b/'evidence/identity-after.json').read_text());claim=json.loads((b/'evidence/launch-claim.json').read_text());quit=json.loads((b/'evidence/normal-quit.json').read_text())
assert launch['directPidMatched'] and launch['singleAttempt'] and launch['running'] and claim['singleAttempt'];assert launch['binarySha256']==v['binarySha256']==claim['binarySha256'];assert launch['startup']=={'status':'controlled_conversation_started'};assert quit['exited'] and quit['normal_quit_requested'];assert after['instances'][0]['pid']==launch['pid'] and len(after['instances'])==1 and after['instances'][0]['bundleId']=='local.lifeos.p3-157.c1-real-actions'
assert json.loads((b/'checkpoint.json').read_text())['resume_from']=='user_actual_actions_validation'
print(json.dumps(dict(manifestFiles=len(m['files']),candidateFiles=174,checks=281,validMutationsKilled=6,switchReceiptPid=launch['pid'],userAccepted=False,independentPass=False)))
