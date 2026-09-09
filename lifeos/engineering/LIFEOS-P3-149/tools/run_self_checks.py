"""Repeat deterministic synthetic checks without deleting history or launching GUI."""
from pathlib import Path
import os,subprocess,datetime
base=Path(__file__).resolve().parents[1];candidate=base/'candidate';root=Path('/private/tmp/lifeos-p3-149-health-source-v1')
env={**os.environ,'LIFEOS_P3_149_BUILD_PROFILE':'engineering','CARGO_TARGET_DIR':str(root/'target'),'TMPDIR':str(root/'tmp')}
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo'
subprocess.run(['python3','-B',str(candidate/'tools/task_root.py'),'init'],env=env,check=True)
log=base/'evidence'/('rerun-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.log')
with log.open('x') as out:
 for source,name in [('tests/create_alias.swift','create_test_alias'),('tools/alias_metadata.swift','alias_metadata')]:subprocess.run(['swiftc',str(candidate/source),'-o',str(root/name)],env=env,stdout=out,stderr=out,check=True)
 for command in [[node,str(candidate/'tools/build_ui.mjs')],[cargo,'test','--locked','--offline','--manifest-path',str(candidate/'Cargo.toml'),'--','--test-threads=1'],[node,'--test',str(candidate/'tools/test_e04_flow.mjs'),str(candidate/'tools/test_health_ui.mjs')]]:
  subprocess.run(command,env=env,stdout=out,stderr=out,check=True)
print(log)
