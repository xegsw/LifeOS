"""One real invocation, allowlisted scalar receipt only. Never reads the source or DB."""
from pathlib import Path
import subprocess,json,datetime,hashlib,sys
s=Path(__file__).resolve().parents[1]
binary=Path('/private/tmp/lifeos-p3-149-health-source-v1/S3/target/debug/lifeos-p3-149')
assert len(sys.argv)==1
started={'stage':'real_execution_started','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
with (s/'evidence/real-execution-started.json').open('x') as f:json.dump(started,f,indent=2)
try:
 p=subprocess.run([str(binary),'--controlled-health-import'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env={},timeout=150)
 if len(p.stdout)>4096:raise ValueError()
 v=json.loads(p.stdout)
 allowed={'status','code','supported','inserted','duplicates','unsupported','attachments_unprocessed','failed','target_created','retained','network','model'}
 if set(v)-allowed:raise ValueError()
 for k,x in v.items():
  if k=='status':assert x in ['completed','duplicate','failed']
  elif k=='code':assert type(x)==str and len(x)<=64 and all(c in 'abcdefghijklmnopqrstuvwxyz_' for c in x)
  elif k in ['target_created','retained','network','model']:assert x is None or type(x)==bool
  else:assert x is None or (type(x)==int and 0<=x<=2000000)
 assert v.get('network') is False and v.get('model') is False
 assert (p.returncode==0)==(v['status']!='failed')
except Exception:
 v={'status':'failed','code':'receipt_unavailable','network':False,'model':False,'retained':True}
with (s/'evidence/real-receipt.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
