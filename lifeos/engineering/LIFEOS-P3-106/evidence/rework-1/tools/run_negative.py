#!/usr/bin/env python3
import hashlib,json,os,shutil,sqlite3,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]; ENG=ROOT/'lifeos/engineering/LIFEOS-P3-106'; EV=ENG/'evidence/rework-1'; BIN=ENG/'target/debug/lifeos-p3-104'; SRC=Path('/private/tmp/lifeos-p3-104-p3-106-app-rework1-20260823/capture.sqlite')
base='/private/tmp/lifeos-p3-104-p3-106-'; names=['dangling-final','dangling-journal','dangling-wal','dangling-shm','path','path-target','tamper']; F={n:Path(base+n+'-rework1-20260823') for n in names}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def prep(p): p.mkdir(mode=0o700); s=p/'sentinel.txt'; s.write_text('LIFEOS-P3-106 rework-1 fixed non-sensitive sentinel\n'); return s
def run(rid,db,s):
 b=sha(s); env=os.environ.copy(); env['LIFEOS_P3_104_DB_PATH']=str(db); c=subprocess.run([str(BIN)],cwd=ENG,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=8); log=EV/f'{rid.lower()}.log'; log.write_text(c.stdout); return {'id':rid,'returncode':c.returncode,'sentinel_unchanged':b==sha(s),'log':str(log.relative_to(ENG)),'log_sha256':sha(log),'status':'PASS' if c.returncode!=0 and b==sha(s) else 'FAIL'}
if any(os.path.lexists(x) for x in F.values()): raise RuntimeError('negative fixture occupied')
rows=[]; root=F['dangling-final']; s=prep(root); db=root/'capture.sqlite'; miss=root/'missing.sqlite'; db.symlink_to(miss); x=run('ACTUAL-DANGLING-FINAL',db,s); x.update({'link_preserved':db.is_symlink(),'target_absent':not miss.exists()}); x['status']='PASS' if x['status']=='PASS' and x['link_preserved'] and x['target_absent'] else 'FAIL'; rows.append(x)
for suffix in ['journal','wal','shm']:
 root=F['dangling-'+suffix]; s=prep(root); db=root/'capture.sqlite'; shutil.copyfile(SRC,db); side=Path(str(db)+'-'+suffix); miss=root/('missing-'+suffix); side.symlink_to(miss); before=sha(db); x=run('ACTUAL-DANGLING-'+suffix.upper(),db,s); x.update({'link_preserved':side.is_symlink(),'target_absent':not miss.exists(),'db_unchanged':before==sha(db)}); x['status']='PASS' if x['status']=='PASS' and all([x['link_preserved'],x['target_absent'],x['db_unchanged']]) else 'FAIL'; rows.append(x)
target=F['path-target']; s=prep(target); F['path'].symlink_to(target,target_is_directory=True); db=F['path']/'capture.sqlite'; x=run('ACTUAL-PARENT-SYMLINK',db,s); x.update({'parent_link_preserved':F['path'].is_symlink(),'db_absent':not db.exists()}); x['status']='PASS' if x['status']=='PASS' and x['parent_link_preserved'] and x['db_absent'] else 'FAIL'; rows.append(x)
tam=F['tamper']; s=prep(tam); db=tam/'capture.sqlite'; shutil.copyfile(SRC,db)
with sqlite3.connect(db) as c: c.execute("UPDATE captures SET content='P3-106 rework-1 fixed tampered content'"); c.commit()
d={'task':'LIFEOS-P3-106','execution':'rework-1','rows':rows,'tamper_prepared':{'db':str(db),'sentinel_sha256':sha(s),'status':'PASS'},'dangling_4_passed':sum(x['status']=='PASS' and x['id'].startswith('ACTUAL-DANGLING') for x in rows)}; d['status']='PASS' if all(x['status']=='PASS' for x in rows) and d['dangling_4_passed']==4 else 'FAIL'; (EV/'negative_results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':d['status'],'dangling':d['dangling_4_passed']})); raise SystemExit(0 if d['status']=='PASS' else 1)
