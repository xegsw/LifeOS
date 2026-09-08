"""Read-only package integrity and evidence linkage; never PM or independent approval."""
from pathlib import Path
import hashlib,json,struct,sys
BASE=Path(__file__).resolve().parents[2]
def verify(m):
 errors=[];seen=set()
 excluded={'FINAL_MANIFEST.json','evidence/release-verification.json','evidence/manifest-mutations.json'}
 inventory={str(p.relative_to(BASE)) for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}-excluded
 if set(r['path'] for r in m['files'])!=inventory:errors.append('coverage')
 digest=hashlib.sha256(json.dumps([[r['path'],r['sha256']] for r in m['files'] if r['path'].startswith('candidate/')],separators=(',',':')).encode()).hexdigest()
 if digest!=m['candidate_sha256']:errors.append('candidate_identity')
 if set(m['test_evidence'])!={'rust','parser','web','inherited','public_api'}:errors.append('test_groups')
 if len(m['native_evidence'])<3 or {r['width'] for r in m['native_evidence']}!={700,1280}:errors.append('native_coverage')
 if m['gate_status']!={'independent_security':'pending','real_user_gate':'pending','pm_final':'pending'}:errors.append('gate_overclaim')
 for row in m['files']:
  rel=Path(row['path']);p=BASE/rel
  if rel.is_absolute() or '..' in rel.parts or str(rel) in seen or str(rel)=='FINAL_MANIFEST.json':errors.append('manifest_path');continue
  seen.add(str(rel))
  if p.is_symlink() or not p.is_file():errors.append('missing_file');continue
  b=p.read_bytes()
  if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:errors.append('file_integrity')
 report=BASE.parents[1]/'deliverables/LIFEOS-P3-147_obsidian_readonly_source_and_conversation_memory_integration.md'
 if hashlib.sha256(report.read_bytes()).hexdigest()!=m['report_sha256']:errors.append('report_integrity')
 for group,row in m['test_evidence'].items():
  result=json.loads((BASE/row['results']).read_text())
  if not any(s['name']==group and s['exit_code']==0 for s in result['steps']):errors.append('test_failed')
  log=(BASE/row['log']).read_text()
  import re
  pattern=r'test result: ok\. (\d+) passed' if group=='rust' else r'Ran (\d+) test' if group in ['parser','public_api'] else r'(?:ℹ tests|# tests) (\d+)'
  found=re.search(pattern,log)
  if not found or int(found.group(1))!=row['count']:errors.append('test_count')
 if sum(r['count'] for r in m['test_evidence'].values())!=71:errors.append('test_total')
 for row in m['native_evidence']:
  evidence=json.loads((BASE/row['evidence']).read_text());launch=json.loads((BASE/row['launch']).read_text())
  if evidence['pid']!=launch['pid'] or launch['binary_sha256']!=m['binary_sha256'] or launch['source_binary_sha256']!=m['binary_sha256']:errors.append('native_identity')
  if evidence['window']['title']!='LifeOS · P3-147 · 合成离线' or not any(n['role'] in ['AXWebArea','AXWebView'] for n in evidence['window']['nodes']):errors.append('native_window')
  if row.get('revoked_restart'):
   objects=evidence['synthetic_objects']
   if any(r.get('sourceFile') and r['status']=='active' for r in objects['records']) or any(s['id']=='directory' and s['authorized'] for s in objects['sources']):errors.append('revoked_restart')
  png=(BASE/row['image']).read_bytes();w,h=struct.unpack('>II',png[16:24]);g=evidence['window']['geometry']
  if w/g['width']!=h/g['height'] or w/g['width'] not in [1,2] or g['width']!=row['width']:errors.append('native_geometry')
  if hashlib.sha256(png).hexdigest()!=evidence['image_sha256']:errors.append('native_image')
  for name,digest in launch['source_files'].items():
   if name.startswith(('src/','application/','ui/','capabilities/')) or name in ['Cargo.toml','Cargo.lock','tauri.conf.json','build.rs']:
    if hashlib.sha256((BASE/'candidate'/name).read_bytes()).hexdigest()!=digest:errors.append('runtime_source_drift')
 return errors
if __name__=='__main__':
 m=json.loads((BASE/'FINAL_MANIFEST.json').read_text());errors=verify(m)
 print(json.dumps({'integrity_and_linkage':not errors,'errors':errors,'files':len(m['files']),'tests':71,'independent_security':'pending','real_user_gate':'pending'}))
 sys.exit(bool(errors))
