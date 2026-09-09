"""Read-only task package checks. Does not contact any data root."""
from pathlib import Path
import hashlib,json,re,subprocess
BASE=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 for name,wanted in json.loads((BASE/'contract-inputs/sha256.json').read_text()).items():
  assert digest(BASE/'contract-inputs'/name)==wanted,name
  if name[0].isdigit():assert digest(BASE/'design'/name)==wanted,name
 e=json.loads((BASE/'contract-inputs/E01-sha256.json').read_text());assert digest(BASE/'contract-inputs/E01-task-card.md')==e['E01-task-card.md']
 e2=json.loads((BASE/'contract-inputs/E02-sha256.json').read_text());assert digest(BASE/'contract-inputs/E02-task-card.md')==e2['sha256']
 e3=json.loads((BASE/'contract-inputs/E03-sha256.json').read_text());assert digest(BASE/'contract-inputs/E03-task-card.md')==e3['sha256']
 src=(BASE/'candidate/src/main.rs').read_text();registered=re.search(r'generate_handler!\[(.*?)\]',src,re.S).group(1);commands=re.findall(r'\b[a-z][a-z_]+\b',registered)
 expected=re.findall(r'^\| \d+ \| (\w+) \|',(BASE/'contract-inputs/01-ipc-contract.md').read_text(),re.M)+['send_source_ai_request']
 assert len(commands)==26 and set(commands)==set(expected)
 ui=(BASE/'candidate/application/source_ui.ts').read_text()
 assert len(re.findall("'[^']+'",re.search(r'const cloud=\[(.*?)\]',ui).group(1)))==8
 assert len(re.findall("'[^']+'",re.search(r'const local=\[(.*?)\]',ui).group(1)))==4
 profiles=json.loads((BASE/'candidate/root_profiles.json').read_text());assert profiles.keys()=={'engineering','independent-review','source-pilot-1'}
 assert profiles['source-pilot-1']['markerFile']=='.lifeos-p3-147-owner.json'
 assert 'source' not in profiles['source-pilot-1']
 assert (BASE/'candidate/ui/index.html').read_text().count('source_ui.js')==1
 return {'status':'pass','checks':['five_design_seals','E01_seal','E02_seal','E03_seal','26_registered_commands','8_cloud_4_local_catalog','fixed_profiles_no_scan_root','active_application_entry'],'fixed_parent_commit':'5c26431ca43d68b77ab3d91a715dd59444a62e2e'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
