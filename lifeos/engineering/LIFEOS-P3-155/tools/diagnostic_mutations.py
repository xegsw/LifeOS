from pathlib import Path
import os,subprocess,shutil,json,uuid
b=Path(__file__).resolve().parents[1];r=Path('/private/tmp/lifeos-p3-155-source-update-v1');assert json.loads((r/'.owner.json').read_text())['task']=='P3-155';os.umask(0o077)
out=r/'mutations'/('c1-'+str(uuid.uuid4()));out.mkdir();results=[]
for name in ['hide-code','raw-error-leak']:
 case=out/name;case.mkdir();shutil.copytree(b/'candidate',case/'candidate');shutil.copytree(b/'tests',case/'tests')
 p=case/'candidate/ui/health_errors.js';s=p.read_text();needle='export function errorText(e) {';assert needle in s
 s=s.replace(needle,needle+(' return "操作未完成，草稿已保留。";' if name=='hide-code' else ' if(e.message)return e.message;'),1);p.write_text(s)
 done=subprocess.run(['/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node','--test','--test-reporter=tap',str(case/'tests/error_diagnostics.mjs')],capture_output=True,text=True);(out/(name+'.log')).write_text(done.stdout+done.stderr);killed=done.returncode!=0 and 'not ok' in done.stdout;assert killed;results.append({'mutation':name,'killed':killed})
(b/'evidence/diagnostic-mutations.json').write_text(json.dumps({'results':results,'output':str(out)},indent=2)+'\n');print(json.dumps(results))
