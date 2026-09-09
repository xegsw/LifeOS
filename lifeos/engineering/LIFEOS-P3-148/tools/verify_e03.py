"""E03 compile and pure mode checks; never probes or initializes review root."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys

BASE = Path(__file__).resolve().parents[1]
CANDIDATE = BASE / 'candidate'
assert os.environ.get('LIFEOS_P3_148_BUILD_PROFILE') == 'engineering'
sys.path.insert(0, str(CANDIDATE / 'tools'))
from task_root import ROOT, verify
verify()  # Engineering root only; all caches stay here.
OUT = BASE / 'evidence'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
rows = []
cargo = '/Users/xxe/.cargo/bin/cargo'
binary = ROOT / 'target/debug/lifeos-p3-148'
for profile in ['independent-review', 'engineering']:
    env = dict(os.environ, LIFEOS_P3_148_BUILD_PROFILE=profile,
               CARGO_TARGET_DIR=str(ROOT / 'target'), TMPDIR=str(ROOT / 'tmp'))
    for name, args in [
        ('build', ['build']),
        ('pure-tests', ['test', 'p148_e03_', '--', '--test-threads=1']),
        ('transport-mode', ['test', 'p148_runtime_env_cannot_enable_transport', '--', '--test-threads=1']),
    ]:
        cmd = [cargo, args[0], '--locked', '--offline', '--manifest-path', str(CANDIDATE / 'Cargo.toml')] + args[1:]
        log = OUT / f'e03-{stamp}-{profile}-{name}.log'
        assert not log.exists()
        with log.open('w') as f:
            result = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        rows.append(dict(profile=profile, step=name, exit_code=result.returncode, log=log.name))
        if result.returncode:
            raise SystemExit(f'failed: {log}')
    # --profile-info returns pure compiled constants before any root verification or GUI.
    expected = json.loads((CANDIDATE / 'root_profiles.json').read_text())[profile]['root']
    info = subprocess.run([str(binary), '--profile-info'], env=env, capture_output=True, text=True)
    assert info.returncode == 0 and json.loads(info.stdout) == {'profile': profile, 'root': expected}
    cases = [('LIFEOS_P3_148_BUILD_PROFILE', 'unknown'),
             ('LIFEOS_P3_148_BUILD_PROFILE', 'engineering' if profile == 'independent-review' else 'independent-review'),
             ('LIFEOS_P3_148_BUILD_PROFILE', 'source-pilot-1'),
             ('LIFEOS_P3_148_PROFILE', 'real')]
    cases += [(key, '/arbitrary/root') for key in ['LIFEOS_RUNTIME_ROOT', 'LIFEOS_P3_145_ROOT_PROFILE', 'LIFEOS_P3_148_ROOT', 'LIFEOS_P3_148_ROOT_PROFILE']]
    for key, value in cases:
        r = subprocess.run([str(binary), '--profile-info'], env=dict(env, **{key: value}), capture_output=True, text=True)
        assert r.returncode == 2 and r.stderr.strip() == 'profile_rejected'
    rows.append(dict(profile=profile, step='pure-profile-info', overrides_rejected=len(cases),
                     binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                     runtime_root_contact=False, gui_launched=False))
result = dict(task='LIFEOS-P3-148', status='pass', checks=rows,
              cache_scope='engineering root only', review_root_contact=False,
              review_app_launched=False, independent_pass=False)
path = OUT / f'e03-{stamp}-result.json'
path.write_text(json.dumps(result, indent=2))
print(json.dumps({'status': 'pass', 'result': str(path), 'review_root_contact': False}))
