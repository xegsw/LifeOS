# Attempt-8 PM 复跑

提交 runner：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/scripts/run_attempt_8.py --evidence-dir lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8
```

PM Schema 反例：

```bash
python3 -B lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/pm_schema_constraint_counterexamples.py --source lifeos/engineering/LIFEOS-P3-094/src/local_capture.py --output lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/pm_schema_constraint_counterexamples.json
```

两条命令仅使用项目文件与新建 `/private/tmp` 固定非敏感夹具。runner 会重建指定 PM Evidence 目录，因此如需保全当前 PM 反例和 Manifest，应改用新的空目录复跑提交 runner，不得覆盖本目录。
