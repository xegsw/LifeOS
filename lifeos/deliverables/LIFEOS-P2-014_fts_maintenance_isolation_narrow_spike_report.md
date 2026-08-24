# LIFEOS-P2-014｜FTS 维护隔离窄测报告

## 1. 执行摘要

1. **[实测]** 已完成 10 万内容单元 / 30 万分块快速档与 100 万 / 300 万主档；两档全部 11 项机器可读 P0 断言通过，整轮 `PASS`。
2. **[实测]** 主档三类维护并发期间完成 5,686 次权威捕获，合并 p50 / p95 / p99 / 最大等待为 0.140 / 0.843 / 0.917 / 2.952 ms，低于 1 秒门槛，失败 0。
3. **[实测]** 50 次提交失败注入的成功回执、残留权威行、保存回执和误报保存均为 0；权限、tombstone、restriction generation 泄漏均为 0。
4. **[实测]** 新 generation 仅在校验通过后切换；校验失败、模拟 ENOSPC、重建中断均未破坏权威库或当前合法索引，迟到低 generation 无法覆盖高 generation。
5. **[结论]** 本任务判定 **`Pass`**。证据支持 PM 验收后关闭 R-0039，但不自动冻结技术架构或准入 Stage 3 / MVP 开发。

## 2. 环境与合成数据

**[实测]** 环境为 macOS 26.5.2 arm64、Python 3.9.6、SQLite 3.51.0 + FTS5；完整运行 29.021 秒。seed 为 `20260809`，每个合成单元生成 3 个分块。未使用网络、真实数据、真实 Vault、模型、云或第三方服务。

**[方案]** harness 将权威数据、FTS 派生、当前 generation 分置于独立 SQLite 文件。权威库使用 WAL、`synchronous=FULL` 与短事务；长维护不取得权威写锁。该布局不冻结实现。

## 3. 验证方案与证据入口

证据入口：`lifeos/spikes/P2-014-fts-maintenance-isolation/README.md`。

- `run_spike.py`：确定性脚本，任一 P0 失败返回非零。
- `evidence/results.json`：完整环境、延迟、故障、切换与断言；`execution_summary.json` 为摘要。
- `evidence/test_matrix.csv`：逐档矩阵；`privacy_scan.json` 为隐私扫描。
- `fixtures.md`、`environment.md`、`failure_samples.md`：夹具与解释边界。

最终复跑命令：

```bash
python3 lifeos/spikes/P2-014-fts-maintenance-isolation/run_spike.py --tiers 100000,1000000
```

默认清理可重建工作库；最终工作目录已移除。

## 4. P0 断言结果矩阵

| P0 断言 | 快速档 | 主档 |
|---|---:|---:|
| 捕获不等待长索引事务；最大等待 ≤1 秒 | Pass（1.665 ms） | Pass（2.952 ms） |
| 误报保存数为 0 | 0 | 0 |
| 权限 / tombstone / restriction generation 泄漏 | 0 / 0 / 0 | 0 / 0 / 0 |
| 校验后才切换；失败保留合法索引 | Pass | Pass |
| ENOSPC / 中断不损坏权威或合法索引 | Pass | Pass |
| 旧任务 / 旧 generation 不覆盖高 generation | Pass | Pass |

两档 22 个断言均 PASS，P0 失败数 0。

## 5. 捕获、维护、切换与回退

| 档位 / 场景 | 样本 | p50 | p95 | p99 | 最大 | 失败 |
|---|---:|---:|---:|---:|---:|---:|
| 10 万：合并 | 660 | 0.405 ms | 0.857 ms | 0.978 ms | 1.665 ms | 0 |
| 100 万：合并 | 5,686 | 0.140 ms | 0.843 ms | 0.917 ms | 2.952 ms | 0 |
| 100 万：增量维护 | 150 | 0.534 ms | 0.841 ms | 0.888 ms | 1.868 ms | 0 |
| 100 万：影子重建 | 3,974 | 0.120 ms | 0.545 ms | 0.858 ms | 2.952 ms | 0 |
| 100 万：索引校验 | 1,562 | 0.734 ms | 0.881 ms | 0.952 ms | 2.118 ms | 0 |

**[实测]** 主档 300 万 posting 影子构建 6.109 秒，校验 4.699 秒；期间捕获持续可用。generation 2 只有在 generation、期望/实际分块数、状态、摘要和 FTS integrity 均通过后，才以短事务 CAS 从 generation 1 切换。校验失败的 generation 3 未激活；迟到 generation 1 CAS 失败。

**[推断]** 对比 SP-09 同库 rebuild 约 4 秒等待，核心成因是长维护与权威写锁耦合；保持两者不共享写锁即可关闭该成因，不要求照搬三文件模型。

## 6. 泄漏、误报、损坏与隐私

**[实测]** 每档 25 次权威提交前失败均回滚：确认成功、权威行、保存回执、误报均为 0。“已保存”只由权威内容与回执同一耐久事务决定，索引状态不参与。

posting 建成后分别执行权限拒绝、tombstone 与 restriction generation 推进。查询候选回连当前权威状态，只接受 active、allowed、无 tombstone 且 posting generation 等于当前 generation 的内容，三类泄漏均为 0。

模拟 ENOSPC、中断、校验失败后，权威库和合法索引 integrity 均为 `ok`；故障后捕获成功。结构化证据隐私扫描命中 0。

## 7. 最终判定

**`Pass`。** 全部 P0 安全与保存真实性断言通过；主档达到 100 万 / 300 万；最大等待 2.952 ms；误报和三类泄漏为 0；校验切换、失败保留合法索引、故障完整性与 generation fencing 均有可复跑证据。

**[建议｜需 PM 确认]** PM 可验收本任务并关闭 R-0039；专项会话不直接修改 `RISK_LOG.md`。

## 8. 可冻结输入、不可外推与降级

可作为冻结输入的责任边界：

- “已保存”只由权威耐久提交决定；索引成功或排队不得冒充保存。
- FTS 为可重建派生；长维护不得共享权威捕获的长写锁。
- posting 只是候选，消费前须重检当前权限、active、tombstone、generation、Source / ArtifactVersion。
- 新 generation 校验后才切换；旧任务须 fencing；失败影子不得污染合法索引。

**[不可外推]** 不冻结数据库/FTS Schema、FTS5、PRAGMA、文件数、worker、队列、调度、分块、API、容量或 SLA；不证明跨平台、真实长文/附件、冷缓存、多进程、断电瞬间一致性或 UI 端到端时延。模拟 ENOSPC 验证故障边界，不是实际填满用户磁盘的专项测试。

**[建议]** 若正式实现不能保持隔离，应禁用在线全量 rebuild，降级为增量、可中断分块、维护窗口或已校验旧索引；不得关闭耐久、权限过滤或 tombstone/generation 门控，也不得先显示已保存再补写。

## 9. 角色、关卡与待确认事项

- **技术架构负责人：Pass。** 主档、实测与边界清楚；支持关闭 R-0039。
- **数据 / 领域模型负责人：Gate 2 Pass（窄测语义层）。** 权威、Source、ArtifactVersion、派生、tombstone、generation 未混淆；Schema 未冻结。
- **AI 信任与安全负责人：Gate 3 Pass（本地合成门控层）。** 撤权、generation、tombstone fail closed，隐私扫描零命中；真实处理者关闭。
- **体验设计负责人：检查通过（状态合同层）。** 可区分“已保存，索引更新中”“维护中”“失败，继续使用上次合法索引”“保存失败”；具体 UI 不在范围。
- **PM：范围检查通过。** 仅关闭 R-0039，不偷渡架构冻结或 MVP 准入。
- **Gate 4：Pass（P2-014 范围）。** 技术架构整体 Gate 4、P2-015 与 Stage 3 准入仍待各自验收。

需要 PM 确认：验收 P2-014 为 `Pass` 并关闭 R-0039；采纳第 8 节责任边界作为冻结输入但不冻结 harness 细节；继续保持技术架构未冻结、MVP 开发未准入，等待 P2-015 与后续独立决策。

## 范围声明

本任务只修改指定 Spike 目录与本交付物；未修改 PM 主账本、产品代码、Stitch、PRD、V1 范围、领域模型、AI 权限模型或外部系统。
