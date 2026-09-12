"""Task-local CI entry: contracts, build, and newly authorized ordinary synthetic checks only."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys
from verify_design_contract import run as contracts
BASE=Path(__file__).resolve().parents[1];C=BASE/'candidate';ROOT=Path('/private/tmp/lifeos-p3-148-source-ai-v1')
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['contracts','build','storage','credentials_mock','transport_mock','restart','all'],required=True);args=parser.parse_args()
assert os.environ.get('LIFEOS_P3_148_BUILD_PROFILE')=='engineering'
contracts()
if args.phase=='contracts':print(json.dumps(contracts()));sys.exit(0)
sys.path.insert(0,str(C/'tools'));from task_root import verify
verify()
env={**os.environ,'CARGO_TARGET_DIR':str(ROOT/'target'),'TMPDIR':str(ROOT/'tmp'),'PYTHONDONTWRITEBYTECODE':'1'}
cargo=['/Users/xxe/.cargo/bin/cargo'];manifest=['--locked','--offline','--manifest-path',str(C/'Cargo.toml')]
phases={
 'build':[['/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node',str(C/'tools/build_ui.mjs')],cargo+['build']+manifest],
 'storage':[cargo+['test']+manifest+['conversation_store::p148_tests','--','--test-threads=1']],
 'credentials_mock':[cargo+['test']+manifest+['provider_store::p148_tests','--','--test-threads=1'],cargo+['test']+manifest+['provider_store::lifecycle_mock','--','--test-threads=1'],cargo+['test']+manifest+['p148_memory_port_checks','--','--test-threads=1']],
 'transport_mock':[cargo+['test']+manifest+['p148_transport_checks','--','--test-threads=1'],cargo+['test']+manifest+['ipc_boundary::tests','--','--test-threads=1'],cargo+['test']+manifest+['strict_json::boundary_tests','--','--test-threads=1']],
 'restart':[[sys.executable,'-B',str(C/'tools/test_source_conversation.py')],[sys.executable,'-B',str(C/'tools/test_conversation_extended.py')],['/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node',str(C/'tools/test_legacy_functional.mjs')]]}
results=[];stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
for phase in (list(phases) if args.phase=='all' else [args.phase]):
 for i,command in enumerate(phases[phase]):
  log=BASE/'evidence'/f'ci-{stamp}-{phase}-{i}.log'
  with log.open('x') as f:r=subprocess.run(command,env=env,stdout=f,stderr=subprocess.STDOUT)
  results.append({'phase':phase,'exit_code':r.returncode,'log':log.name})
  if r.returncode:print(json.dumps(results));sys.exit(r.returncode)
print(json.dumps({'scope':'synthetic_only','results':results},indent=2))
