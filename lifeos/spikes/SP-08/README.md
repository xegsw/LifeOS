# SP-08 证据包入口

## 结论

本目录是 `LIFEOS-P2-008` 的确定性合成证据包。验证范围为 48 条内容单元、4 个 Project、人可读目录、JSON manifest、Markdown 内容、SHA-256 校验、引用闭包、5 类破损包、空环境与已有环境重导入。结果以 `results.json` 和 `test_matrix.csv` 为准。

本证据只证明非冻结候选机制在 Python 标准库、单进程、本地合成数据中成立；不证明正式格式、跨版本完全还原、真实附件、加密、生产备份 / 灾备 SLA、真实云 / 第三方能力、容量或技术架构。

## 一条命令复跑

```bash
python3 lifeos/spikes/SP-08/run_spike.py
```

脚本只重建 `lifeos/spikes/SP-08/` 下的 `sample_export/`、`broken_package_cases/`、`raw_logs/` 和机器报告，不读取网络、真实 Vault、用户文档、凭据、模型、云或第三方服务。

## 证据索引

- `SP-08_report.md`、`results.json`、`test_matrix.csv`：结论、机器摘要和逐项断言。
- `run_spike.py`：合成夹具、导出器、校验器、故障注入与重导入候选实现。
- `fixtures.md`：48 条夹具覆盖与特殊状态。
- `export_format_candidate.md`：目录、manifest、checksum 和导入合同。
- `sample_export/`：可由通用文本 / JSON 工具读取的样例包。
- `validation_report.json`：基线与 5 类破损包校验结果。
- `reimport_results.json`：空环境、重复、已有原文、冲突和旧代导入结果。
- `broken_package_cases/`：篡改、缺文件、断引用、不兼容版本、缺 restriction 说明，另含冲突版本样例。
- `permission_and_license_report.md`：数据主权与外部再分发许可边界。
- `rebuildable_artifacts_report.md`：FTS / 向量 / 缓存 / 重排特征的排除与重建前置。
- `failed_cases.md`：失败样例与用户可理解语言。
- `raw_logs/`：只含结果码、计数和作用域化引用的日志。
- `environment.md`、`cleanup.md`：环境与精确清理说明。

