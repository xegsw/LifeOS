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
 if set(m['test_evidence'])!={'rust','parser','web','inherited','public_api','root_profiles','target_boundaries'}:errors.append('test_groups')
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
  pattern=r'test result: ok\. (\d+) passed' if group=='rust' else r'Ran (\d+) test' if group in ['parser','public_api','root_profiles','target_boundaries'] else r'(?:ℹ tests|# tests) (\d+)'
  found=re.search(pattern,log)
  if not found or int(found.group(1))!=row['count']:errors.append('test_count')
 if sum(r['count'] for r in m['test_evidence'].values())!=94:errors.append('test_total')
 for row in m['native_evidence']:
  evidence=json.loads((BASE/row['evidence']).read_text());launch=json.loads((BASE/row['launch']).read_text())
  if launch.get('compiled_profile')!='engineering':errors.append('native_profile')
  if evidence['pid']!=launch['pid'] or launch['binary_sha256']!=m['binary_sha256'] or launch['source_binary_sha256']!=m['binary_sha256']:errors.append('native_identity')
  if evidence['window']['title']!='LifeOS · P3-147 · 合成离线' or not any(n['role'] in ['AXWebArea','AXWebView'] for n in evidence['window']['nodes']):errors.append('native_window')
  if row.get('revoked_restart'):
   objects=evidence['synthetic_objects']
   if any(r.get('sourceFile') and r['status']=='active' for r in objects['records']) or any(s['id']=='directory' and s['authorized'] for s in objects['sources']):errors.append('revoked_restart')
  png=(BASE/row['image']).read_bytes();w,h=struct.unpack('>II',png[16:24]);g=evidence['window']['geometry']
  if w/g['width']!=h/g['height'] or w/g['width'] not in [1,2] or g['width']!=row['width']:errors.append('native_geometry')
  if hashlib.sha256(png).hexdigest()!=evidence['image_sha256']:errors.append('native_image')
  for name,digest in launch['source_files'].items():
   if name.startswith(('src/','application/','ui/','capabilities/')) or name in ['Cargo.toml','Cargo.lock','tauri.conf.json','build.rs','root_profile.rs','root_profiles.json']:
    if hashlib.sha256((BASE/'candidate'/name).read_bytes()).hexdigest()!=digest:errors.append('runtime_source_drift')
 build=json.loads((BASE/m['root_build_evidence']).read_text())
 if build.get('review_root_contact') is not False or len(build['steps'])!=4:errors.append('root_build_coverage')
 for row in build['steps']:
  log=(BASE/Path(m['root_build_evidence']).parent/(row['name']+'.log')).read_text()
  if row['runtime_executed'] or row['cache_scope']!='engineering root only' or (row['exit_code']==0)!=row['expected_success'] or not row['pass']:errors.append('root_build_result')
  if not row['expected_success'] and 'profile' not in log:errors.append('root_build_reason')
 history=json.loads((BASE/'evidence/root-closure-history.json').read_text())
 for row in history['files']:
  if hashlib.sha256((BASE/'history/pre-root-closure'/row['path']).read_bytes()).hexdigest()!=row['sha256']:errors.append('history_integrity')
 if hashlib.sha256((BASE/'history/pre-root-closure/report.md').read_bytes()).hexdigest()!=history['report_sha256']:errors.append('history_report')
 current_build=json.loads((BASE/m['artifact_review_compile']).read_text())
 if current_build!={'exit_code':0,'profile':'independent-review','compile_only':True,'review_runtime_contact':False,'cache':'engineering root only'}:errors.append('artifact_compile')
 targets=json.loads((BASE/m['artifact_target_evidence']).read_text())
 if targets.get('review_runtime_contact') is not False or targets['binary_sha256']!=m['binary_sha256'] or len(targets['results'])!=10:errors.append('artifact_targets')
 for row in targets['results']:
  if not row['passed'] or not row['sentinel_unchanged'] or row['before']!=row['after'] or (row['status']=='fetched')!=row['case'].endswith('-control'):errors.append('artifact_target_semantics')
 repro=json.loads((BASE/m['review_repro_evidence']).read_text())
 if repro['binary_sha256']!=m['binary_sha256'] or len(repro['results'])!=2:errors.append('review_repro')
 for row in repro['results']:
  if not row['passed'] or row['before']!=row['after'] or not row['target_status'] or any((s['status']=='fetched')==row['attack'] for s in row['target_status']):errors.append('review_repro_semantics')
 import tarfile
 history_dir=BASE/'history/pre-artifact-closure'
 lineage=json.loads((history_dir/'lineage.json').read_text())
 if lineage['commit']!='640ebb6fe8d87398a05940b30f1263dad157dfa0' or len(lineage['files'])!=566:errors.append('artifact_history_lineage')
 with tarfile.open(history_dir/'snapshot.tar.gz','r:gz') as archive:
  members=archive.getmembers()
  if len(members)!=566 or {r.name for r in members}!={r['path'] for r in lineage['files']}:errors.append('artifact_history_coverage')
  for row in lineage['files']:
   member=archive.getmember(row['path'])
   if not member.isfile() or hashlib.sha256(archive.extractfile(member).read()).hexdigest()!=row['sha256']:errors.append('artifact_history_integrity')
  if archive.extractfile('FINAL_MANIFEST.json').read()!=(history_dir/'FINAL_MANIFEST.json').read_bytes():errors.append('artifact_history_manifest')
 runtime=json.loads((BASE/'evidence/artifact-closure-runtime.json').read_text())
 if not runtime['marker_verified'] or not runtime['writers_stopped'] or runtime['wal_count']!=0 or runtime['removed']:errors.append('runtime_retention')
 return errors
if __name__=='__main__':
 m=json.loads((BASE/'FINAL_MANIFEST.json').read_text());errors=verify(m)
 print(json.dumps({'integrity_and_linkage':not errors,'errors':errors,'files':len(m['files']),'tests':94,'review_reproduction_cases':2,'independent_security':'pending','real_user_gate':'pending'}))
 sys.exit(bool(errors))
