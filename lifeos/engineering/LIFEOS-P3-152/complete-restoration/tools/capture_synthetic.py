import json,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-152-health-conversation-v1');ENGINE=Path(__file__).resolve().parents[1]

r=json.loads((ENGINE/'evidence/synthetic-launch.json').read_text());assert r['mode']=='synthetic'
assert hashlib.sha256(Path(r['binary']).read_bytes()).hexdigest()==r['binary_sha256']
actual=subprocess.check_output(['/bin/ps','-p',str(r['pid']),'-o','comm='],text=True).strip();assert actual==r['binary']
tag=sys.argv[1];assert tag.replace('-','').isalnum()
out=subprocess.check_output([str(ROOT/'complete_evidence'),str(r['pid'])],text=True);data=json.loads(out)
assert len(data['windows'])==1 and data['windows'][0]['title']=='LifeOS P3-152 - Synthetic Conversation'
assert any(n['role'] in ('AXWebArea','AXWebView') for n in data['windows'][0]['nodes'])
(ENGINE/f'evidence/{tag}.json').write_text(json.dumps(data,indent=2))
window=[w for w in data['cg'] if w['layer']==0 and abs(w['bounds'].get('Width',0)-data['windows'][0]['geometry']['width'])<=1 and abs(w['bounds'].get('Height',0)-data['windows'][0]['geometry']['height'])<=1 and abs(w['bounds'].get('X',0)-data['windows'][0]['geometry']['x'])<=1];assert len(window)==1
subprocess.run(['/usr/sbin/screencapture','-x','-o','-l',str(window[0]['id']),str(ENGINE/f'evidence/{tag}.png')],check=True)
print(json.dumps(dict(status='synthetic_captured',tag=tag,pid=r['pid'],geometry=data['windows'][0]['geometry'])))
