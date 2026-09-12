"""P3-148 ordinary synthetic conversation integration. No real mode or network."""
from pathlib import Path
import json,os,sqlite3,subprocess,uuid
from task_root import ROOT,verify
verify()
BINARY=ROOT/'target/debug/lifeos-p3-148'
class Session:
 def __init__(self,fixture):
  self.fixture=fixture
  self.p=subprocess.Popen([str(BINARY),'--repository-stdio',fixture],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ,'LIFEOS_P3_148_BUILD_PROFILE':'engineering'})
 def call(self,command,op=None,payload=None,version=3,expect=None):
  req={'version':version,'payload':payload or {}}
  if op is not None:req['operation']=op
  self.p.stdin.write(json.dumps({'ipc':command,'request':req},ensure_ascii=True)+'\n');self.p.stdin.flush()
  line=self.p.stdout.readline()
  if not line:raise AssertionError('candidate exited: '+self.p.stderr.read()[-1200:])
  out=json.loads(line)
  if expect:
   assert out.get('error',{}).get('code')==expect,(expect,out);return out
  assert 'ok' in out,out
  return out['ok']
 def close(self):
  self.p.stdin.close();self.p.wait(timeout=5)
def seed(session):
 subprocess.run([str(BINARY),'--init-synthetic-fixture',session.fixture],check=True,capture_output=True)
 c=sqlite3.connect(ROOT/(session.fixture+'.sqlite'))
 c.execute("INSERT INTO connectors VALUES('directory',1,1,'active','app-source')")
 c.execute('INSERT INTO sources VALUES(?,?)',('directory',json.dumps({'id':'directory','authorized':True,'generation':1,'sourceType':'local_file'})))
 for i,text in enumerate(['纸鹤项目星期四整理图纸，先按日期分类。','纸鹤项目图纸复核由林岚完成。','纸鹤项目每周一更新清单。','花园的向日葵需要浇水。','纸鹤项目图纸保留原始编号。']):
  fid=f'fixture-file-{i}';rid=f'seg:{fid}:1:0';artifact=f'artifact-{i}'
  c.execute('INSERT INTO source_artifacts VALUES(?,?,?,?,?)',(artifact,artifact,'text/markdown',len(text.encode()),1))
  c.execute('INSERT INTO source_files VALUES(?,?,?,?,?,?,?,?,?,?)',(fid,'directory',f'fiction-{i}.md',1,'{}','synthetic',artifact,'parsed',None,1))
  record={'id':rid,'sourceId':'directory','externalId':f'fiction-{i}:0','version':1,'text':text,'domain':'person','status':'active','intent':'source','observedAt':1,'sourceFile':fid,'locator':'line:1','confirmed':False}
  c.execute('INSERT INTO records VALUES(?,?)',(rid,json.dumps(record)))
  c.execute('INSERT INTO source_segments VALUES(?,?,?,?,?,?,?)',(rid,fid,1,0,'line:1',text,rid))
 c.commit();c.close()
def configure(s):
 s.call('get_context_recovery','open_conversation',{'requestId':'open','conversationId':'source-chat'})
 p={'requestId':'key-save','profileId':'deepseek-default','expectedCredentialRevision':0,'apiKey':'synthetic-only-canary-key'}
 saved=s.call('save_ai_provider_credential','replace_credential',p)
 assert saved['state']=='stored'
 assert s.call('save_ai_provider_credential','replace_credential',p)==saved
 tested=s.call('test_ai_provider_connection','test_connection',{'requestId':'test','profileId':'deepseek-default','expectedCredentialRevision':1,'confirmation':'test_deepseek_models_once'})
 setting=s.call('get_ai_provider_settings','read_settings')
 selected=s.call('save_ai_provider_settings','select_model',{'requestId':'select','profileId':'deepseek-default','expectedProfileRevision':setting['profileRevision'],'testReceiptId':tested['testReceiptId'],'modelId':tested['models'][0]})
 s.call('set_ai_provider_enabled','set_enabled',{'requestId':'enable','profileId':'deepseek-default','expectedProfileRevision':selected['profileRevision'],'enabled':True})
def run(fixture=None):
 fixture=fixture or ('conversation-'+uuid.uuid4().hex[:10]);s=Session(fixture);results=[]
 try:
  seed(s);configure(s)
  p={'requestId':'draft-1','draftId':'draft-one','conversationId':'source-chat','turnId':'turn-one','revision':1,'text':'纸鹤项目图纸如何整理？'}
  s.call('capture_record','draft_question',p);s.call('capture_record','draft_question',p)
  recovered=s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat'})
  assert set(recovered['pendingDraft'])=={'draftId','conversationId','turnId','revision','text','requestId'}
  assert recovered['pendingDraft']['text']==p['text']
  s.call('get_context_recovery','read_conversation',{'conversationId':'other-chat'},expect='authorization_rejected')
  other=s.call('get_context_recovery','open_conversation',{'requestId':'open-other','conversationId':'other-chat'})
  assert 'pendingDraft' not in other
  s.close();s=Session(fixture)
  resumed=s.call('get_context_recovery','open_conversation',{'requestId':'resume-draft','conversationId':'source-chat'})
  assert resumed['pendingDraft']['draftId']==p['draftId']
  results.append({'check':'E01_draft_restart_and_session_isolation','pass':True})
  s.call('capture_record','draft_question',{**p,'requestId':'draft-conflict','text':'different'},expect='draft_conflict')
  saved={'requestId':'save-one','draftId':'draft-one','conversationId':'source-chat','turnId':'turn-one','expectedDraftRevision':1}
  q=s.call('capture_record','save_question',saved);assert q==s.call('capture_record','save_question',saved)
  assert q==s.call('capture_record','save_question',{**saved,'requestId':'save-again'})
  assert 'pendingDraft' not in s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat'})
  results.append({'check':'draft_save_idempotency','pass':True})
  s.call('capture_record','draft_question',{**p,'unexpected':True},expect='unknown_field')
  preview=s.call('assemble_global_ai_context','prepare_source_preview',{'requestId':'preview-one','conversationId':'source-chat','turnId':'turn-one','expectedQuestionVersion':1,'excludedSegmentIds':[]})
  assert preview['state']=='ready' and len(preview['items'])==3
  assert preview['budget']['usedInputBytes']==len(preview['bodyJson'].encode())
  assert all('向日葵' not in x['text'] for x in preview['items'])
  repeated=s.call('assemble_global_ai_context','prepare_source_preview',{'requestId':'preview-repeat','conversationId':'source-chat','turnId':'turn-one','expectedQuestionVersion':1,'excludedSegmentIds':[]})
  assert repeated['items']==preview['items'] and repeated['bodyJson']==preview['bodyJson'];preview=repeated
  results.append({'check':'relevant_bounded_preview_four_matches_stable_top3','pass':True})
  send={'requestId':'send-one','previewId':preview['previewId'],'expectedPreviewRevision':1,'confirmationToken':preview['confirmationToken']}
  s.call('send_source_ai_request','confirm_send',{**send,'confirmationToken':'bad'},version=1,expect='confirmation_rejected')
  out=s.call('send_source_ai_request','confirm_send',send,version=1);assert out['state']=='succeeded'
  again=s.call('send_source_ai_request','confirm_send',{**send,'requestId':'send-again'},version=1);assert out['dispatchId']==again['dispatchId']
  answer=s.call('get_evidence_backed_understanding','read_answer',{'dispatchId':out['dispatchId']})
  assert answer['confirmed'] is False and answer['citations'][0]['citationId']=='C1'
  results.append({'check':'confirm_send_answer_citation','pass':True})
  s.call('decide_understanding_feedback','answer_feedback',{'requestId':'feedback-one','answerId':answer['answerId'],'expectedAnswerRevision':1,'decision':'correct','correctionText':'请按材料类型整理，不按日期。','affectedCitationIds':[]})
  assert s.call('get_evidence_backed_understanding','read_answer',{'dispatchId':out['dispatchId']})['validity']=='stale'
  s.close();s=Session(fixture)
  read=s.call('get_context_recovery','open_conversation',{'requestId':'open-again','conversationId':'source-chat'})
  assert len(read['turns'])==1 and read['turns'][0]['answer']['validity']=='stale'
  assert read['turns'][0]['feedbackIds']==['feedback-one']
  assert s.call('capture_record','save_question',saved)==q
  corrected=s.call('assemble_global_ai_context','prepare_source_preview',{'requestId':'corrected-after-restart','conversationId':'source-chat','turnId':'turn-one','expectedQuestionVersion':1,'excludedSegmentIds':[]})
  assert any(i['kind']=='user_correction' and i['text']=='请按材料类型整理，不按日期。' for i in corrected['items'])
  assert s.call('get_ai_provider_settings','read_settings')['credentialState']=='stored'
  assert s.call('test_ai_provider_connection','test_connection',{'requestId':'test-after-restart','profileId':'deepseek-default','expectedCredentialRevision':1,'confirmation':'test_deepseek_models_once'})['state']=='succeeded'
  results.append({'check':'correction_and_restart_persistence','pass':True})
  c=sqlite3.connect(ROOT/(fixture+'-provider.sqlite'))
  text=''.join(str(r) for t in ['provider_profile','provider_operations'] for r in c.execute('SELECT * FROM '+t));c.close()
  assert 'synthetic-only-canary-key' not in text
  results.append({'check':'no_plain_secret_in_provider_store','pass':True})
  return {'fixture':fixture,'results':results,'scope':'synthetic ordinary functional checks only','network_calls':0,'os_credential_calls':0}
 finally:s.close()
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=True,indent=2))
