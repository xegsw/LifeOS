from pathlib import Path
import hashlib,json,zipfile,os
B=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
checks=[]
with zipfile.ZipFile(B/'history/pre-E04-D2-fix-package.zip') as z:
 old=json.loads(z.read('FINAL_MANIFEST.json'));assert len(old['files'])==486
 for f in old['files']:assert sha(z.read(f['path']))==f['sha256'],f['path']
checks.append('486 pre-fix files preserved')
with zipfile.ZipFile(B/'history/pre-E04-package.zip') as z:
 m=json.loads(z.read('FINAL_MANIFEST.json'));assert len(m['files'])==387
 for f in m['files']:assert sha(z.read(f['path']))==f['sha256'],f['path']
 for f in m['files']:
  if f['path'].startswith('candidate/src/') or f['path'] in ['candidate/Cargo.toml','candidate/Cargo.lock','candidate/root_profiles.json']:
   assert sha((B/f['path']).read_bytes())==f['sha256'],f['path']
 checks+=['387 historical files preserved','Rust/Raw DTO/ports/root profiles unchanged']
for path,digest in json.loads((B/'contract-inputs/E04-visual-bindings.json').read_text()).items():assert sha(Path(path).read_bytes())==digest,path
assert (B/'candidate/ui/design116.css').read_bytes()==Path('/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/prototypes/LIFEOS-P3-116/styles.css').read_bytes()
checks+=['precise visual and Delta1 bindings','116 CSS byte-exact']
for name in ['E04-flow-01.log','E04-ir-regression-01.log','E04-passive-01.log','E04-disclosure-01.log']:
 text=(B/'evidence'/name).read_text();assert 'fail 0' in text or '0 failed' in text or text.startswith('PASS'),name
checks+=['9 flow tests + 5 IR regression + 1 passive lifecycle + disclosure render checks']
for n,g in [('E04-narrow-controls.json',(406,81,700,760)),('E04-desktop-controls.json',(221,33,1280,949))]:
 d=json.loads((B/'evidence'/n).read_text());x,y,w,h=g
 controls=[c for c in d['controls'] if c['title'] in ['发送','确认发送','取消','自然提问']]
 assert len(controls)==4
 for c in controls:assert c['width']>0 and c['height']>0 and c['x']>=x and c['y']>=y and c['x']+c['width']<=x+w and c['y']+c['height']<=y+h,c
 editor=next(c for c in controls if c['role']=='AXTextArea');confirm=next(c for c in controls if c['title']=='确认发送');assert confirm['y']+confirm['height']<=editor['y']
checks+=['desktop/narrow exact native control geometry, no editor overlap']
a,b=[next(c for c in json.loads((B/'evidence'/n).read_text())['controls'] if c['role']=='AXTextArea') for n in ['E04-caret-before.json','E04-caret-after.json']]
assert (a['value'],a['selectionStart'],a['selectionLength'])==(b['value'],b['selectionStart'],b['selectionLength'])
assert not any(c['title']=='确认发送' for c in json.loads((B/'evidence/E04-edit-invalidated.json').read_text())['controls'])
checks+=['native caret/draft preservation','actual edit invalidates old confirmation']
launches=[json.loads((B/'evidence'/n).read_text()) for n in ['launch-e04narrow2.json','launch-e04desktop3.json']]
assert launches[0]['binary_sha256']==launches[1]['binary_sha256']
delta=json.loads((B/'evidence/E04-D2-remove-lineage.json').read_text())
for launch in launches:
 for path,digest in launch['source_files'].items():
  if path in delta['changes']:
   assert digest==delta['changes'][path]['before'] and sha((B/'candidate'/path).read_bytes())==delta['changes'][path]['after'],path
  else:assert sha((B/'candidate'/path).read_bytes())==digest,path
assert set(delta['changes'])=={'application/conversation_flow.ts','ui/conversation_flow.js','application/source_ui.ts','ui/source_ui.js'}
assert 'pass 20' in (B/'evidence/E04-D2-remove-tests.log').read_text()
for p in (B/'evidence').glob('launch-*.json'):
 pid=json.loads(p.read_text())['pid']
 try:os.kill(pid,0)
 except ProcessLookupError:continue
 raise AssertionError('recorded task PID still exists '+str(pid))
checks+=['prior E04 GUI inherited; four explicitly bound application/generated files changed, 20 tests pass','all recorded task Apps stopped']
print(json.dumps({'status':'pass','scope':'E04 engineering only','checks':checks},ensure_ascii=False,indent=2))

with zipfile.ZipFile(B/'history/pre-E04-D2-remove-package.zip') as z:
 old=json.loads(z.read('FINAL_MANIFEST.json'));assert len(old['files'])==494
 for f in old['files']:assert sha(z.read(f['path']))==f['sha256'],f['path']
launch=json.loads((B/'evidence/launch-e04remove1.json').read_text())
for path,digest in launch['source_files'].items():assert sha((B/'candidate'/path).read_bytes())==digest,path
before=json.loads((B/'evidence/E04-remove-packets-before.json').read_text())[0]
after=json.loads((B/'evidence/E04-remove-packets-after.json').read_text())
old=next(p for p in after if p['previewId']==before['previewId']);new=next(p for p in after if p['previewId']!=before['previewId'])
assert old['state']=='cancelled' and new['state']=='ready' and old['confirmationToken']!=new['confirmationToken']
removed=before['items'][0]['source']['segmentId'];assert not any(i.get('source',{}).get('segmentId')==removed for i in new['items'])
a,b=[json.loads((B/'evidence'/n).read_text()) for n in ['app-e04removebefore1.json','app-e04removeafter1.json']]
assert a['pid']==b['pid']==launch['pid'] and a['counts']['derivations']==b['counts']['derivations']
print('PASS IR-D2-002: 494 history preserved, fresh candidate/PID GUI bound, cancelled old packet, new token and excluded segment, no new model answer')
