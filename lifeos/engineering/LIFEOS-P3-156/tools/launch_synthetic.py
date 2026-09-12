from pathlib import Path
import json,hashlib,subprocess,os,select,time
b=Path(__file__).resolve().parents[1];v=json.loads((b/'evidence/synthetic-bundle-final.json').read_text());assert v['mode']=='synthetic'
assert hashlib.sha256(Path(v['binary']).read_bytes()).hexdigest()==v['binarySha256']
claim=b/'evidence/synthetic-launch-final-claim.json'
with claim.open('x') as f:json.dump({'binary':v['binary'],'binarySha256':v['binarySha256'],'singleAttempt':True},f)
p=subprocess.Popen([v['binary']],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,env=dict(os.environ,TMPDIR='/private/tmp/lifeos-p3-156-next-action-v1/tmp'))
ready,_,_=select.select([p.stdout],[],[],20);receipt=json.loads(p.stdout.readline()) if ready else {'status':'startup_timeout'}
out={'pid':p.pid,'startup':receipt,'running':p.poll() is None,'binary':v['binary'],'binarySha256':v['binarySha256']};(b/'evidence/synthetic-launch-final.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert receipt=={'status':'synthetic_conversation_started'}
