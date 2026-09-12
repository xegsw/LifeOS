"""Engineering adaptation of IR-P0-147-001. All sentinels stay in selected owned root.
Review original and results remain immutable history; no review runtime is accessed.
"""
import unittest,os,json,hashlib,subprocess,time,stat,sqlite3
from pathlib import Path
from task_root import ROOT,PROFILE,verify,verify_binary
BIN=ROOT/'initial-build-cache/debug/lifeos-p3-147'
class TargetBoundaries(unittest.TestCase):
 def scenario(self,kind,attack):
  verify();verify_binary(BIN)
  fixture='boundary-'+str(time.time_ns())
  sentinel=ROOT/'fixtures'/(fixture+'-sentinel');sentinel.mkdir(mode=0o700)
  (sentinel/'canary').write_bytes(b'SYNTHETIC-UNTOUCHED');(sentinel/'canary').chmod(0o640);sentinel.chmod(0o750)
  def snap():return {'mode':stat.S_IMODE(sentinel.stat().st_mode),'files':{p.name:{'mode':stat.S_IMODE(p.stat().st_mode),'body':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sentinel.iterdir()}}
  before=snap();events=[];proc=subprocess.Popen([str(BIN),'--repository-stdio',fixture],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  target_dir=ROOT/'artifacts'/('target-'+hashlib.sha256(fixture.encode()).hexdigest()[:16])
  def call(ipc,payload):
   req={'ipc':ipc,'request':{'version':1,'payload':payload}};proc.stdin.write(json.dumps(req)+'\n');proc.stdin.flush();reply=json.loads(proc.stdout.readline());events.append({'request':req,'reply':reply});return reply
  def status():
   v=call('get_source_status',{'connectorId':'directory'});self.assertIn('ok',v);return v['ok']['connectors'][0]
  def wait(check):
   for _ in range(300):
    s=status()
    if check(s):return s
    time.sleep(.03)
   self.fail('worker timeout')
  connection=None
  try:
   self.assertIn('ok',call('connect_source_directory',{'requestId':'connect'}))
   s=wait(lambda s:s['scanComplete'] and s['pending']==0)
   target='../external/approved.txt' if kind=='local' else 'https://synthetic.invalid/article'
   link=next(l for l in s['links'] if l['target']==target)['linkId']
   token='target-'+hashlib.sha256(link.encode()).hexdigest()[:32]+'-1'
   if attack=='directory-link':target_dir.symlink_to(sentinel,target_is_directory=True)
   elif attack in ('file-link','staging-link'):
    target_dir.mkdir(mode=0o700);(target_dir/(token+('.staging' if attack=='staging-link' else ''))).symlink_to(sentinel/'canary')
   elif attack=='receipt-failure':
    connection=sqlite3.connect(ROOT/(fixture+'.sqlite'))
    connection.execute("CREATE TRIGGER target_receipt_fail BEFORE INSERT ON connector_requests WHEN NEW.id LIKE 'fetch:%' BEGIN SELECT RAISE(ABORT,'synthetic fault'); END");connection.commit()
   grant=call('authorize_source_target',{'requestId':'grant','connectorId':'directory','expectedGeneration':s['grantGeneration'],'linkId':link,'decision':'grant'});self.assertIn('ok',grant)
   s=wait(lambda s:next(l for l in s['links'] if l['linkId']==link)['status']!='fetch_pending')
   observed=next(l for l in s['links'] if l['linkId']==link)['status']
   self.assertEqual(snap(),before)
   if attack=='control':self.assertEqual(observed,'fetched')
   else:
    self.assertNotEqual(observed,'fetched');self.assertTrue(observed.startswith('unavailable:'))
    db=connection or sqlite3.connect(ROOT/(fixture+'.sqlite'))
    try:self.assertEqual(db.execute("SELECT count(*) FROM records WHERE json_extract(body,'$.sourceId') LIKE 'target:%'").fetchone()[0],0)
    finally:
     if not connection:db.close()
   self.results.append({'case':kind+'-'+attack,'pid':proc.pid,'status':observed,'sentinel_unchanged':before==snap(),'before':before,'after':snap(),'events':events,'passed':True})
  finally:
   if connection:connection.close()
   proc.stdin.close();proc.wait(timeout=15);proc.stderr.close();proc.stdout.close()
 @classmethod
 def setUpClass(cls):cls.results=[]
 @classmethod
 def tearDownClass(cls):
  out=Path(__file__).resolve().parents[2]/'evidence'/('artifact-target-'+str(time.time_ns())+'.json')
  out.write_text(json.dumps({'profile':PROFILE,'binary_sha256':hashlib.sha256(BIN.read_bytes()).hexdigest(),'source':'adapted review counterexample plus engineering negative paths','review_runtime_contact':False,'results':cls.results},ensure_ascii=False,indent=2))
for kind in ['web','local']:
 for attack in ['control','directory-link','file-link','staging-link','receipt-failure']:
  setattr(TargetBoundaries,'test_'+kind+'_'+attack.replace('-','_'),lambda self,k=kind,a=attack:self.scenario(k,a))
if __name__=='__main__':unittest.main(verbosity=2)
