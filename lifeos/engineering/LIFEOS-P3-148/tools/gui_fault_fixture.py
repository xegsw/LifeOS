"""Finite new GUI failure fixtures in the explicitly owned synthetic app DB only."""
from pathlib import Path
import sys,json,sqlite3,time
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'candidate/tools'))
from task_root import ROOT,verify
verify()
c=sqlite3.connect('file:'+str(ROOT/'app.sqlite')+'?mode=rw',uri=True)
mode=sys.argv[1]
if mode=='save-fail':
 c.execute("CREATE TRIGGER p148_closure_save_fail BEFORE INSERT ON records WHEN json_extract(NEW.body,'$.kind')='source_ai_question' BEGIN SELECT RAISE(ABORT,'synthetic save failure'); END")
elif mode in ['prepare-fail','only-prepare-fail']:
 if mode=='prepare-fail':c.execute('DROP TRIGGER p148_closure_save_fail')
 c.execute("CREATE TRIGGER p148_closure_prepare_fail BEFORE INSERT ON packets WHEN json_extract(NEW.body,'$.kind')='source_ai_preview' BEGIN SELECT RAISE(ABORT,'synthetic prepare failure'); END")
elif mode=='clear-prepare': c.execute('DROP TRIGGER p148_closure_prepare_fail')
elif mode=='display-states':
 original=json.loads(c.execute("SELECT body FROM packets WHERE json_extract(body,'$.kind')='source_ai_preview' LIMIT 1").fetchone()[0])
 for n,(case,state,code) in enumerate([('auth','failed','provider_authentication'),('model','failed','provider_model'),('empty','failed','provider_protocol'),('limit','failed','response_too_large'),('unknown','outcome_unknown','dispatch_outcome_unknown'),('literal','succeeded',None)]):
  prefix='p148-gui-closure-'+case; qid=prefix+'-question';did=prefix+'-dispatch';pid=prefix+'-preview';aid=prefix+'-answer'
  question={'id':qid,'schemaVersion':3,'kind':'source_ai_question','intent':'question','sourceId':'conversation','conversationId':'source-chat','turnId':prefix,'text':'虚构故障界面检查：'+case,'version':1,'status':'active','createdAt':int(time.time()*1000)+n}
  packet={**original,'id':pid,'previewId':pid,'questionId':qid,'question':question['text'],'turnId':prefix,'dispatchId':did,'state':'consumed','deliveryState':state,'errorCode':code,'expiresAt':int(time.time()*1000)}
  c.execute('INSERT INTO records VALUES(?,?)',(qid,json.dumps(question)));c.execute('INSERT INTO packets VALUES(?,?)',(pid,json.dumps(packet)))
  if state=='succeeded':
   answer={'id':aid,'answerId':aid,'kind':'source_ai_answer','schemaVersion':3,'dispatchId':did,'state':'succeeded','revision':1,'text':'纯文本检查 <img src="https://example.invalid/pixel"> <b>不是HTML</b> [C99]','citations':[],'invalidCitationCount':1,'status':'candidate','confirmed':False,'provider':'DeepSeek','modelId':'deepseek-synthetic-v1','startedAt':1,'finishedAt':2,'inputRefs':[],'conversationId':'source-chat','turnId':prefix}
   c.execute('INSERT INTO derivations VALUES(?,?)',(aid,json.dumps(answer)))
 c.execute('UPDATE meta SET revision=revision+1 WHERE id=1')
else: raise SystemExit('unknown fixture action')
c.commit();c.close();print(json.dumps({'synthetic_fixture_action':mode,'app_db_only':True}))
