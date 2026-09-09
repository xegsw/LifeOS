# coding: utf-8
"""Read only S2 synthetic health namespaces; never select credentials or other roots."""
from pathlib import Path
import sys,json,sqlite3,hashlib
s=Path(__file__).resolve().parents[1];label=sys.argv[1];assert label.replace('-','').isalnum()
c=sqlite3.connect('file:/private/tmp/lifeos-p3-149-health-source-v1/S2/app.sqlite?mode=ro',uri=True)
v={}
for t in ['records','sources','states']:
 h=hashlib.sha256();count=0;kinds={};summary=[]
 for id,body in c.execute('SELECT id,body FROM '+t+" WHERE json_extract(body,'$.protocol')='apple-file-v1' ORDER BY id"):
  b=json.loads(body);h.update(json.dumps([id,body],ensure_ascii=False).encode());count+=1;kinds[b['kind']]=kinds.get(b['kind'],0)+1
  if b['kind'] in ['health_batch','health_source','health_current_state']:summary.append(b)
 v[t]={'count':count,'digest':h.hexdigest(),'kinds':kinds,'summary':summary}
c.close();p=s/'evidence'/('db-'+label+'.json')
with p.open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
print(json.dumps({k:{'count':x['count'],'kinds':x['kinds']} for k,x in v.items()}))
