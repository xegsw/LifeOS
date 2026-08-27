#!/usr/bin/env python3
"""Create a non-self-referential Closure-3 Manifest and read-only verifier."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path('/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-134/evidence/closure-3')
MANIFEST = ROOT / 'FINAL_MANIFEST.json'
VERIFIER = ROOT / 'verify_closure3_readonly.py'
EXCLUDED = {MANIFEST.name, VERIFIER.name, 'verifier-result.json'}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def assets():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name not in EXCLUDED)

def main():
    rows = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p), 'bytes': p.stat().st_size} for p in assets()]
    MANIFEST.write_text(json.dumps({'schema':'LIFEOS-P3-134-closure3-manifest-v1','self_referential':False,'scope':'all stable Closure-3 assets except manifest and verifier','assets':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    verifier = '''#!/usr/bin/env python3
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
'''
    VERIFIER.write_text(verifier,encoding='utf-8')

if __name__ == '__main__': main()
