"""Read-only integrity verification. Never implies acceptance."""
from pathlib import Path
import json,hashlib,sys
base=Path(__file__).resolve().parents[2];manifest=json.loads((base/'FINAL_MANIFEST.json').read_text());errors=[]
for row in manifest['files']:
 p=base/row['path']
 if p.is_symlink() or not p.is_file():errors.append(row['path']);continue
 data=p.read_bytes()
 if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:errors.append(row['path'])
report=base.parents[1]/'deliverables/LIFEOS-P3-147_obsidian_readonly_source_and_conversation_memory_integration.md'
if hashlib.sha256(report.read_bytes()).hexdigest()!=manifest['report_sha256']:errors.append('report')
print(json.dumps({'integrity_only':not errors,'status':'Partial; not Engineering Pass','files':len(manifest['files']),'errors':errors}))
sys.exit(bool(errors))
