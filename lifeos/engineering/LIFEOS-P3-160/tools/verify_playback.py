#!/usr/bin/env python3
"""Native playback accounting: device-free Swift tests, compile-only real branch, A-denial FFI."""
import pathlib,subprocess,os,json,datetime
r=pathlib.Path(__file__).resolve().parents[1];t=pathlib.Path('/private/tmp/lifeos-p3-160-voice-v1');n=t/'native';src=r/'candidate/src/voice/native';stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S');out=r/'evidence'/('native-playback-'+stamp);out.mkdir();steps=[]
def run(name,args,env=None):
 x=subprocess.run(list(map(str,args)),capture_output=True,text=True,env=env,timeout=120);(out/(name+'.log')).write_text(x.stdout+x.stderr);steps.append({'name':name,'exit':x.returncode});print(name,x.returncode,flush=True);assert x.returncode==0
run('ledger-build',['/usr/bin/swiftc',src/'PlaybackLedger.swift',r/'tools/test_playback_ledger.swift','-o',n/'test-playback-ledger'])
run('ledger-fake',[n/'test-playback-ledger'])
run('swift-build',['/usr/bin/swiftc','-emit-library','-module-name','LifeOSVoice','-o',n/'libLifeOSVoice.dylib',src/'PlaybackLedger.swift',src/'AudioEngine.swift',src/'MiMoHTTP.swift'])
run('real-typecheck',['/usr/bin/swiftc','-D','LIFEOS_VOICE_REAL','-typecheck',src/'PlaybackLedger.swift',src/'AudioEngine.swift',src/'MiMoHTTP.swift'])
lib=t/'dependencies/sherpa-onnx-v1.13.7-osx-arm64-shared-no-tts-lib/lib';env=dict(os.environ,CARGO_TARGET_DIR=str(t/'native-rust-target'),RUSTFLAGS=f'-L native={n} -l dylib=LifeOSVoice -l dylib=LifeOSDetector -C link-arg=-Wl,-rpath,{n} -C link-arg=-Wl,-rpath,{lib}')
run('rust-native-tests',['/Users/xxe/.cargo/bin/cargo','test','--offline','--locked','--features','voice-native-tests','--manifest-path',r/'tools/rust-tests/Cargo.toml','native::tests'],env)
mutants=[('capacity','samples <= Self.capacity - queued','samples <= Self.capacity'),('stale-seal','guard expected == generation, !sealed, accepted > 0','guard !sealed, accepted > 0'),('premature-drain','guard sealed, !drained, pending.isEmpty','guard !drained, pending.isEmpty')];mutation_results=[]
work=t/('playback-mutations-'+stamp);work.mkdir()
for name,old,new in mutants:
 s=(src/'PlaybackLedger.swift').read_text();assert s.count(old)==1;p=work/(name+'.swift');p.write_text(s.replace(old,new));binary=work/name
 run('mutation-build-'+name,['/usr/bin/swiftc',p,r/'tools/test_playback_ledger.swift','-o',binary])
 # Python resets inherited signals; Swift precondition failure is the expected kill.
 x=subprocess.run([str(binary)],capture_output=True,text=True,timeout=10);log=x.stdout+x.stderr;(out/('mutation-'+name+'.log')).write_text(log);killed=x.returncode!=0 and 'Precondition failed' in log;mutation_results.append({'name':name,'exit':x.returncode,'killed_by_precondition':killed});assert killed
(out/'result.json').write_text(json.dumps({'steps':steps,'mutations':mutation_results,'device_starts':0,'actual_playback':0,'POST':0,'scope':'native ledger pure fake, native A-denial and callback fake, real compile only'},indent=2)+'\n');print(out/'result.json')
