# LIFEOS-P3-096 Rework 1 PM rerun

Submitted runner with PM output separated from Engineering Evidence:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/engineering/LIFEOS-P3-096/scripts/run_p3_096.py --evidence-dir /private/tmp/pm-lifeos-p3-096-r1-XXXXXX/submitted-runner-evidence
```

Initial PM counterexample rerun:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/reviews/LIFEOS-P3-096/pm_evidence/initial/pm_post_commit_close_counterexample.py --source lifeos/engineering/LIFEOS-P3-096/src/local_capture.py --output /private/tmp/pm-lifeos-p3-096-r1-XXXXXX/initial-counterexample-rerun.json
```

Remaining completion-point counterexample:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/pm_post_commit_sidecar_counterexample.py --source lifeos/engineering/LIFEOS-P3-096/src/local_capture.py --output lifeos/reviews/LIFEOS-P3-096/pm_evidence/rework-1/pm_post_commit_sidecar_counterexample.json
```

The remaining counterexample intentionally exits non-zero when it reproduces the P1.
