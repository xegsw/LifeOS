"""Fixed approved launch. Never inspect real roots, databases, Keychain, AX or screen."""
import os,json,hashlib,shutil,plistlib,subprocess,time,stat
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1')
assert not R.is_symlink() and stat.S_IMODE(R.stat().st_mode)==0o700
m=json.loads((R/'.owner.json').read_text());assert m['task']=='P3-152' and m['owner']=='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
a=json.loads((E/'design/pm-approval.json').read_text());assert a['status']=='Approved before real launch';assert a['proposal_sha256']==hashlib.sha256((E/'design/acceptance-supplement-proposal.md').read_bytes()).hexdigest()
assert '40 passed; 0 failed' in (E/'evidence/host-tests.log').read_text()
assert json.loads((E/'evidence/integration-tests.json').read_text())['passed']==8
assert 'Finished' in (E/'evidence/real-build.log').read_text()
os.umask(0o077)
app=R/'LifeOS P3-152 Controlled.app';binary=app/'Contents/MacOS/lifeos-p3-152'
app.mkdir(exist_ok=False);binary.parent.mkdir(parents=True)
shutil.copy2(R/'real-target/debug/lifeos-p3-152',binary)
(app/'Contents/Info.plist').write_bytes(plistlib.dumps(dict(CFBundleExecutable='lifeos-p3-152',CFBundleIdentifier='local.lifeos.p3-152.controlled',CFBundleName='LifeOS Controlled Conversation',CFBundlePackageType='APPL',NSHighResolutionCapable=True)))
# Only process-local startup status is collected. Data paths are literals, never probed here.
log=R/('controlled-startup-'+str(time.time_ns())+'.json')
with log.open('xb') as stream:
 p=subprocess.Popen([str(binary)],stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.DEVNULL,start_new_session=True,env={**os.environ,'TMPDIR':'/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/tmp'})
for _ in range(100):
 time.sleep(.1)
 if log.stat().st_size:break
status='startup_unconfirmed'
if 0<log.stat().st_size<1024:
 try:
  v=json.loads(log.read_text())
  if v=={'status':'controlled_conversation_started'}:status='controlled_conversation_started'
  elif v.get('status')=='failed':status='startup_failed'
 except (ValueError,UnicodeError):pass
r={'status':status,'pid':p.pid,'binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'real_content_captured':False,'agent_sent_request':False}
(E/'evidence/controlled-launch.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if status!='controlled_conversation_started':raise SystemExit(1)
