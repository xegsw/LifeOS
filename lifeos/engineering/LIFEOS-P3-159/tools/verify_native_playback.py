"""Same-candidate A native link/ledger checks. Never enables real audio or HTTP."""
from pathlib import Path
import os,json,datetime,subprocess,hashlib
b=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-159-unified-proactive-v1');os.umask(0o077)
assert json.loads((root/'.owner.json').read_text())==dict(task='P3-159',root=str(root),owner='01a07f0e-dbbd-7d23-9e6d-68f2152f9484')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');out=b/'evidence'/('A-native-playback-'+stamp);out.mkdir();run=root/'offline'/('native-playback-'+stamp);run.mkdir(mode=0o700)
source=b/'candidate/src/voice/native';test=b/'contracts/voice-native-a38a90cf/tools/test_playback_ledger.swift';assert hashlib.sha256(test.read_bytes()).hexdigest()=='bf491534973418e77f29be9ac154168fa36e5b0eed020738f72dfbf240a3d9f0'
env=dict(os.environ,LIFEOS_P3_159_MODE='synthetic',CARGO_TARGET_DIR=str(root/'build/offline'),TMPDIR=str(root/'offline/tmp'),CARGO_NET_OFFLINE='true')
commands=[('ledger-build',['/usr/bin/xcrun','swiftc',str(source/'PlaybackLedger.swift'),str(test),'-o',str(run/'ledger-test')]),('ledger-fake',[str(run/'ledger-test')]),('real-typecheck',['/usr/bin/xcrun','swiftc','-D','LIFEOS_VOICE_REAL','-typecheck',*[str(source/n) for n in ['PlaybackLedger.swift','AudioEngine.swift','MiMoHTTP.swift']]]),('same-app-rust-ffi',['/Users/xxe/.cargo/bin/cargo','test','--offline','--locked','--features','synthetic-driver,voice-native-tests','--manifest-path',str(b/'candidate/Cargo.toml'),'--bin','lifeos-p3-152','voice::native::tests','--','--test-threads=1'])]
results=[]
for name,cmd in commands:
 with (out/(name+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 results.append({'step':name,'exitCode':r.returncode,'log':str(out/(name+'.log'))});print(name,r.returncode,flush=True)
 if r.returncode:break
(out/'result.json').write_text(json.dumps({'steps':results,'actualDeviceOpens':0,'actualPlayback':0,'credentialReads':0,'actualPosts':0,'realBranch':'typecheck only; linked library always A hard-disabled'},indent=2)+'\n')
raise SystemExit(any(x['exitCode'] for x in results))
