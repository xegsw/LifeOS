"""Read-only ordinary entry package linkage. Does not run or replace security review."""
from pathlib import Path
import hashlib,json,struct,sys
BASE=Path(__file__).resolve().parents[2]
def sha(data):return hashlib.sha256(data).hexdigest()
def verify(m):
 errors=[]
 excluded={'FINAL_MANIFEST.json','evidence/entry-release-verification.json'}
 actual={str(p.relative_to(BASE)) for p in BASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}-excluded
 listed=[r['path'] for r in m['files']]
 if len(set(listed))!=len(listed) or set(listed)!=actual:errors.append('coverage')
 for r in m['files']:
  p=Path(r['path'])
  if p.is_absolute() or '..' in p.parts:errors.append('path');continue
  p=BASE/p
  if p.is_symlink() or not p.is_file():errors.append('file');continue
  data=p.read_bytes()
  if len(data)!=r['bytes'] or sha(data)!=r['sha256']:errors.append('hash')
 digest=sha(json.dumps([[r['path'],r['sha256']] for r in m['files'] if r['path'].startswith('candidate/')],separators=(',',':')).encode())
 if digest!=m['candidate_sha256']:errors.append('candidate_identity')
 report=BASE.parents[1]/'deliverables/LIFEOS-P3-147_obsidian_readonly_source_and_conversation_memory_integration.md'
 if sha(report.read_bytes())!=m['report_sha256']:errors.append('report')
 if m['gate_status']!={'independent_security':'user_directed_waiver_no_independent_pass','real_activation':'ready_waiting_user_click','pm_final':'pending'}:errors.append('gate_status')
 history=BASE/'history/pre-user-entry'
 for r in json.loads((history/'lineage.json').read_text())['files']:
  if sha((history/r['path']).read_bytes())!=r['sha256']:errors.append('history')
 previous=json.loads((history/'FINAL_MANIFEST.json').read_text())
 allowed={'candidate/application/ui.ts','candidate/ui/ui.js','candidate/tests/source_entry.mjs','candidate/tools/run_internal_checks.py','candidate/tools/verify_entry_release.py','candidate/tests/real_entry_ui.mjs','candidate/tools/package_source_pilot.py','candidate/root_profiles.json','candidate/root_profile.rs','candidate/build.rs','candidate/src/main.rs','candidate/src/runtime_root.rs','candidate/src/artifact_io.rs','candidate/src/source_api.rs','candidate/src/source_file.rs','candidate/src/source_worker.rs','candidate/src/repository.rs'}
 for r in previous['files']:
  if r['path'].startswith('candidate/') and r['path'] not in allowed and sha((BASE/r['path']).read_bytes())!=r['sha256']:errors.append('unrelated_candidate_change')
 flow=json.loads((BASE/m['ordinary_flow']['log']).read_text())
 result=json.loads((BASE/m['ordinary_flow']['results']).read_text())
 if flow['count']!=6 or len(flow['results'])!=6 or flow['external_target_calls']!=0 or not any(r['name']=='entry_flow' and r['exit_code']==0 for r in result['steps']):errors.append('ordinary_flow')
 build=json.loads((BASE/m['build_evidence']).read_text())
 if {r['name'] for r in build['steps']}!={'format','build','real_entry_ui','entry_flow'} or any(r['exit_code'] for r in build['steps']):errors.append('build')
 ui=json.loads((BASE/m['ui_build_evidence']).read_text())
 if not any(r['name']=='ui_build' and r['exit_code']==0 for r in ui['steps']):errors.append('ui_build')
 if len(m['native_evidence'])!=3 or {r['width'] for r in m['native_evidence']}!={700,1280}:errors.append('native_coverage')
 for r in m['native_evidence']:
  e=json.loads((BASE/r['evidence']).read_text());launch=json.loads((BASE/r['launch']).read_text())
  if e['pid']!=launch['pid'] or launch['compiled_profile']!='engineering' or launch['binary_sha256']!=m['binary_sha256']:errors.append('native_identity')
  if e['window']['title']!='LifeOS · P3-147 · 合成离线' or not any(n['role'] in ['AXWebArea','AXWebView'] for n in e['window']['nodes']):errors.append('native_window')
  png=(BASE/r['image']).read_bytes();w,h=struct.unpack('>II',png[16:24]);g=e['window']['geometry']
  if sha(png)!=e['image_sha256'] or g['width']!=r['width'] or w/g['width']!=h/g['height'] or w/g['width'] not in [1,2]:errors.append('native_geometry')
  for name,digest in launch['source_files'].items():
   if name.startswith(('src/','application/','ui/','capabilities/')) or name in ['Cargo.toml','Cargo.lock','tauri.conf.json','build.rs','root_profile.rs','root_profiles.json']:
    if sha((BASE/'candidate'/name).read_bytes())!=digest:errors.append('runtime_source_drift')
 runtime=json.loads((BASE/'evidence/real-wiring-runtime.json').read_text())
 if not runtime['marker_verified'] or not runtime['writers_stopped'] or runtime['wal_count'] or runtime['removed']:errors.append('runtime_retention')
 real_ui=json.loads((BASE/m['real_ui_evidence']).read_text())
 if real_ui['count']!=3 or real_ui['real_path_contact'] is not False:errors.append('real_ui')
 pilot=json.loads((BASE/m['pilot_test_evidence']).read_text())
 if pilot['exit_code']!=0 or pilot['test_only_paths'] is not True or pilot['real_path_contact'] is not False or pilot['filter']!='pilot_normal_lifecycle':errors.append('pilot_test')
 if '1 passed; 0 failed' not in (BASE/Path(m['pilot_test_evidence']).parent/'ordinary.log').read_text():errors.append('pilot_test_log')
 hist=BASE/'history/pre-real-wiring'
 for row in json.loads((hist/'lineage.json').read_text())['files']:
  if sha((hist/row['path']).read_bytes())!=row['sha256']:errors.append('wiring_history')
 package=json.loads((BASE/m['real_app_package']).read_text())
 app=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS Local Source.app')
 if package['app']!=str(app) or package['profile']!='source-pilot-1' or package['build_exit_code']!=0 or package['launched'] is not False or package['real_path_contact'] is not False:errors.append('package')
 else:
  for name,digest in package['app_files'].items():
   p=Path(name)
   if p.is_absolute() or '..' in p.parts:errors.append('package_path');continue
   if (app/p).is_symlink() or sha((app/p).read_bytes())!=digest:errors.append('package_hash')
  if sha((app/'Contents/MacOS/lifeos-p3-147').read_bytes())!=package['binary_sha256']:errors.append('package_binary')
  if (app/'Contents/Resources/parse_source.py').read_bytes()!=(BASE/'candidate/tools/parse_source.py').read_bytes():errors.append('package_parser')
 return errors
if __name__=='__main__':
 m=json.loads((BASE/'FINAL_MANIFEST.json').read_text());errors=verify(m)
 print(json.dumps({'package_integrity':not errors,'errors':errors,'files':len(m['files']),'ordinary_checks':10,'independent_security':'User-directed review waiver / No Independent Pass','real_activation':'ready_waiting_user_click'}))
 sys.exit(bool(errors))
