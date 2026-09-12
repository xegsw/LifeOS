#!/usr/bin/env python3
import pathlib,subprocess,shutil,json,os,datetime
r=pathlib.Path(__file__).resolve().parents[1];stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S');t=pathlib.Path('/private/tmp/lifeos-p3-160-voice-v1')/('mutations-'+stamp);t.mkdir()
mutations=[('stale-playback','audio.rs','!self.active || g != self.generation','!self.active'),('budget-no-persist','budget.rs','store.compare_save(rev, l)','Ok(())'),('revoke-in-flight','gateway.rs','auth.check(&r.binding, r.purpose)?;','/* mutation: revoked response accepted */')]
result=[]
for name,file,old,new in mutations:
 p=t/name;p.mkdir();shutil.copytree(r/'candidate/src/voice',p/'src');s=(p/'src'/file).read_text();assert s.count(old)==1;(p/'src'/file).write_text(s.replace(old,new));manifest=(r/'tools/rust-tests/Cargo.toml').read_text().replace('../../candidate/src/voice/mod.rs','src/mod.rs');(p/'Cargo.toml').write_text(manifest);shutil.copyfile(r/'tools/rust-tests/Cargo.lock',p/'Cargo.lock')
 env=dict(os.environ,CARGO_TARGET_DIR=str(t/'target'));x=subprocess.run(['/Users/xxe/.cargo/bin/cargo','test','--offline','--locked','--manifest-path',str(p/'Cargo.toml')],capture_output=True,text=True,env=env,timeout=120);log=x.stdout+x.stderr;(r/'evidence'/('mutation-'+stamp+'-'+name+'.log')).write_text(log);killed=x.returncode!=0 and 'test result: FAILED' in log;result.append({'name':name,'exit':x.returncode,'killed_by_assertion':killed})
(r/'evidence'/('mutations-'+stamp+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert all(x['killed_by_assertion'] for x in result)
