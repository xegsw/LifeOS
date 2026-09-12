"""Synthetic public-IPC lifecycle. No network, credentials or real source paths."""
import json,os,subprocess,time,unittest,sqlite3
from pathlib import Path
from task_root import ROOT,verify
BIN=ROOT/'initial-build-cache/debug/lifeos-p3-147'
class SourceAPI(unittest.TestCase):
 def test_public_lifecycle(self):
  verify();fixture='public-'+str(os.getpid())
  proc=subprocess.Popen([str(BIN),'--repository-stdio',fixture],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  def raw(ipc,p,version=1,operation=None):
   request={'version':version,'payload':p}
   if operation:request['operation']=operation
   proc.stdin.write(json.dumps({'ipc':ipc,'request':request})+'\n');proc.stdin.flush();return json.loads(proc.stdout.readline())
  def call(ipc,p):
   result=raw(ipc,p);self.assertIn('ok',result);return result['ok']
  def status():return call('get_source_status',{})['connectors'][0]
  def done():
   end=time.monotonic()+40
   while time.monotonic()<end:
    s=status()
    if s['error']:self.fail(s['error'])
    if s['scanComplete'] and not s['pending']:return s
    time.sleep(.1)
   self.fail('worker timeout')
  try:
   self.assertEqual(call('get_source_status',{}),{'connectors':[]})
   self.assertIn('error',raw('connect_source_directory',{'requestId':'bad','path':'forbidden'}))
   db=sqlite3.connect(ROOT/(fixture+'.sqlite'))
   db.execute("CREATE TRIGGER fail_source_receipt BEFORE INSERT ON source_api_requests BEGIN SELECT RAISE(ABORT,'synthetic failure'); END");db.commit()
   self.assertIn('error',raw('connect_source_directory',{'requestId':'failed-connect'}))
   self.assertEqual(db.execute('SELECT count(*) FROM connectors').fetchone()[0],0)
   db.execute('DROP TRIGGER fail_source_receipt');db.commit()
   connected=call('connect_source_directory',{'requestId':'connect'})
   self.assertEqual(connected,call('connect_source_directory',{'requestId':'connect'}))
   s=done();self.assertEqual(s['discovered'],6);self.assertEqual(s['parsed'],3)
   self.assertNotIn('CONFIG_CANARY',json.dumps(s))
   query={'mode':'search','connectorId':'directory','expectedGeneration':1,'query':'项目计划'}
   matches=call('get_source_evidence',query)['results'];self.assertGreater(len(matches),0);self.assertLessEqual(len(matches),8)
   self.assertEqual(call('get_source_evidence',{**query,'query':'NO_MATCH_CANARY'})['results'],[])
   self.assertIn('error',raw('get_source_evidence',{**query,'cursor':'illegal'}))
   self.assertIn('error',raw('get_source_evidence',{**query,'expectedGeneration':9007199254740992}))
   snap=raw('get_today',{},2,'snapshot')['ok'];self.assertFalse(any('sourceFile'in r for r in snap['records']))
   self.assertNotIn('CONFIG_CANARY',json.dumps(snap))
   saved_cursor=None
   for f in s['files']:
    d=call('get_source_evidence',{'mode':'detail','connectorId':'directory','sourceRef':f['sourceRef'],'expectedVersion':f['version']})
    if f['status']=='restricted':self.assertEqual(d['segments'],[])
    self.assertIn('title',d);self.assertIn('mimeType',d);self.assertIn('observedAt',d)
    if d.get('nextCursor'):
     saved_cursor=(f,d['nextCursor'])
     again=call('get_source_evidence',{'mode':'detail','connectorId':'directory','sourceRef':f['sourceRef'],'expectedVersion':f['version'],'cursor':d['nextCursor']});self.assertTrue(again['segments'])
   call('control_source_job',{'requestId':'refresh','connectorId':'directory','expectedGeneration':1,'action':'refresh'});s=done()
   if saved_cursor:
    f,cursor=saved_cursor;self.assertIn('error',raw('get_source_evidence',{'mode':'detail','connectorId':'directory','sourceRef':f['sourceRef'],'expectedVersion':f['version'],'cursor':cursor}))
   external=[l for l in s['links'] if l['target'].startswith(('https:','../'))]
   self.assertEqual(len(external),2)
   db.execute("CREATE TRIGGER fail_target_receipt BEFORE INSERT ON source_api_requests BEGIN SELECT RAISE(ABORT,'synthetic failure'); END");db.commit()
   self.assertIn('error',raw('authorize_source_target',{'requestId':'failed-grant','connectorId':'directory','expectedGeneration':1,'linkId':external[0]['linkId'],'decision':'grant'}))
   self.assertEqual(db.execute("SELECT count(*) FROM connectors WHERE id LIKE 'target:%'").fetchone()[0],0)
   db.execute('DROP TRIGGER fail_target_receipt');db.commit()
   for i,link in enumerate(external):call('authorize_source_target',{'requestId':f'grant-{i}','connectorId':'directory','expectedGeneration':1,'linkId':link['linkId'],'decision':'grant'})
   end=time.monotonic()+15
   while time.monotonic()<end:
    s=status();targets=[l for l in s['links'] if l['target'].startswith(('https:','../'))]
    if all(l['status']=='fetched' for l in targets):break
    if any(l['status'].startswith('unavailable') for l in targets):self.fail(str([l['status'] for l in targets]))
    time.sleep(.1)
   self.assertTrue(all(l['status']=='fetched' for l in targets))
   matches=call('get_source_evidence',query)['results'];self.assertTrue(any(r['sourceId'].startswith('target:') for r in matches))
   target=next(r for r in matches if r['sourceId'].startswith('target:'))
   for i,link in enumerate(external):call('authorize_source_target',{'requestId':f'revoke-{i}','connectorId':'directory','expectedGeneration':1,'linkId':link['linkId'],'decision':'revoke'})
   self.assertFalse(any(r['sourceId'].startswith('target:') for r in call('get_source_evidence',query)['results']))
   self.assertIn('error',raw('get_source_evidence',{'mode':'detail','connectorId':target['sourceId'],'sourceRef':target['sourceRef'],'expectedVersion':target['version']}))
   call('control_source_job',{'requestId':'disconnect','connectorId':'directory','expectedGeneration':1,'action':'disconnect'})
   self.assertIn('error',raw('get_source_evidence',query));self.assertEqual(call('get_source_status',{})['connectors'],[])
   connected=call('connect_source_directory',{'requestId':'reconnect'});self.assertEqual(connected['grantGeneration'],3);done()
   self.assertIn('error',raw('get_source_evidence',query))
   print('public lifecycle: connection, strict DTO, bounded retrieval, config exclusion, paging, two target bodies, revoke, reconnect passed')
  finally:
   if 'db' in locals():db.close()
   proc.stdin.close();proc.wait(timeout=10);proc.stdout.close();proc.stderr.close()
if __name__=='__main__':unittest.main()
