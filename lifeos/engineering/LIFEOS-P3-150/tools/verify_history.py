import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1];old=E.parent/'LIFEOS-P3-149';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={'': 'ec7ac1ce37fc740df97654bde6574e40a1762cb3950dc448a5caeef7b48658d7','S1':'63e2a206ac66893d2e7858af210e33506a7a06b9da4c4f0e82d5bd4bd4cd8953','S2':'84b81eca1a56044ff2c6475ac427cb3a9c3e686b22737823e1bc8015c5f67cb7','S3':'234fce5f5d9c7f423d84eba8792d7dd4ee3158a527a89477ce4678fd28ba0ad4','S3/closure-1':'a97ed571768cbdc688a95cca270169dc60394bc083e0f22684f719d154cc0c28','S3/closure-2':'c2fef6825e56def0035d9cf2e8fe7ee981468bdc9a1481da96100d17099a75f7','S3/closure-3':'974ded8442c396dc85438224c13cdfe7ffcfdd3cfb828a1dba702436533a2541'}
results={}
for sub,digest in expected.items():
 root=old/sub;p=root/'FINAL_MANIFEST.json';assert sha(p)==digest,(sub,'manifest_changed');data=json.loads(p.read_text());files=data['files'];assert isinstance(files,dict)
 for name,h in files.items():
  rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts
  f=root/rel;assert not f.is_symlink();assert sha(f)==h,(sub,name)
 results[sub or 'root']=dict(files=len(files),manifest_sha256=digest,status='unchanged')
for name in ['design116.css','settings142.css','conversation.css','health.css']:
 assert sha(E/'candidate/ui'/name)==sha(old/'S3/closure-3/candidate/ui'/name)
(E/'evidence/history-preservation.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
