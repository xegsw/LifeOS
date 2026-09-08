"""Review-owned M02/M04 target artifact directory substitution counterexample.
No engineering tests imported. All fixture paths are inside the review-owned root.
Run against the pristine compiled candidate; do not patch product sources.
"""
import os,json,hashlib,subprocess,time,stat
from pathlib import Path
ROOT=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1')
OUT=Path('/private/tmp/lifeos-p3-147-obsidian-source-v1/.runtime/review-repro-1788847179082677000')
BIN=ROOT/'initial-build-cache/debug/lifeos-p3-147'
os.umask(0o077)
ENV={**os.environ,'LIFEOS_P3_147_BUILD_PROFILE':'engineering','TMPDIR':str(ROOT/'tmp'),'PYTHONDONTWRITEBYTECODE':'1'}
assert json.loads(subprocess.check_output([str(BIN),'--profile-info'],env=ENV))=={'profile':'engineering','root':str(ROOT)}
source=ROOT/'fixtures/app-source';assert source.is_dir()
def snap(p):
 return {'mode':oct(stat.S_IMODE(p.lstat().st_mode)),'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.iterdir() if f.is_file()}}
results=[]
for fixture,attack in [('ir-target-control-1788847179082981000',False),('ir-target-link-1788847179082984000',True)]:
 events=[]
 sentinel=ROOT/(fixture+'-sentinel');sentinel.mkdir(mode=0o700);(sentinel/'canary.txt').write_text('IR-SYNTHETIC-DO-NOT-WRITE')
 sentinel.chmod(0o750)
 target_dir=ROOT/'artifacts'/('target-'+hashlib.sha256(fixture.encode()).hexdigest()[:16])
 if attack:target_dir.symlink_to(sentinel,target_is_directory=True)
 before=snap(sentinel)
 stderr=(OUT/(fixture+'.stderr')).open('xb')
 p=subprocess.Popen([str(BIN),'--repository-stdio',fixture],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,env=ENV)
 def call(ipc,payload):
  req={'ipc':ipc,'request':{'version':1,'payload':payload}};p.stdin.write(json.dumps(req)+'\n');p.stdin.flush();reply=json.loads(p.stdout.readline());events.append({'request':req,'response':reply});return reply
 try:
  connect=call('connect_source_directory',{'requestId':fixture+'-connect'});assert 'ok' in connect,connect
  for _ in range(200):
   st=call('get_source_status',{'connectorId':'directory'});rows=st.get('ok',{}).get('connectors',[])
   if rows and rows[0]['scanComplete'] and rows[0]['pending']==0:break
   time.sleep(.05)
  assert rows and rows[0]['links'],st
  link=next(l for l in rows[0]['links'] if l['target']=='https://synthetic.invalid/article')['linkId']
  grant=call('authorize_source_target',{'requestId':fixture+'-grant','connectorId':'directory','expectedGeneration':1,'linkId':link,'decision':'grant'});assert 'ok' in grant,grant
  for _ in range(200):
   st=call('get_source_status',{'connectorId':'directory'});links=[l for l in st['ok']['connectors'][0]['links'] if l['linkId']==link]
   if links and links[0]['status']!='fetch_pending':break
   time.sleep(.05)
  after=snap(sentinel)
  result={'id':'IR-TARGET-LINK' if attack else 'IR-TARGET-CONTROL','matrix':['M02','M04'],'fixture':fixture,'pid':p.pid,'attack':attack,'before':before,'after':after,'target_status':links,'expected':'reject symlink before chmod/create; sentinel unchanged' if attack else 'successful target fetch','passed':before==after and links[0]['status']!='fetched' if attack else links[0]['status']=='fetched','events':events}
  results.append(result)
 finally:
  p.stdin.close();p.wait(timeout=10);stderr.close()
(OUT/'target-boundary-results.json').write_text(json.dumps({'binary_sha256':hashlib.sha256(BIN.read_bytes()).hexdigest(),'source_mutated':False,'results':results,'writers_stopped':True},ensure_ascii=False,indent=2))
print(json.dumps([{k:v for k,v in r.items() if k!='events'} for r in results],ensure_ascii=False,indent=2))
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
