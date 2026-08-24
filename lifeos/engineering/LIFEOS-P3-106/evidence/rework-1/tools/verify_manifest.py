#!/usr/bin/env python3
import hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]; ENG=ROOT/"lifeos/engineering/LIFEOS-P3-106"; EV=ENG/"evidence/rework-1"; man=EV/"MANIFEST.md"
rows=re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|$",man.read_text(),re.M); bad=[]
for rel,want,size in rows:
 p=ROOT/rel
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=want or p.stat().st_size!=int(size): bad.append(rel)
expected=[str(p.relative_to(ROOT)) for p in ENG.rglob("*") if p.is_file() and "target" not in p.parts and p!=man]; listed=[x[0] for x in rows]
missing=sorted(set(expected)-set(listed)); extra=sorted(set(listed)-set(expected)); selfref=str(man.relative_to(ROOT)) in listed; ok=not bad and not missing and not extra and not selfref
print({"status":"PASS" if ok else "FAIL","entries":len(rows),"bad":bad,"missing":missing,"extra":extra,"self_reference":selfref}); raise SystemExit(0 if ok else 1)
