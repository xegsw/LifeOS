# coding: utf-8
import hashlib,json
from pathlib import Path
ENGINE=Path(__file__).resolve().parents[1];BASE=ENGINE.parent
results=[]
for item in json.loads((ENGINE/'evidence/input-identity.json').read_text()):
 root=BASE/item['input'];manifest=root/'FINAL_MANIFEST.json'
 assert hashlib.sha256(manifest.read_bytes()).hexdigest()==item['manifest_sha256']
 entries=json.loads(manifest.read_text())['files']
 if isinstance(entries,list):entries={e['path']:e['sha256'] for e in entries}
 selected={p:h for p,h in entries.items() if p.startswith(('candidate/','design/','deliverables/'))}
 for name,digest in selected.items():
  path=root/name;assert not path.is_symlink();assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
 results.append(dict(input=item['input'],verified=len(selected),status='unchanged'))
print(json.dumps(results,indent=2))
