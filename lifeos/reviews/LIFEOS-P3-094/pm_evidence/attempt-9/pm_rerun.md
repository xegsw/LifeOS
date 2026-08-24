# P3-094 Final Invariant Closure PM 复跑

提交 runner 应复跑到新的空目录，避免覆盖当前 PM 反例：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-9/scripts/run_attempt_9.py --evidence-dir /private/tmp/lifeos-p3-094-attempt-9-review-evidence
```

PM 反例：

```bash
python3 -B lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.py --source lifeos/engineering/LIFEOS-P3-094/src/local_capture.py --tests lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py --output /private/tmp/lifeos-p3-094-attempt-9-pm-counterexamples.json
```

复核后精确删除上述两个 `/private/tmp` 路径。
