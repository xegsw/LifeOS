#!/usr/bin/env python3
"""Closure-1 read-only integrity and regression-evidence verification."""
from pathlib import Path
import json,hashlib,re
b=Path(__file__).resolve().parents[1];parent=b.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'FINAL_MANIFEST.json').read_text())
for rel,digest in m['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 assert not (b/p).is_symlink() and sha(b/p)==digest,rel
snapshot=json.loads((b/'evidence/parent-snapshot.json').read_text());assert sha(parent/'FINAL_MANIFEST.json')==snapshot['manifestSha256']
for rel,digest in snapshot['files'].items():
 p=Path(rel);assert not p.is_absolute() and '..' not in p.parts
 assert sha(parent/p)==digest,'parent changed: '+rel
repo=parent.parents[2]
assert sha(repo/'lifeos/deliverables/LIFEOS-P3-153_continuous_understanding_and_useful_clarification.md')==snapshot['reportSha256']
assert sha(repo/'lifeos/deliverables/LIFEOS-P3-153_closure_1_clarification_freshness.md')==m['reportSha256']
for name,count in [('rust-host',35),('rust-disclosure',23),('source-expiry-final',1)]:assert f'{count} passed; 0 failed' in (b/f'evidence/{name}.log').read_text()
for name,count in [('integration',14),('continuity',8),('freshness',6)]:
 v=json.loads((b/f'evidence/{name}.json').read_text());assert v['passed']==v['total']==count
 if name=='freshness':assert v['networkCalls']==0 and len(set(v['restart']['pids']))==2
v=json.loads((b/'evidence/reuse.json').read_text());assert v['affectedTotal']==86 and v['unchangedUiRendererAndCss']
print(json.dumps({'status':'Closure-1 self-check passed','closureFiles':len(m['files']),'parentFilesPreserved':len(snapshot['files']),'affectedTests':86,'additionalTargetedRerun':1,'guiRerun':False,'independentReview':'paused','realAccess':False},indent=2))
