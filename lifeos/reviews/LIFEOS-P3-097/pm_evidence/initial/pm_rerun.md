# LIFEOS-P3-097 PM Rerun

提交 runner：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py --output /private/tmp/lifeos-p3-097-pm-review-initial
python3 -B lifeos/engineering/LIFEOS-P3-097/scripts/run_p3_097.py --verify-only /private/tmp/lifeos-p3-097-pm-review-initial
```

PM 外置反例：

```bash
python3 -B lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/pm_boundary_counterexamples.py --output lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/pm_boundary_counterexamples.json
```

预期：提交 runner 和 verify-only 退出 0；PM 反例 `pass_count=9`、`fail_count=0`。所有命令离线运行，仅使用新建固定非敏感夹具。
