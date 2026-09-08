import sys,json,subprocess,sqlite3,hashlib,datetime
from pathlib import Path
root=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1')
base=Path(__file__).resolve().parents[2];label=sys.argv[1];pid=int(sys.argv[2])
assert label.replace('-','').isalnum()
raw=json.loads(subprocess.check_output([str(root/'native_evidence'),str(pid)]))
windows=[w for w in raw['windows'] if w['title']=='LifeOS · P3-147 · 合成离线']
assert len(windows)==1 and any(n['role'] in ['AXWebArea','AXWebView'] for n in windows[0]['nodes'])
g=windows[0]['geometry']
owned=[w for w in raw['cg'] if w['layer']==0 and w['bounds'].get('Width')==g['width'] and w['bounds'].get('Height')==g['height'] and w['bounds'].get('X')==g['x'] and w['bounds'].get('Y')==g['y']]
assert len(owned)==1
out=base/'evidence'/('app-'+label+'.png');assert not out.exists()
subprocess.run(['/usr/sbin/screencapture','-x','-o','-l',str(owned[0]['id']),str(out)],check=True)
conn=sqlite3.connect('file:'+str(root/'app.sqlite')+'?mode=ro',uri=True)
counts={t:conn.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ['records','states','memories','questions','packets','derivations','drafts','feedback','audit','requests']}
objects={t:[json.loads(row[0]) for row in conn.execute('SELECT body FROM '+t+' ORDER BY id')] for t in ['records','states','memories','questions','derivations','drafts','sources']};conn.close()
result={'schema':'lifeos.p3-147.actual-app.v1','label':label,'pid':pid,'window_attribute':raw.get('window_attribute','AXWindows'),'timestamp':raw['timestamp'],'window':windows[0],'window_id':owned[0]['id'],'image_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'counts':counts,'synthetic_objects':objects}
(base/'evidence'/('app-'+label+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'label':label,'pid':pid,'window_attribute':raw.get('window_attribute','AXWindows'),'geometry':windows[0]['geometry'],'counts':counts,'screenshot':str(out)}))
