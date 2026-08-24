# LIFEOS-P3-046 PM Counterexample Evidence Manifest

## 结论

- PM 在隔离临时副本复跑原任务入口：P3-046 为 248 PASS / 0 FAIL，P3-031 为 64 PASS / 0 FAIL，退出码 0，P3-044 preservation 为 True。
- 原回归可复现，但其攻击集合不完整。PM 对当前候选 SQL 新增 5 条定向反例，结果为 0 PASS / 5 BYPASS，其中 P1=2、P2=3，反例入口退出码 1。
- 本 evidence 只支持 PM 对 P3-046 作 Rework 判断；不关闭风险、不冻结 Schema/API、不触达真实数据或真实能力。

## 复跑命令

```bash
python3 lifeos/reviews/LIFEOS-P3-046/evidence/pm_counterexample_attacks.py
```

预期退出码：`1`，表示候选实现仍存在可复现合同旁路或过度约束。

## 文件与 Hash

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `pm_counterexample_attacks.py` | 合成内存 SQLite 定向反例 | `725dc0b2a4e36e9eac9949c9dbc9cb969493a67c303f5684ad268d63d8edb777` |
| `counterexample_results.json` | 结构化实际结果 | `541fe7980e7ab7d4ce6c38188aeacac477813760ff0810ada0cfee40ff16e560` |

## 反例摘要

| ID | 级别 | 结果 | 问题 |
|---|---|---|---|
| PM-CE-01 | P2 | BYPASS | 任意 `canonical_request_hash='x'` 且无 Submission 行时 lifecycle command 仍成功 |
| PM-CE-02 | P1 | BYPASS | `available_at_ms` 在未来的 pending job 仍可被提前 leased |
| PM-CE-03 | P1 | BYPASS | 不带当前 lease owner/generation CAS 条件也能把有效租约标为 completed |
| PM-CE-04 | P2 | BYPASS | cleanup_pending Authorization tombstone 的 subject、command、reason、blocked time 可被重写 |
| PM-CE-05 | P2 | BYPASS | 非 Authorization terminal outbox job 被全局 delete trigger 永久阻断，缺少通用受控清理路线 |

此外，静态复核确认当前 Authorization outbox 删除合同没有实现 P3-045 所述 retention window。该项与 PM-CE-05 一并进入后续整改，不单独增加统计实例。

## 数据与执行边界

- 只读取当前候选 SQL，并在 `:memory:` SQLite 中使用合成记录。
- 未修改 P3-031/P3-046 工程实现或原 evidence。
- 未连接真实 DB、Vault、文件能力、Tauri/IPC、网络、云、第三方模型、同步、多设备、L3 或外部用户。
