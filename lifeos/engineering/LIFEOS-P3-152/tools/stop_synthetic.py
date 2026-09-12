import json,hashlib,subprocess,os,signal,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
r=json.loads((E/'evidence/synthetic-launch.json').read_text());expected=ROOT/'LifeOS P3-152 Synthetic.app/Contents/MacOS/lifeos-p3-152'
assert r['mode']=='synthetic' and r['binary']==str(expected)
assert hashlib.sha256(expected.read_bytes()).hexdigest()==r['binary_sha256']
assert subprocess.check_output(['/bin/ps','-p',str(r['pid']),'-o','comm='],text=True).strip()==str(expected)
os.kill(r['pid'],signal.SIGTERM)
for _ in range(100):
 if subprocess.run(['/bin/ps','-p',str(r['pid']),'-o','comm='],capture_output=True).returncode!=0:break
 time.sleep(.05)
else:raise RuntimeError('synthetic did not stop')
print(json.dumps({'status':'synthetic_stopped','pid':r['pid']}))
