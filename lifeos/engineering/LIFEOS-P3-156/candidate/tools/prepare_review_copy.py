"""Run ONLY in a separately authorized independent session, after its precontact seal.
Copies immutable Git blobs, never engineering runtime/caches/DB/Evidence.
"""
import re,sys,json,hashlib,subprocess,os
from pathlib import Path,PurePosixPath
from task_root import ROOT,PROFILE,verify
if PROFILE!='independent-review':raise SystemExit('review_profile_required')
if len(sys.argv)!=2 or not re.fullmatch('[0-9a-f]{40}',sys.argv[1]):raise SystemExit('fixed_commit_required')
commit=sys.argv[1]
repo=subprocess.check_output(['git','-C',str(Path(__file__).resolve().parent),'rev-parse','--show-toplevel']).decode().strip()
prefix='lifeos/engineering/LIFEOS-P3-147/'
def blob(path):return subprocess.check_output(['git','-C',repo,'show',commit+':'+prefix+path])
manifest_bytes=blob('FINAL_MANIFEST.json');manifest=json.loads(manifest_bytes)
rows=[r for r in manifest['files'] if r['path'].startswith('candidate/')]
assert rows and len({r['path'] for r in rows})==len(rows)
# Validate all source blobs in memory before creating a review-owned copy.
sources=[]
for row in rows:
 path=PurePosixPath(row['path']);assert not path.is_absolute() and '..' not in path.parts
 data=blob(str(path));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
 sources.append((path,data))
verify();work=ROOT/'work'
if os.path.lexists(work):raise SystemExit('review_copy_already_exists; preserve and resume using its lineage')
work.mkdir(mode=0o700)
for relative,data in sources:
 out=work/relative;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f:f.write(data)
(work/'evidence').mkdir(mode=0o700)
(work/'source-lineage.json').write_text(json.dumps({'fixed_commit':commit,'manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest(),'candidate_sha256':manifest['candidate_sha256'],'files':rows,'no_engineering_runtime_reuse':True},indent=2))
print(str(work/'candidate'))
