from pathlib import Path
import hashlib,json
b=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for p,h in m['files'].items():assert sha(b/p)==h,p
assert sha(Path(m['reportPath']))==m['reportSha256']
child=b;history=[]
for _ in range(3):
 s=json.loads((child/'parent-snapshot.json').read_text());parent=Path(s.get('parentRoot',str(child.parent)))
 assert sha(parent/'FINAL_MANIFEST.json')==s['manifestSha256']
 for p,h in s['files'].items():assert sha(parent/p)==h,p
 assert sha(Path(s['reportPath']))==s['reportSha256'];history.append(len(s['files']));child=parent
assert all(v['exitCode']==0 for v in json.loads((b/'evidence/affected/affected-rerun-results.json').read_text()))
assert all(v['killed'] for v in json.loads((b/'evidence/flow-mutations.json').read_text()))
assert all(v['killed'] for v in json.loads((b/'evidence/diagnostic-mutations.json').read_text())['results'])
launch=json.loads((b/'evidence/launch.json').read_text());assert launch['startup']=={'status':'controlled_conversation_started'}
v=json.loads((b/'evidence/real-bundle.json').read_text())
for p,h in v['candidateFiles'].items():assert sha(b/'candidate'/p)==h,p
print(json.dumps({'files':len(m['files']),'parentFilesPreserved':history,'businessFailureClosed':False,'status':m['status']}))
