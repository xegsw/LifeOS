# SP-07 证据包入口

## 结论

本目录是 `LIFEOS-P2-007` 的可重复合成证据包。`python3 run_spike.py` 在 Python 3 标准库、SQLite FTS5、内存数据库和 deterministic semantic stub 范围内完成 60 条内容单元、4 个 Project、20 条标注查询与 23 项断言。当前结果为 23/23 PASS、P0 失败 0、权限泄漏 0、证据完整性 100%。

该结论不代表真实数据、真实 Vault、真实 embedding、pgvector、ANN、生产容量或 SLA 已通过；不冻结 Schema、API、排序、分块、模型或技术架构。

## 复跑

```bash
python3 lifeos/spikes/SP-07/run_spike.py
```

脚本只覆盖本目录内机器生成的文件，不连接网络、模型、云、第三方或真实 Vault。

## 文件索引

- `run_spike.py`：合成语料、FTS5、元数据/权限过滤、轻量重排、semantic stub、恢复包、候选建议与断言。
- `results.json`：机器总结果。
- `corpus.json`：60 条合成内容单元。
- `query_set.json` / `golden_labels.json`：20 条查询及标注。
- `retrieval_results.json`：FTS-only、semantic-only、hybrid 的逐查询结果、指标与延迟。
- `test_matrix.csv`：23 项断言。
- `recovery_package_samples.json`：4 个 Project 恢复包与候选下一步。
- `permission_filter_report.md`：授权、墓碑、撤回、断源、旧代与跨用途过滤证据。
- `evidence_integrity_report.md`：结果、恢复包与候选建议的证据字段完整性。
- `failed_queries.md`：空结果与降级状态样例。
- `fixtures.md`：夹具范围与最小状态模型。
- `SP-07_report.md`：证据摘要。
- `audit_log.json`：不含正文、路径、prompt 或向量的最小审计样例。
- `environment.md` / `cleanup.md`：环境边界与精确清理说明。

