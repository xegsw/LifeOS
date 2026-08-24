#!/usr/bin/env python3
import hashlib, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
EV=ROOT/"lifeos/engineering/LIFEOS-P3-106/evidence/resume-1"
manifest=EV/"MANIFEST.md"
rows=re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|$",manifest.read_text(),re.M)
bad=[]
for rel,want,size in rows:
    p=ROOT/rel
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=want or p.stat().st_size!=int(size): bad.append(rel)
expected=[]
eng=ROOT/"lifeos/engineering/LIFEOS-P3-106"
for p in eng.rglob("*"):
    if p.is_file() and "target" not in p.parts and p!=manifest: expected.append(str(p.relative_to(ROOT)))
listed=[x[0] for x in rows]
missing=sorted(set(expected)-set(listed)); extra=sorted(set(listed)-set(expected))
ok=not bad and not missing and not extra and str(manifest.relative_to(ROOT)) not in listed
print({"status":"PASS" if ok else "FAIL","entries":len(rows),"hash_or_size_bad":bad,"missing":missing,"extra":extra,"self_reference":str(manifest.relative_to(ROOT)) in listed})
raise SystemExit(0 if ok else 1)
