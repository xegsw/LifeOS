#!/usr/bin/env python3
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/"evidence/rework-1"; TARGET=ROOT/"target"; CARGO="/Users/xxe/.cargo/bin/cargo"
PAT=re.compile(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+")
def residual(): return sorted(str(p) for p in Path('/private/tmp').iterdir() if PAT.fullmatch(p.name))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,cmd):
 env=os.environ.copy(); env['CARGO_NET_OFFLINE']='true'; c=subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); log=OUT/f'{name}.log'; log.write_text(c.stdout)
 return {'id':name,'command':cmd,'returncode':c.returncode,'log':str(log.relative_to(ROOT)),'sha256':sha(log),'status':'PASS' if c.returncode==0 else 'FAIL'}
before=residual(); existed=TARGET.exists()
if existed: shutil.rmtree(TARGET)
absent=not TARGET.exists(); rows=[run('cargo_test',[CARGO,'test','--locked']),run('cargo_build',[CARGO,'build','--locked']),run('cargo_tauri_bundle',[CARGO,'tauri','build','--debug','--bundles','app','--no-sign','--config','{"bundle":{"active":true,"targets":["app"]}}','--','--locked'])]; after=residual()
binary=ROOT/'target/debug/lifeos-p3-104'; bundle=ROOT/'target/debug/bundle/macos/LifeOS P3-104.app/Contents/MacOS/lifeos-p3-104'
d={'task':'LIFEOS-P3-106','execution':'rework-1','network_mode':'CARGO_NET_OFFLINE=true','target_existed_before_authorized_clean':existed,'target_absent_before_build':absent,'unit_paths_before':before,'unit_paths_after':after,'commands':rows,'artifacts':{'source_main_sha256':sha(ROOT/'src/main.rs'),'source_runtime_sha256':sha(ROOT/'src/runtime.rs'),'cargo_lock_sha256':sha(ROOT/'Cargo.lock'),'binary':str(binary.relative_to(ROOT)),'binary_sha256':sha(binary) if binary.is_file() else None,'bundle_binary':str(bundle.relative_to(ROOT)),'bundle_binary_sha256':sha(bundle) if bundle.is_file() else None}}
d['status']='PASS' if absent and not before and not after and all(x['status']=='PASS' for x in rows) and binary.is_file() and bundle.is_file() else 'FAIL'; (OUT/'clean_build_results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':d['status'],'commands':[(x['id'],x['returncode']) for x in rows]})); raise SystemExit(0 if d['status']=='PASS' else 1)
