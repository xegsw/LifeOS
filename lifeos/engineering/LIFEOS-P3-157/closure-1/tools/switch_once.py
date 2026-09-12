"""Authorized fixed App lifecycle. Reads code identity only, never real data or UI."""
from pathlib import Path
import os,json,subprocess,hashlib,select,ctypes,datetime
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-157-real-actions-v1/closure-1');helper=root/'app-identity';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();os.umask(0o077)
def save(name,v):(b/'evidence'/name).write_text(json.dumps(v,indent=2)+'\n')
assert json.loads((b/'evidence/check-summary.json').read_text())['checks']==281
assert json.loads((b/'evidence/mutations/results.json').read_text())['allKilled']
assert all(v['passed'] for v in json.loads((b/'evidence/build-mode-guards.json').read_text()))
new=json.loads((b/'evidence/real-bundle.json').read_text());old=json.loads((b.parent/'evidence/real-bundle.json').read_text())
assert old['app']=='/private/tmp/lifeos-p3-157-real-actions-v1/LifeOS P3-157 Real Actions.app'
assert new['app']==str(root/'LifeOS P3-157 C1 Real Actions.app')
for v in [old,new]:
 app=Path(v['app']);assert not app.is_symlink()
 actual={str(p.relative_to(app)) for p in app.rglob('*') if p.is_file()};assert actual==set(v['bundleFiles'])
 for rel,h in v['bundleFiles'].items():
  q=Path(rel);assert not q.is_absolute() and '..' not in q.parts;assert not (app/q).is_symlink();assert sha(app/q)==h
for rel,h in new['candidateFiles'].items():assert sha(b/'candidate'/rel)==h
save('package-identity.json',{'oldCodeVerified':True,'newCodeVerified':True,'oldBinarySha256':old['binarySha256'],'newBinarySha256':new['binarySha256'],'newCandidateFiles':len(new['candidateFiles'])})
state=json.loads(subprocess.check_output([str(helper),'inspect'],text=True));save('identity-before.json',state)
old_instances=[x for x in state['instances'] if x['executable']==old['binary']];new_instances=[x for x in state['instances'] if x['executable']==new['binary']];assert len(old_instances)==1 and old_instances[0]['pid']==84364 and not new_instances,'identity conflict'
claim=b/'evidence/launch-claim.json'
with claim.open('x') as f:json.dump({'task':'P3-157','binary':new['binary'],'binarySha256':new['binarySha256'],'singleAttempt':True,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()},f,indent=2)
if old_instances:
 quit_result=json.loads(subprocess.check_output([str(helper),'quit',str(old_instances[0]['pid'])],text=True));save('normal-quit.json',quit_result);assert quit_result['exited'] and quit_result['normal_quit_requested']
else:save('normal-quit.json',{'oldAlreadyNotRunning':True,'exited':True,'normal_quit_requested':False})
p=subprocess.Popen([new['binary']],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,env=dict(os.environ,TMPDIR=str(root/'tmp')))
ready,_,_=select.select([p.stdout],[],[],20);receipt=json.loads(p.stdout.readline()) if ready else {'status':'startup_timeout'}
lib=ctypes.CDLL('/usr/lib/libproc.dylib');buf=ctypes.create_string_buffer(4096);matched=lib.proc_pidpath(p.pid,buf,4096)>0 and buf.value.decode()==new['binary']
launch={'pid':p.pid,'binary':new['binary'],'binarySha256':new['binarySha256'],'startup':receipt,'running':p.poll() is None,'directPidMatched':matched,'singleAttempt':True};save('launch.json',launch)
cp=json.loads((b/'checkpoint.json').read_text());cp.update(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage='app_launch',status='paused_resumable',pause_class='user_validation',pause_reason_code='user_result_pending',resume_from='user_actual_actions_validation',safe_to_resume=True);cp['runtime']={'app_running':launch['running'],'direct_pid':p.pid,'writers_stopped':False,'database_closed':False,'temporary_root_state':'owned; real App uses existing-only authorized root'};cp['completed_checks']=cp.get('completed_checks',[])+['old and new complete App code identities verified','normal old App exit','single launch attempt and fixed receipt'];cp['pending_checks']=['user ABF08 result'];cp['notes']='No true content, Key, AX, screenshot, content log or data hash collected. No refresh/import/send. Do not relaunch on unlock; inspect existing claim and fixed identity only.';(b/'checkpoint.json').write_text(json.dumps(cp,indent=2)+'\n')
print(json.dumps(launch));assert receipt=={'status':'controlled_conversation_started'} and matched and launch['running']
state=json.loads(subprocess.check_output([str(helper),'inspect'],text=True));save('identity-after.json',state);assert len(state['instances'])==1 and state['instances'][0]['pid']==p.pid
