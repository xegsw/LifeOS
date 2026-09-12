from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for p,h in m['files'].items():assert sha(b/p)==h,p
assert sha(Path(m['reportPath']))==m['reportSha256']
s=json.loads((b/'parent-snapshot.json').read_text());parent=Path(s['parentRoot']);assert sha(parent/'FINAL_MANIFEST.json')==s['manifestSha256']
for p,h in s['files'].items():assert sha(parent/p)==h,p
assert sha(Path(s['reportPath']))==s['reportSha256'];assert sha(Path(s['reviewPath']))==s['reviewSha256']
assert sha(parent/'checkpoint.json')==sha(b/'evidence/parent-checkpoint.json')
v=json.loads((b/'evidence/real-bundle.json').read_text())
for p,h in v['candidateFiles'].items():assert sha(parent/'candidate'/p)==h,p
launch=json.loads((b/'evidence/launch.json').read_text());claim=json.loads((b/'evidence/launch-claim.json').read_text());quit=json.loads((b/'evidence/normal-quit.json').read_text());after=json.loads((b/'evidence/identity-after.json').read_text());activation=json.loads((b/'evidence/activation.json').read_text())
assert quit['exited'] and quit['normal_quit_requested'];assert launch['startup']=={'status':'controlled_conversation_started'} and launch['singleAttempt'] and launch['running'];assert launch['binarySha256']==v['binarySha256']==claim['binarySha256'];assert claim['singleAttempt']
assert len(after['instances'])==1 and after['instances'][0]['pid']==launch['pid'] and after['instances'][0]['bundleId']=='local.lifeos.p3-155.source-update';assert activation['pid']==launch['pid'] and activation['activation_requested']
print(json.dumps({'incrementFiles':len(m['files']),'parentPreserved':len(s['files']),'candidateFiles':len(v['candidateFiles']),'switchReceiptVerified':True,'pidAtReceipt':launch['pid'],'userAccepted':False,'visualPass':False}))
