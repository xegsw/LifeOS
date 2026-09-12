#!/usr/bin/env python3
"""Recreate only missing inherited source from the exact approved Git blobs."""
from pathlib import Path
import json,hashlib,subprocess
r=Path(__file__).resolve().parents[1];identity=json.loads((r/'inputs/baseline_identity.json').read_text());commit='46829c74eeb83c270a3258949c5d27db5bdea296'
for rel,sha in identity['sourceFiles'].items():
 assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
 target=r/'candidate'/rel;assert not target.is_symlink()
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==sha;continue
 blob=subprocess.check_output(['git','show',commit+':lifeos/engineering/LIFEOS-P3-159/baseline/candidate/'+rel],cwd=r);assert hashlib.sha256(blob).hexdigest()==sha
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
print('182 baseline files verified; no existing mismatch overwritten')
