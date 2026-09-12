from pathlib import Path
import os,json,subprocess
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-158-main-chain-v1');os.umask(0o077);results=[]
for name,mode,features,needle in [('wrong-mode','real','','build mode rejected'),('online-driver','online-synthetic','online-synthetic,synthetic-driver','network driver forbidden'),('real-driver','real','controlled-real,synthetic-driver','network driver forbidden'),('mixed-online-real','real','controlled-real,online-synthetic','mixed runtime modes forbidden')]:
 env=dict(os.environ,LIFEOS_P3_158_MODE=mode,CARGO_TARGET_DIR=str(root/'build/guards'),TMPDIR=str(root/'offline/tmp'))
 with (b/'evidence'/('guard-'+name+'.log')).open('w') as f:r=subprocess.run(['/Users/xxe/.cargo/bin/cargo','check','--locked','--offline','--features',features,'--manifest-path',str(b/'candidate/Cargo.toml')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 log=(b/'evidence'/('guard-'+name+'.log')).read_text();v=dict(name=name,exitCode=r.returncode,passed=r.returncode!=0 and needle in log);results.append(v);print(v,flush=True)
(b/'evidence/build-mode-guards.json').write_text(json.dumps(results,indent=2)+'\n');assert all(x['passed'] for x in results)
