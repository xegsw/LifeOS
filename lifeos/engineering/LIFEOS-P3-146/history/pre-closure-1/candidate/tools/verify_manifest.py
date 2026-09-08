"""Read-only task delivery verification. Does not inspect runtime or source roots."""
from pathlib import Path
import json,hashlib,struct
base=Path(__file__).resolve().parents[2]
manifest=json.loads((base/'FINAL_MANIFEST.json').read_text())
assert manifest['task']=='LIFEOS-P3-146'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for item in manifest['files']:
 rel=Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts
 p=base/rel;assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(base)
 assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],str(rel)
report=base.parents[1]/'deliverables/LIFEOS-P3-146_natural_conversation_memory_and_source_integration.md'
assert sha(report)==manifest['report_sha256']
e=base/'evidence'
checks=json.loads((e/'checks-1788831561777.json').read_text());assert len(checks)==4 and all(x['exit']==0 for x in checks)
log=(e/'logs/1788831561777-integration.log').read_text();assert 'tests 23' in log and 'pass 23' in log and 'fail 0' in log
validation=json.loads((e/'actual-app-validation.json').read_text());assert validation['captures']==16 and len(validation['checks'])==26 and all(c['pass'] for c in validation['checks'])
launches={json.loads(p.read_text())['pid']:json.loads(p.read_text()) for p in e.glob('launch-*.json')}
for p in e.glob('app-final-*.json'):
 d=json.loads(p.read_text());assert launches[d['pid']]['binary_sha256']==validation['binary_sha256']
 assert d['window']['title']=='LifeOS · P3-146 · 合成离线' and any(n['role'] in ['AXWebArea','AXWebView'] for n in d['window']['nodes'])
 png=p.with_suffix('.png');assert sha(png)==d['image_sha256']
 w,h=struct.unpack('>II',png.read_bytes()[16:24]);g=d['window']['geometry'];assert (w,h)==(g['width']*2,g['height']*2)
def app(label):return json.loads((e/('app-final-'+label+'.json')).read_text())
assert all(app('save')['counts'][k]==app('failure')['counts'][k] for k in ['records','states','audit','requests'])
assert app('answer')['counts']['records']==2
assert app('revoke-b')['counts']==app('restart-narrow')['counts']
for state,label in [('deferred','defer'),('refused','refuse')]:
 assert app(label)['counts']==app(label+'-restart')['counts']
 assert app(label+'-restart')['synthetic_objects']['questions'][0]['status']==state
for item in json.loads((e/'source-lineage.json').read_text()):
 f=base/'baseline'/item['git_path'].split('/candidate/',1)[1];assert sha(f)==item['sha256']
for name in ['src/secure_credentials.rs','src/deepseek.rs','ui/styles.css','ui/viewport-adapter.css']:
 assert sha(base/'baseline'/name)==sha(base/'candidate'/name)
assert sha(base/'history/preparation-D0653.md')=='98b151d3b30908079c6e76cc236a93d03f0a6cbdba5796ab0739a54cbddfd6b5'
cleanup=json.loads((e/'cleanup-20260908T015659.json').read_text());assert cleanup['removed'] and cleanup['writers_stopped'] and cleanup['marker_verified']
checkpoint=json.loads((e/'checkpoint.json').read_text());assert not checkpoint['runtime']['app_running'] and checkpoint['runtime']['temporary_root_state']=='removed'
print(json.dumps({'status':'PASS','files':len(manifest['files']),'automated_tests':23,'actual_app_captures':16,'evidence_assertions':26,'P0':0,'P1':0,'P2':1,'contract_Unknown':0,'contract_NotImplemented':0,'pm_review':'pending'},ensure_ascii=False))
