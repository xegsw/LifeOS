"""One real invocation, allowlisted scalar receipt only. Never reads the source or DB."""
from pathlib import Path
import subprocess,json,datetime,hashlib,sys
s=Path(__file__).resolve().parents[1]
binary=Path('/private/tmp/lifeos-p3-149-health-source-v1/S3/closure-3/target/debug/lifeos-p3-149')
assert len(sys.argv)==2 and sys.argv[1] in ['1','2','3']
attempt=int(sys.argv[1])
for previous in range(1,attempt):
 assert json.loads((s/'evidence'/('real-receipt-'+str(previous)+'.json')).read_text())['status']=='failed'
started={'stage':'closure3_real_attempt_started','attempt':attempt,'authorization':'P3-149-S3-closure-3-user-complete','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
with (s/'evidence'/('real-execution-started-'+str(attempt)+'.json')).open('x') as f:json.dump(started,f,indent=2)
try:
 p=subprocess.run([str(binary),'--controlled-health-import'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env={},timeout=330)
 if len(p.stdout)>4096:raise ValueError()
 v=json.loads(p.stdout)
 allowed={'status','code','skipped','unprojected','supported','inserted','duplicates','unsupported','attachments_unprocessed','failed','target_verified','retained','network','model'}
 if set(v)-allowed:raise ValueError()
 for k,x in v.items():
  if k=='status':assert x in ['completed','successful_with_skips','duplicate','failed']
  elif k=='code':assert type(x)==str and len(x)<=64 and all(c in 'abcdefghijklmnopqrstuvwxyz_' for c in x)
  elif k in ['target_verified','retained','network','model']:assert x is None or type(x)==bool
  else:assert x is None or (type(x)==int and 0<=x<=2000000)
 assert v.get('network') is False and v.get('model') is False
 assert (p.returncode==0)==(v['status']!='failed')
except Exception:
 v={'status':'failed','code':'receipt_unavailable','network':False,'model':False,'retained':True}
with (s/'evidence'/('real-receipt-'+str(attempt)+'.json')).open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
