#!/usr/bin/env python3
"""Offline deterministic entry. No real asset access, microphone, POST or app launch."""
import argparse,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--offline',action='store_true',required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1];candidate=root/'candidate';temp=Path('/private/tmp/lifeos-p3-160-voice-v1')
assert not temp.is_symlink();temp.mkdir(exist_ok=True)
marker=temp/'.p3-160-synthetic.json'
identity={'task':'LIFEOS-P3-160','kind':'synthetic-only','root':str(temp)}
if marker.exists():assert json.loads(marker.read_text())==identity
else:marker.write_text(json.dumps(identity)+'\n')
(temp/'native').mkdir(exist_ok=True);(temp/'tmp').mkdir(exist_ok=True)
run=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=root/'evidence'/run;out.mkdir(parents=True)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=json.loads((root/'inputs/baseline_identity.json').read_text())['sourceFiles']
assert len(original)==182
for path,sha in original.items():assert not (candidate/path).is_symlink() and h(candidate/path)==sha,path
assert h(candidate/'application/voice/interaction-v1.ts')==h(root/'inputs/LIFEOS-INTERACTION-V1.ts')
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
env=dict(os.environ,CARGO_TARGET_DIR=str(temp/'rust-target'),TMPDIR=str(temp/'tmp'))
steps=[('rust',['/Users/xxe/.cargo/bin/cargo','test','--locked','--offline','--manifest-path',str(root/'tools/rust-tests/Cargo.toml')]),('consumer',[node,'--experimental-strip-types','--test',str(root/'tools/test_voice.mjs')]),('legacy-ui',[node,'--test',*[str(candidate/'tools'/n) for n in ['test_e04_flow.mjs','test_health_ui.mjs','test_snapshot_ui.mjs','test_apple_ui.mjs']]]),('native-offline',['/usr/bin/swiftc','-emit-library','-module-name','LifeOSVoice','-o',str(temp/'native/libLifeOSVoice.dylib'),str(candidate/'src/voice/native/AudioEngine.swift'),str(candidate/'src/voice/native/MiMoHTTP.swift')]),('native-real-compile-only',['/usr/bin/swiftc','-D','LIFEOS_VOICE_REAL','-typecheck',str(candidate/'src/voice/native/AudioEngine.swift'),str(candidate/'src/voice/native/MiMoHTTP.swift')]),('sherpa-header',['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-c',str(candidate/'src/voice/native/sherpa_adapter.c'),'-I',str(root/'inputs/sherpa-1.13.7'),'-o',str(temp/'native/sherpa_adapter.o')])]
results=[]
for name,cmd in steps:
 r=subprocess.run(cmd,cwd=candidate,env=env,capture_output=True,text=True,timeout=180)
 (out/(name+'.log')).write_text(r.stdout+r.stderr);results.append({'name':name,'exit':r.returncode,'log':str(out/(name+'.log'))});print(name,r.returncode,flush=True)
 # Continue independent checks after failure; preserve every failing result.
if any(x['name']=='native-offline' and x['exit']==0 for x in results):
 # Exercise ONLY compiled A rejection paths. No native object touches a device/session.
 import ctypes
 lib=ctypes.CDLL(str(temp/'native/libLifeOSVoice.dylib'));P=ctypes.c_void_p;I=ctypes.c_int32
 S=ctypes.CFUNCTYPE(None,P,ctypes.POINTER(ctypes.c_float),I);E=ctypes.CFUNCTYPE(None,P,I)
 sample=S(lambda *a:None);event=E(lambda *a:None)
 lib.lifeos_voice_audio_create.argtypes=[P,S,E];lib.lifeos_voice_audio_create.restype=P
 lib.lifeos_voice_audio_start.argtypes=[P];lib.lifeos_voice_audio_start.restype=I
 lib.lifeos_voice_audio_destroy.argtypes=[P]
 obj=lib.lifeos_voice_audio_create(None,sample,event);assert lib.lifeos_voice_audio_start(obj)==1;lib.lifeos_voice_audio_destroy(obj)
 H=ctypes.CFUNCTYPE(I,P,I,P,I);http=H(lambda *a:0)
 lib.lifeos_voice_http_create.argtypes=[P,H,I];lib.lifeos_voice_http_create.restype=P
 lib.lifeos_voice_http_start.argtypes=[P,P,I,P,I,I];lib.lifeos_voice_http_start.restype=I
 lib.lifeos_voice_http_destroy.argtypes=[P]
 obj=lib.lifeos_voice_http_create(None,http,1);body=ctypes.create_string_buffer(b'{}');key=ctypes.create_string_buffer(b'SYNTHETIC-NOT-A-KEY');assert lib.lifeos_voice_http_start(obj,body,2,key,19,1)==1;lib.lifeos_voice_http_destroy(obj)
 results.append({'name':'native-A-device-and-network-denial','exit':0})
report={'run':run,'status':'pass' if all(x['exit']==0 for x in results) else 'fail','scope':'offline technical subset; not A acceptance or production integration','checks':results,'inherited_unchanged':182,'actual_posts':{'ASR':0,'TTS':0,'DeepSeek':0},'real_microphone_opened':False,'real_speaker_opened':False}
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');(root/'evidence/latest-run.json').write_text(json.dumps({'path':str(out/'result.json'),'sha256':h(out/'result.json')},indent=2)+'\n')
print(json.dumps(report,indent=2));sys.exit(0 if report['status']=='pass' else 1)
