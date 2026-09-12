from pathlib import Path
import subprocess,shutil,uuid,json,os
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-154-real-continuity-v1');assert json.loads((root/'.owner.json').read_text())['task']=='P3-154';os.umask(0o077)
results=[]
for name,old,new in [('old-draft-error','serial === this.serial && d.turnId === this.draft.turnId && !this.busy','true'),('saved-refresh-reprepare',"this.phase = 'refresh-failed'","this.phase = 'failed'")]:
 d=root/'mutations'/str(uuid.uuid4());d.mkdir(parents=True);shutil.copytree(b/'candidate',d/'candidate');shutil.copytree(b/'tests',d/'tests');p=d/'candidate/ui/controlled_conversation.js';s=p.read_text();assert old in s;p.write_text(s.replace(old,new));run=subprocess.run(['/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node','--test','--test-reporter=tap',str(d/'tests/flow_races.mjs')],capture_output=True,text=True);(d/'result.log').write_text(run.stdout+run.stderr);results.append({'name':name,'killed':run.returncode!=0 and 'not ok' in run.stdout,'exitCode':run.returncode,'output':str(d)})
assert all(v['killed'] for v in results);print(json.dumps(results))
