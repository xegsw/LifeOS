#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'FINAL_MANIFEST.json').read_text(encoding='utf-8'))
exclude={'FINAL_MANIFEST.json','verify_closure3_readonly.py','verifier-result.json'}
actual=sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name not in exclude)
expected=sorted(x['path'] for x in manifest['assets'])
errors=[]
if actual!=expected: errors.append('asset_set_mismatch')
for item in manifest['assets']:
 p=root/item['path']; h=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
 if h!=item['sha256'] or (p.is_file() and p.stat().st_size!=item['bytes']): errors.append('hash_or_size_mismatch:'+item['path'])
print(json.dumps({'overall':'PASS' if not errors else 'NOT_PASS','errors':errors,'read_only':True,'asset_count':len(expected)},ensure_ascii=False))
sys.exit(0 if not errors else 1)
