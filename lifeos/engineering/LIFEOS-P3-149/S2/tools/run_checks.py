# coding: utf-8
"""S2 impact-scoped deterministic rerun. No GUI, no cleanup, no network."""
from pathlib import Path
import os,subprocess,datetime
s=Path(__file__).resolve().parents[1];c=s/'candidate';root=Path('/private/tmp/lifeos-p3-149-health-source-v1/S2')
env={**os.environ,'LIFEOS_P3_149_BUILD_PROFILE':'engineering','CARGO_TARGET_DIR':str(root/'target'),'TMPDIR':str(root/'tmp')}
subprocess.run(['/usr/bin/python3','-B',str(c/'tools/task_root.py'),'verify'],env=env,check=True)
log=s/'evidence'/('rerun-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.log')
cargo='/Users/xxe/.cargo/bin/cargo'
commands=[['/usr/bin/python3','-B',str(s/'tools/test_parser.py')],[cargo,'test','--locked','--offline','--manifest-path',str(c/'Cargo.toml'),'health','--','--test-threads=1'],[cargo,'test','--locked','--offline','--manifest-path',str(c/'Cargo.toml'),'p149_apple_import','--','--test-threads=1']]
node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
commands.append([node,'--test',*[str(c/'tools'/n) for n in ['test_e04_flow.mjs','test_health_ui.mjs','test_snapshot_ui.mjs','test_apple_ui.mjs']]])
with log.open('x') as out:
 for cmd in commands:
  subprocess.run(cmd,env=env,stdout=out,stderr=out,check=True)
print(log)
