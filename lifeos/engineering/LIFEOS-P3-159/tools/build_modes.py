from pathlib import Path
import os,subprocess,json,datetime,hashlib
b=Path(__file__).resolve().parents[1];stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S');out=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()}
for mode,feature in [('online-synthetic','online-synthetic'),('real','controlled-real')]:
 log=b/'evidence'/f'A-mode-build-{stamp}-{mode}.log';target=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1/build')/mode
 env=dict(os.environ,LIFEOS_P3_159_MODE=mode,CARGO_TARGET_DIR=str(target),TMPDIR='/private/tmp/lifeos-p3-159-unified-proactive-v1/offline/tmp',CARGO_NET_OFFLINE='true')
 with log.open('w') as f:r=subprocess.run(['/Users/xxe/.cargo/bin/cargo','build','--locked','--offline','--bin','lifeos-p3-152','--features',feature,'--manifest-path',str(b/'candidate/Cargo.toml')],env=env,stdout=f,stderr=subprocess.STDOUT)
 binary=target/'debug/lifeos-p3-152';out.append({'mode':mode,'exitCode':r.returncode,'log':str(log),'binary':str(binary),'binarySha256':sha(binary) if r.returncode==0 else None,'execution':'build only; not launched; no credential/network','sourceFiles':before});print(mode,r.returncode,flush=True)
assert before=={str(p.relative_to(b/'candidate')):sha(p) for p in sorted((b/'candidate').rglob('*')) if p.is_file()}
(b/'evidence'/f'A-mode-build-{stamp}.json').write_text(json.dumps(out,indent=2)+'\n')
raise SystemExit(any(x['exitCode'] for x in out))
