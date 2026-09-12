#!/usr/bin/env python3
import pathlib,subprocess,os,json,datetime
r=pathlib.Path(__file__).resolve().parents[1];t=pathlib.Path('/private/tmp/lifeos-p3-160-voice-v1');lib=t/'dependencies/sherpa-onnx-v1.13.7-osx-arm64-shared-no-tts-lib/lib';n=t/'native';stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S');out=r/'evidence'/('native-'+stamp);out.mkdir();steps=[]
def run(name,cmd,env=None):
 x=subprocess.run([str(a) for a in cmd],capture_output=True,text=True,env=env,timeout=120);(out/(name+'.log')).write_text(x.stdout+x.stderr);steps.append({'name':name,'exit':x.returncode});print(name,x.returncode,flush=True);assert x.returncode==0
run('assets',['/usr/bin/python3',r/'tools/prepare_voice_assets.py'])
run('swift',['/usr/bin/swiftc','-emit-library','-module-name','LifeOSVoice','-o',n/'libLifeOSVoice.dylib',r/'candidate/src/voice/native/PlaybackLedger.swift',r/'candidate/src/voice/native/AudioEngine.swift',r/'candidate/src/voice/native/MiMoHTTP.swift'])
run('swift-real-typecheck',['/usr/bin/swiftc','-D','LIFEOS_VOICE_REAL','-typecheck',r/'candidate/src/voice/native/PlaybackLedger.swift',r/'candidate/src/voice/native/AudioEngine.swift',r/'candidate/src/voice/native/MiMoHTTP.swift'])
run('sherpa',['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-fPIC','-c',r/'candidate/src/voice/native/sherpa_adapter.c','-I',r/'inputs/sherpa-1.13.7','-o',n/'sherpa_adapter.o'])
run('sherpa-link',['/usr/bin/clang','-dynamiclib',n/'sherpa_adapter.o','-L',lib,'-lsherpa-onnx-c-api','-o',n/'libLifeOSDetector.dylib'])
env=dict(os.environ,CARGO_TARGET_DIR=str(t/'native-rust-target'),RUSTFLAGS=f'-L native={n} -l dylib=LifeOSVoice -l dylib=LifeOSDetector -C link-arg=-Wl,-rpath,{n} -C link-arg=-Wl,-rpath,{lib}')
run('rust-ffi-denial',['/Users/xxe/.cargo/bin/cargo','test','--offline','--locked','--features','voice-native-tests','--manifest-path',r/'tools/rust-tests/Cargo.toml','native::tests'],env)
run('detector-build',['/usr/bin/clang',r/'tools/test_detector.c',n/'sherpa_adapter.o','-I',r/'inputs/sherpa-1.13.7','-L',lib,'-lsherpa-onnx-c-api',f'-Wl,-rpath,{lib}','-o',n/'test-detector'])
k=t/'models/kws';run('real-model-negative',[n/'test-detector',k/'encoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx',k/'decoder-epoch-12-avg-2-chunk-16-left-64.onnx',k/'joiner-epoch-12-avg-2-chunk-16-left-64.int8.onnx',k/'tokens.txt',t/'models/silero-v5.1.onnx'])
(out/'result.json').write_text(json.dumps({'steps':steps,'POST':0,'microphone':False,'speaker':False,'scope':'native compile/link/A-denial and real model synthetic negative only'},indent=2)+'\n');print(str(out/'result.json'))
