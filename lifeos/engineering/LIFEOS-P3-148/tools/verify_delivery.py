"""Read-only check of the P3-148 engineering delivery manifest, not a safety gate."""
from pathlib import Path,PurePosixPath
import hashlib,json
BASE=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((BASE/'FINAL_MANIFEST.json').read_text())
assert m['task']=='LIFEOS-P3-148' and m['scope']=='synthetic_engineering_only'
for f in m['files']:
 rel=PurePosixPath(f['path']);assert not rel.is_absolute() and '..' not in rel.parts
 p=BASE/str(rel);assert p.is_file() and not p.is_symlink()
 assert digest(p)==f['sha256'],str(rel)
report=BASE.parents[1]/'deliverables/LIFEOS-P3-148_source_backed_ai_conversation.md'
assert digest(report)==m['report_sha256']
print(json.dumps({'verified':True,'files':len(m['files']),'candidate_sha256':m['candidate_sha256'],'scope':m['scope'],'independent_pass':False}))
