#!/usr/bin/env python3
"""Package self-check; not independent review, PM acceptance, or real capability proof."""
from pathlib import Path
import json,hashlib,re
base=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((base/'FINAL_MANIFEST.json').read_text())
for rel,digest in m['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 p=base/p;assert not p.is_symlink() and p.is_file() and sha(p)==digest, rel
report=base.parents[1]/'deliverables/LIFEOS-P3-153_continuous_understanding_and_useful_clarification.md'
assert sha(report)==m['reportSha256']
baseline=Path('/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/settings-baseline-restoration')
old=json.loads((base/'evidence/inherited-candidate.json').read_text())
assert old['baseline']==str(baseline)
assert sha(baseline/'FINAL_MANIFEST.json')==old['manifest_sha256']
for rel,digest in old['files'].items():
 p=Path(rel);assert p.parts[0]=='candidate' and '..' not in p.parts and not p.is_absolute()
 assert sha(baseline/p)==digest, 'historical input changed'
assert '88 passed; 0 failed' in (base/'evidence/rust.log').read_text()
for name,count in [('ui',25),('clarification-ui',5)]:
 log=(base/f'evidence/{name}.log').read_text();assert re.search(r'pass\s+'+str(count)+r'\b',log) and re.search(r'fail\s+0\b',log)
for name,count in [('integration',14),('combined',11),('continuity',8)]:
 v=json.loads((base/f'evidence/{name}.json').read_text());assert v['passed']==v['total']==count
 if name=='continuity':assert v['networkCalls']==0 and len(set(v['restartEvidence']['pids']))==3
assert json.loads((base/'evidence/gui-results.json').read_text())['passed']
print(json.dumps({'packageFiles':len(m['files']),'baselineFiles':len(old['files']),'tests':151,'status':'self-check passed','independentReview':'paused','realModeEnabled':False},indent=2))
