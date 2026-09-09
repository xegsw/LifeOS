import json,sqlite3,subprocess,os,signal,time,hashlib
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-150-health-view-v1');E=Path(__file__).resolve().parents[1]/'evidence'
assert not (E/'real-launch.json').exists()
assert json.loads((ROOT/'.owner.json').read_text())['task']=='P3-150'
r=json.loads((E/'synthetic-launch.json').read_text());assert r['mode']=='synthetic'
def identity(pid):return subprocess.check_output(['/bin/ps','-p',str(pid),'-o','comm='],text=True).strip()==r['binary']
def snap():
 p=ROOT/'synthetic/health-import.sqlite'
 return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,sidecars={s:Path(str(p)+s).exists() for s in ['-wal','-shm','-journal']})
assert identity(r['pid']);before=snap()
c=sqlite3.connect(ROOT/'synthetic/health-import.sqlite');c.execute('BEGIN EXCLUSIVE')
subprocess.run([str(ROOT/'health_ax'),str(r['pid']),'press','最近有数据'],check=True)
time.sleep(.6)
subprocess.run(['/usr/bin/python3',str(E.parent/'tools/capture_synthetic.py'),'readonly-busy-error'],check=True)
c.rollback();c.close()
subprocess.run([str(ROOT/'health_ax'),str(r['pid']),'press','重试读取'],check=True)
time.sleep(.4)
assert before==snap()
assert identity(r['pid']);os.kill(r['pid'],signal.SIGTERM);time.sleep(.3)
assert before==snap()
(E/'synthetic-launch-first.json').write_text(json.dumps(r,indent=2))
with (ROOT/'synthetic-restart-status.json').open('xb') as out:
 p=subprocess.Popen([r['binary']],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':str(ROOT/'tmp')})
for _ in range(100):
 time.sleep(.1)
 if (ROOT/'synthetic-restart-status.json').stat().st_size:break
status=json.loads((ROOT/'synthetic-restart-status.json').read_text());assert status==dict(status='readonly_view_started',mode='synthetic')
r['pid']=p.pid;r['startup']=status;(E/'synthetic-launch.json').write_text(json.dumps(r,indent=2));time.sleep(.7)
assert before==snap()
(E/'lifecycle.json').write_text(json.dumps(dict(status='pass',before=before,after=snap(),restart_pid=p.pid,busy_error_recovered=True),indent=2))
print(json.dumps(dict(status='lifecycle_pass',restart_pid=p.pid)))
