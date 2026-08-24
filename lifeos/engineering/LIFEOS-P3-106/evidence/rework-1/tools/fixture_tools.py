#!/usr/bin/env python3
import hashlib,json,sqlite3,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]; ENG=ROOT/'lifeos/engineering/LIFEOS-P3-106'; EV=ENG/'evidence/rework-1'; FIX=Path('/private/tmp/lifeos-p3-104-p3-106-app-rework1-20260823'); DB=FIX/'capture.sqlite'; SENT=FIX/'sentinel.txt'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
 try: s=p.lstat(); return {'exists':True,'type':stat.filemode(s.st_mode)[0],'size':s.st_size,'mtime_ns':s.st_mtime_ns,'ctime_ns':s.st_ctime_ns}
 except FileNotFoundError: return {'exists':False}
def prepare():
 if meta(FIX)['exists']: raise RuntimeError('fixture occupied')
 FIX.mkdir(mode=0o700); SENT.write_text('LIFEOS-P3-106 rework-1 fixed non-sensitive sentinel\n'); d={'fixture':str(FIX),'db':str(DB),'sentinel':str(SENT),'sentinel_sha256':sha(SENT),'database_pre_lstat':meta(DB),'status':'PASS'}; (EV/'main_fixture_before.json').write_text(json.dumps(d,indent=2)+'\n')
def snap(label):
 q=None; captures=audits=None; actions=[]
 if DB.is_file():
  with sqlite3.connect(f'file:{DB}?mode=ro&immutable=1',uri=True) as c:
   q=c.execute('PRAGMA quick_check').fetchone()[0]; captures=c.execute('SELECT COUNT(*) FROM captures').fetchone()[0]; audits=c.execute('SELECT COUNT(*) FROM audit').fetchone()[0]; actions=[x[0] for x in c.execute('SELECT event FROM audit ORDER BY id')]
 d={'label':label,'fixture':str(FIX),'db_metadata':meta(DB),'db_sha256':sha(DB) if DB.is_file() else None,'quick_check':q,'captures':captures,'audits':audits,'audit_actions':actions,'sentinel_metadata':meta(SENT),'sentinel_sha256':sha(SENT),'sidecars':{x:meta(Path(str(DB)+f'-{x}')) for x in ['journal','wal','shm']},'status':'PASS' if q=='ok' and sha(SENT)==sha(SENT) else 'FAIL'}; (EV/f'fixture-{label}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':
 import sys
 prepare() if sys.argv[1]=='prepare' else snap(sys.argv[1])
