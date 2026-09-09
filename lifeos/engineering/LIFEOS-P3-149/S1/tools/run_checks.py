"""S1 impact-scoped offline rerun; no GUI, no cleanup, preserve earlier logs."""
from pathlib import Path
import os,subprocess,datetime
s=Path(__file__).resolve().parents[1];c=s/'candidate';root=Path('/private/tmp/lifeos-p3-149-health-source-v1');env={**os.environ,'LIFEOS_P3_149_BUILD_PROFILE':'engineering','CARGO_TARGET_DIR':str(root/'target'),'TMPDIR':str(root/'tmp')};node='/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';cargo='/Users/xxe/.cargo/bin/cargo'
subprocess.run(['python3','-B',str(c/'tools/task_root.py'),'verify'],env=env,check=True)
log=s/'evidence'/('rerun-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.log')
with log.open('x') as out:
 for cmd in [[cargo,'test','--locked','--offline','--manifest-path',str(c/'Cargo.toml'),'health','--','--test-threads=1'],[node,'--test',str(c/'tools/test_e04_flow.mjs'),str(c/'tools/test_health_ui.mjs'),str(c/'tools/test_snapshot_ui.mjs')]]:subprocess.run(cmd,env=env,stdout=out,stderr=out,check=True)
print(log)
