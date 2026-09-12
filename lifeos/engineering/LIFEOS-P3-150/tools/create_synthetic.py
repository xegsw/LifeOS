import os, json, sqlite3
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-150-health-view-v1')
assert json.loads((ROOT/'.owner.json').read_text())['task']=='P3-150'
os.umask(0o077)
p=ROOT/'synthetic/health-import.sqlite'
assert not p.exists()
c=sqlite3.connect(p)
c.executescript('CREATE TABLE states(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE records(id TEXT PRIMARY KEY,body TEXT);CREATE TABLE sources(id TEXT PRIMARY KEY,body TEXT);')
for m in ['sleep','steps','exercise']:
 for source,offset in [('Synthetic Watch',480),('Synthetic Phone',480),('Synthetic Watch',0)]:
  for day in range(20570,20700):
   if day%13==0: continue
   value=None if day%17==0 else (400+(day%9)*8 if m=='sleep' else 2000+day%12*650 if m=='steps' else day%7*9)
   b=dict(protocol='apple-file-v1',kind='health_current_state',metric=m,dayIndex=day,offsetMinutes=offset,sources=[dict(name=source)],value=value,estimated=m=='sleep',method='file_observation_uncertain' if value is None else 'subset',observedAt=day*86400000,receivedAt=20701*86400000)
   c.execute('INSERT INTO states VALUES(?,?)',(f'{m}-{source}-{offset}-{day}',json.dumps(b)))
for i in range(36):
 b=dict(protocol='apple-file-v1',kind='health_current_state',metric='steps',dayIndex=20570,offsetMinutes=0,sources=[dict(name=f'Synthetic Archive {i:02}')],value=500)
 c.execute('INSERT INTO states VALUES(?,?)',(f'archive-{i}',json.dumps(b)))
c.executemany('INSERT INTO records VALUES(?,?)',((f'health-apple-content:{i:09}',json.dumps(dict(kind='health_observation',value=i%10,protocol='apple-file-v1'))) for i in range(250000)))
c.execute('INSERT INTO records VALUES(?,?)',('health-apple-batch:synthetic',json.dumps(dict(protocol='apple-file-v1',kind='health_batch',receivedAt=20701*86400000))))
c.commit();c.close()
print(json.dumps(dict(status='synthetic_fixture_created',observations=250000)))
