# LIFEOS-P2-014 证据入口

本目录是 FTS 维护隔离窄测的可复核证据包。它只使用确定性合成文本与合成标识，不读取真实用户数据、真实 Vault、真实路径或外部服务；其中代码为可丢弃验证 harness，不是产品实现，也不冻结 SQLite Schema、FTS 表结构、PRAGMA、调度、API、性能 SLA 或技术架构。

## 复跑命令

快速回归（10 万内容单元 / 30 万分块）：

```bash
python3 lifeos/spikes/P2-014-fts-maintenance-isolation/run_spike.py --tiers 100000
```

完整主档（10 万 / 30 万 + 100 万 / 300 万）：

```bash
python3 lifeos/spikes/P2-014-fts-maintenance-isolation/run_spike.py --tiers 100000,1000000
```

加 `--keep-work` 可保留可删除工作库用于抽查；默认只保留轻量证据。脚本任一 P0 断言失败时返回非零。

## 验证模型

- `authority.db`：唯一权威内容与保存回执；WAL + FULL，同一短事务提交后才确认保存。
- `index-gN.db`：可重建 FTS 派生库；全量维护在独立影子文件进行，不持有权威库写锁。
- `registry.db`：校验成功后以短事务 CAS 切换 generation；低 generation 不能覆盖高 generation。
- 查询先取 posting 候选，再回连权威库重检 active、permission、tombstone 与 restriction generation；陈旧 posting 不直接成为结果。
- ENOSPC、重建中断、校验失败均注入影子文件；合法旧索引和权威库保持可用。

## 证据索引

- `run_spike.py`：确定性验证脚本。
- `evidence/results.json`：完整机器可读结果、延迟分布、故障与断言。
- `evidence/execution_summary.json`：运行摘要。
- `evidence/test_matrix.csv`：逐档 P0 断言矩阵。
- `evidence/privacy_scan.json`：证据隐私扫描。
- `environment.md`：环境与解释边界。
- `fixtures.md`：合成数据说明。
- `failure_samples.md`：故障注入与回退摘要。

## 结论边界

该 harness 验证“物理分离的派生索引维护不会以长事务阻塞权威捕获”以及 fail-closed 查询回连模式。它不证明 UI 端到端 SLA、跨平台表现、崩溃瞬间文件系统原子性、生产调度、真实长文/附件、真实 Vault 或正式 Schema；也不自动关闭风险、冻结技术架构或准入 MVP 开发，结论须由 PM 验收。
