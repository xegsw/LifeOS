"""P3-159 offline entry. Never opens real stores, credentials, network, or GUI."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, datetime

base = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--offline', action='store_true', required=True)
args = parser.parse_args()

def tree(root):
    rows = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise RuntimeError('symlink in candidate identity')
        if p.is_file():
            rows[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return rows

identity = json.loads((base/'baseline/identity.json').read_text())
baseline = tree(base/'baseline/candidate')
if baseline != identity['sourceFiles']:
    raise RuntimeError('approved baseline differs')
before = tree(base/'candidate')
run = subprocess.run([sys.executable, str(base/'tools/run_v8_checks.py')], check=False)
after = tree(base/'candidate')
delta = {'added': sorted(after.keys()-baseline.keys()),
         'removed': sorted(baseline.keys()-after.keys()),
         'changed': sorted(p for p in after.keys() & baseline.keys() if after[p] != baseline[p])}
receipt = {'task':'P3-159','mode':'offline','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'exitCode':run.returncode if before==after else 1,'sourceStableDuringRun':before==after,'baselineFiles':len(baseline),'baselineMatched':True,
           'sourceBefore':before,'sourceAfter':after,'delta':delta,
           'scope':'deterministic engineering only; B/C and actual GUI remain separate gates'}
(base/'evidence/offline-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(receipt['exitCode'])
