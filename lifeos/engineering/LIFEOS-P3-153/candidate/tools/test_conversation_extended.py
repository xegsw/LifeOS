"""Ordinary synthetic paging, failure recovery and cooperating-instance checks."""
from test_source_conversation import *
def run():
 f='extended-'+uuid.uuid4().hex[:10];s=Session(f);other=None;results=[]
 try:
  seed(s)
  s.call('get_source_status',payload={},version=1,expect='local_activation_required')
  assert not (ROOT/(f+'-provider.sqlite')).exists()
  s.call('get_context_recovery','open_conversation',{'requestId':'open','conversationId':'source-chat'})
  assert s.call('get_ai_provider_settings','read_settings')['credentialState']=='absent'
  assert not (ROOT/(f+'-provider.sqlite')).exists()
  c=sqlite3.connect(ROOT/(f+'.sqlite'));before=c.execute('pragma schema_version').fetchone()
  s.call('get_source_status',payload={},version=1)
  s.call('get_today','snapshot',{},version=2)
  assert c.execute('pragma schema_version').fetchone()==before
  other=Session(f)
  other.call('get_context_recovery','open_conversation',{'requestId':'open','conversationId':'source-chat'},expect='database_unavailable')
  other.close();other=None
  results.append({'check':'passive_no_provider_creation_existing_schema_and_148_lock','pass':True})
  configure(s)
  for cmd in ['get_today','runtime_status','get_evidence_backed_understanding','get_context_disclosure_receipt','get_ai_provider_settings']:
   s.call(cmd,'snapshot',{},version=2)
  for cmd in ['confirm_capture_context','get_context_recovery','get_context_next_action','decide_context_next_action','record_action_result']:
   s.call(cmd,'unavailable',{},version=2,expect='unavailable')
  for cmd in ['save_ai_provider_credential','test_ai_provider_connection','set_ai_provider_enabled']:
   s.call(cmd,'unavailable',{},version=2,expect='offline_capability_denied')
  results.append({'check':'legacy_snapshot_unavailable_and_offline_provider_routes','pass':True})
  def question(i):
   p={'requestId':f'draft-{i}','draftId':f'draft-{i}','conversationId':'source-chat','turnId':f'turn-{i}','revision':1,'text':f'纸鹤项目图纸 {i}'}
   s.call('capture_record','draft_question',p)
   return s.call('capture_record','save_question',{'requestId':f'save-{i}','draftId':p['draftId'],'conversationId':'source-chat','turnId':p['turnId'],'expectedDraftRevision':1})
  for i in range(51):question(i)
  page=s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat'});assert len(page['turns'])==50 and page.get('nextCursor')
  second=s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat','cursor':page['nextCursor']});assert len(second['turns'])==1 and 'nextCursor' not in second
  assert len({x['turnId'] for x in page['turns']+second['turns']})==51
  question(51)
  s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat','cursor':page['nextCursor']},expect='cursor_stale')
  snap=s.call('get_today','snapshot',{},version=2)
  assert 'source_ai_question' not in json.dumps(snap)
  results.append({'check':'50_51_pagination_cursor_revision_and_legacy_isolation','pass':True})
  d={'requestId':'failure-draft','draftId':'failure-draft','conversationId':'source-chat','turnId':'failure-turn','revision':1,'text':'纸鹤图纸失败保留草稿'}
  s.call('capture_record','draft_question',d)
  c.execute("CREATE TRIGGER synthetic_save_fail BEFORE INSERT ON records BEGIN SELECT RAISE(ABORT,'synthetic'); END");c.commit()
  save={'requestId':'failure-save','draftId':d['draftId'],'conversationId':'source-chat','turnId':d['turnId'],'expectedDraftRevision':1}
  s.call('capture_record','save_question',save,expect='database_unavailable')
  assert s.call('get_context_recovery','read_conversation',{'conversationId':'source-chat'})['pendingDraft']['text']==d['text']
  c.execute('DROP TRIGGER synthetic_save_fail');c.commit();s.call('capture_record','save_question',save)
  results.append({'check':'save_transaction_failure_keeps_draft_then_same_request_recovers','pass':True})
  p={'requestId':'preview-restart','conversationId':'source-chat','turnId':'turn-0','expectedQuestionVersion':1,'excludedSegmentIds':[]}
  v=s.call('assemble_global_ai_context','prepare_source_preview',p)
  raw=json.loads(c.execute('SELECT body FROM packets WHERE id=?',(v['previewId'],)).fetchone()[0]);raw.update(state='consumed',deliveryState='dispatching',dispatchId='synthetic-interrupted-dispatch')
  c.execute('UPDATE packets SET body=? WHERE id=?',(json.dumps(raw),v['previewId']));c.commit();c.close()
  s.close();s=Session(f);s.call('get_context_recovery','open_conversation',{'requestId':'restart','conversationId':'source-chat'})
  a=s.call('get_evidence_backed_understanding','read_answer',{'dispatchId':'synthetic-interrupted-dispatch'})
  assert a['state']=='outcome_unknown'
  for i in range(3):assert s.call('get_evidence_backed_understanding','read_answer',{'dispatchId':'synthetic-interrupted-dispatch'})['state']=='outcome_unknown'
  results.append({'check':'cross_process_dispatch_recovery_never_resends','pass':True})
  s.call('connect_source_directory',payload={'requestId':'no-scan'},version=1,expect='source_scan_disabled')
  s.call('authorize_source_target',payload={'requestId':'no-external','connectorId':'directory','expectedGeneration':1,'linkId':'fiction-link','decision':'allow'},version=1,expect='external_targets_disabled')
  for action in ['refresh','resume','pause','cancel']:
   s.call('control_source_job',payload={'requestId':'no-'+action,'connectorId':'directory','expectedGeneration':1,'action':action},version=1,expect='source_scan_disabled')
  found=s.call('get_source_evidence',payload={'mode':'search','connectorId':'directory','query':'纸鹤','expectedGeneration':1},version=1)['results'];assert found
  detail=s.call('get_source_evidence',payload={'mode':'detail','connectorId':'directory','sourceRef':found[0]['sourceRef'],'expectedVersion':1},version=1);assert detail['version']==1 and detail['segments']
  s.call('control_source_job',payload={'requestId':'disconnect-end','connectorId':'directory','expectedGeneration':1,'action':'disconnect'},version=1)
  assert not s.call('get_source_status',payload={},version=1)['connectors']
  s.call('get_source_evidence',payload={'mode':'detail','connectorId':'directory','sourceRef':found[0]['sourceRef'],'expectedVersion':1},version=1,expect='authorization_rejected')
  results.append({'check':'five_source_ipc_allowed_and_disabled_branches','pass':True})
  results.extend(budget())
  return {'fixture':f,'results':results,'scope':'new synthetic ordinary fixtures only; no network or OS credential adapter'}
 finally:
  if other:other.close()
  s.close()
def budget():
 f='budget-'+uuid.uuid4().hex[:10];s=Session(f)
 try:
  seed(s);configure(s);c=sqlite3.connect(ROOT/(f+'.sqlite'))
  content='纸鹤图纸'+('\x01'*1000)
  c.execute("UPDATE source_segments SET text=?",(content,))
  c.execute("UPDATE records SET body=json_set(body,'$.text',?) WHERE json_extract(body,'$.sourceFile') IS NOT NULL",(content,));c.commit();c.close()
  for i,question in enumerate(['纸鹤图纸','纸鹤图纸'+('\x01'*1996)]):
   d={'requestId':f'draft-{i}','draftId':f'draft-{i}','conversationId':'source-chat','turnId':f'turn-{i}','revision':1,'text':question}
   s.call('capture_record','draft_question',d)
   s.call('capture_record','save_question',{'requestId':f'save-{i}','draftId':d['draftId'],'conversationId':'source-chat','turnId':d['turnId'],'expectedDraftRevision':1})
   p={'requestId':f'preview-{i}','conversationId':'source-chat','turnId':d['turnId'],'expectedQuestionVersion':1,'excludedSegmentIds':[]}
   if i:s.call('assemble_global_ai_context','prepare_source_preview',p,expect='context_budget_rejected')
   else:
    v=s.call('assemble_global_ai_context','prepare_source_preview',p);assert len(v['items'])==3 and v['budget']['usedSourceScalars']==2400
    assert v['budget']['usedInputBytes']==len(v['bodyJson'].encode())
  return [{'check':'three_800_scalar_windows_and_json_escape_overhead_limit','pass':True}]
 finally:s.close()
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=True,indent=2))
