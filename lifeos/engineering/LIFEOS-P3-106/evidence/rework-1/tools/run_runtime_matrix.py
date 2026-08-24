#!/usr/bin/env python3
import hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'evidence/rework-1'; CARGO='/Users/xxe/.cargo/bin/cargo'; PAT=re.compile(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+")
TESTS=[('RUNTIME-LIFECYCLE','runtime::tests::lifecycle_saved_repeat_conflict_restart'),('RUNTIME-ATOMIC-FAILURE','runtime::tests::injected_failure_preserves_database_and_sentinel'),('RUNTIME-PATH-ARGUMENTS','runtime::tests::path_and_argument_boundaries_fail_closed'),('RUNTIME-LINK-HARDLINK','runtime::tests::symlink_and_hardlink_boundaries_fail_closed'),('RUNTIME-DANGLING-4','runtime::tests::dangling_database_and_sidecar_links_fail_closed'),('RUNTIME-TAMPER-PROCESS','runtime::tests::tampered_content_and_sidecar_fail_closed'),('RUNTIME-CAPABILITIES','runtime::tests::runtime_status_closes_direct_capabilities')]
def res(): return sorted(str(p) for p in Path('/private/tmp').iterdir() if PAT.fullmatch(p.name))
rows=[]; env=os.environ.copy(); env['CARGO_NET_OFFLINE']='true'
for rid,test in TESTS:
 b=res(); cmd=[CARGO,'test','--locked',test,'--','--exact','--nocapture']; c=subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); a=res(); log=OUT/f'{rid.lower()}.log'; log.write_text(c.stdout); good=c.returncode==0 and not b and not a and '1 passed' in c.stdout
 rows.append({'id':rid,'test':test,'command':cmd,'returncode':c.returncode,'unit_paths_before':b,'unit_paths_after':a,'log':str(log.relative_to(ROOT)),'sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'status':'PASS' if good else 'FAIL'})
d={'task':'LIFEOS-P3-106','execution':'rework-1','rows':rows,'summary':{'total':len(rows),'passed':sum(x['status']=='PASS' for x in rows),'failed':sum(x['status']!='PASS' for x in rows)}}; (OUT/'runtime_process_matrix.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(d['summary'])); raise SystemExit(0 if d['summary']['failed']==0 else 1)
