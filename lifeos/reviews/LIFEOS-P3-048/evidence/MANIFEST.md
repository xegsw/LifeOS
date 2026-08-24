# LIFEOS-P3-048 PM Verification Evidence Manifest

## 结论

- PM 在隔离临时副本复跑 P3-048 总入口，退出码 0。
- P3-048 专项：552 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown。
- P3-047 当前协议等价回归：297 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown。
- P3-031 当前全量：70 PASS / 0 FAIL / 0 Not Implemented，退出码 0。
- 40 个 P3-047/P3-046 只读文件全部满足 expected = before = after，`unchanged=true`。
- PM 在同一隔离副本直接执行 P3-047 原 PM-CE-06 脚本攻击新候选 SQL，得到 8 PASS / 0 BYPASS，入口退出码 0；八个配置均由 `authorization_tombstone_control_envelope_immutable` 拒绝。
- 本 evidence 支持 P3-048 在合成 SQLite 边界内判定 `Accepted / Remediation Regression Passed`；不代表独立复评通过、风险关闭、Schema/API/migration/工程基线冻结或生产适用。

## 隔离复跑

- 隔离副本：`/tmp/lifeos-p3048-pm.eOuqsz`
- 复制范围：工作区 `lifeos/`，排除历史大型 `spikes/` 与各任务 `work/` 合成数据库；测试在隔离副本重新生成自身 work/evidence。
- 总入口：

```bash
sh lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.sh
```

- 总入口退出码：`0`。
- 两次前置命令曾因工作目录使用错误导致路径解析失败并在测试启动前退出 127；未执行测试、未修改项目文件，也未计入验收证据。随后在上述隔离副本根目录成功完整复跑。

## PM 直接反例复跑

在隔离副本中直接运行原 P3-047 PM-CE-06：

```bash
python3 lifeos/reviews/LIFEOS-P3-047/evidence/pm_counterexample_attacks.py
```

结果：

- PASS：8
- BYPASS：0
- P2 BYPASS：0
- 退出码：0
- `ALL_REJECTED=True`
- 唯一拒绝错误：`authorization_tombstone_control_envelope_immutable`

该命令只覆盖隔离副本中的旧结果文件；源工作区 P3-047 原 `0 PASS / 8 BYPASS` 历史结果未改变。

## 结构与回归核查

- 候选 trigger 条件为：OLD 或 NEW 任一侧 `subject_type='authorization'`，且六个控制包络字段任一变化即拒绝。
- 未全局冻结 generic Tombstone；专项合法路径证明 generic generation/control/status 既有更新语义仍可用。
- 攻击矩阵覆盖 generic→Authorization、Authorization→generic、Authorization A→B、六 cleanup 状态、六单字段与复合字段、身份+状态+时间同语句、五类替换/重建相邻语义、多行原子失败和合法状态推进。
- 文件型 SQLite 合计 216 个实例，执行 evidence 记录全部 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

## 源工作区核对

| 文件 | SHA-256 |
|---|---|
| P3-031 当前候选 SQL | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| P3-048 SQL 输入快照 | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| P3-048 runner | `6d5d4b75d3b6439aa903d554d29b80c30ad1470539bb802115fcdda67b3156c2` |
| P3-048 test results | `fc698f8e46230038f5d9110db3b49e1e5971ca11750bea9fde1ca018a5787fb1` |
| P3-047 等价结果 | `85518c2b3a5fa8929b675910ba32756af96388ce08070c2cbce3700d21b29d1f` |
| P3-031 回归结果 | `59fc105b4a4e49330271299a4f881d9a59bf97c6b77fce4eb313f8f88943c2a7` |
| P3-047 原 PM-CE-06 脚本 | `54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50` |
| P3-047 原 PM-CE-06 结果 | `f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5` |

源工作区 `read_only_preservation.json` 共 40 项，PM 重新计算当前源文件 hash 后确认 40/40 保持一致。`lifeos/FREEZE_STATUS.md` 未修改。

## PM 边界

- R-0048 继续保持 `Open / Remediation Candidate`。
- R-0049 可从 `Open / Rework` 更新为 `Open / Remediation Candidate`，但不得关闭。
- P3-048 资产保持 `Accepted but Not Frozen / Pending Independent Re-review`。
- 用户确认前不创建或启动后续隔离独立复评任务；不恢复工程基线、不启用真实能力、不进入下一阶段。
