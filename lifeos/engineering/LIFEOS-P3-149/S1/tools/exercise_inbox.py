"""Synthetic actual-App exercise, preserves all prior inputs and rows."""
from pathlib import Path
import json,os,sqlite3,time
s=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-149-health-source-v1');marker=json.loads((r/'.lifeos-p3-149-owner.json').read_text());assert marker['task']=='LIFEOS-P3-149' and marker['root']==str(r)
def states():
 c=sqlite3.connect('file:'+str(r/'app.sqlite')+'?mode=ro',uri=True);out=dict(c.execute('select id,body from states order by id').fetchall());c.close();return out
def install(name):
 data=(s/'fixtures'/name).read_bytes();fd=os.open(r/'inbox'/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data)
def wait_value(value):
 for _ in range(16):
  st=states();new=[json.loads(v) for v in st.values() if json.loads(v).get('protocol')=='snapshot-v1']
  if len(new)==1 and new[0]['value']==value:return st
  time.sleep(.5)
 raise AssertionError('receiver did not project expected value')
before=states();install('s1-01-full.json');first=wait_value(120);assert all(first[k]==v for k,v in before.items());install('s1-02-correction.json');corrected=wait_value(140);assert all(corrected[k]==v for k,v in before.items());install('s1-03-partial.json');time.sleep(4);assert states()==corrected
(s/'evidence/actual-ingestion.json').write_text(json.dumps({'before':before,'full':first,'corrected':corrected,'partial_kept_state':True,'old_v1_states_unchanged':True},ensure_ascii=False,indent=2));print('actual App: 120 -> 140; incomplete 170 ignored; original v1 states unchanged')
