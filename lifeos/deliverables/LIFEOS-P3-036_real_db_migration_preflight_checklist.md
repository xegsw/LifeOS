# LIFEOS-P3-036｜真实 DB migration 前置验证清单

## 1. 任务信息

- 任务 ID：LIFEOS-P3-036
- 任务类型：技术验证前置任务 / 检查清单 / 决策输入
- 执行 Agent：Codex（专项技术规划会话）
- 主责角色：技术架构负责人
- 协审角色：数据 / 领域模型、AI 信任与安全、QA / Evidence Reviewer、PM
- 评审关卡：Gate 2、Gate 3、Gate 4
- 输出性质：未来执行任务输入；不是 migration、执行记录、风险关闭或冻结结论

## 2. 执行摘要

1. **[事实]** 当前证据证明候选 SQL 可在内存合成空库执行，并通过 35 项合同测试；它没有证明既有非空数据库可升级，也没有触碰真实用户 DB。
2. **[事实]** R-0043 / R-0044 / R-0045 已在“候选 SQL + 合成空库 + 当前 evidence + 有限 Stage 3”范围内关闭；P2-2 / P2-3 / P2-4 已明确转入本前置清单。R-0040 仍为 Open / Conditional。
3. **[判断]** 下一执行任务只能先验证“真实文件型 SQLite 引擎行为”，并继续使用合成、无敏感信息的 fixture；不得把“文件型 DB”偷换为用户真实数据库。
4. **[判断]** 当前 `001_candidate_schema.sql` 是空库/bootstrap 候选，不是任意旧版本到目标版本的 upgrade migration。若后续目标包含非空旧库，必须先补 source-version → target-version 矩阵、字段转换、冲突处理及恢复策略。
5. **[建议｜需 PM 确认]** 可在本清单验收后另立“受控文件型 SQLite migration 验证”任务，专门攻击 P2-2 / P2-3 / P2-4；真实用户库、真实 Vault、Tauri / IPC 与生产发布仍不得启用。

## 3. 前置验证边界

| 层级 | 定义 | 本任务状态 | 后续是否可写 |
|---|---|---|---|
| 候选 SQL | candidate-only 的 `001_candidate_schema.sql` | 只读输入 | 仅新任务明确授权后可改 |
| 合成空库 | 内存 SQLite + 代码内合成夹具 | 已有 35 PASS 证据 | 可在既有受控测试中重建 |
| 文件型临时测试 DB | 临时隔离目录中的 SQLite 文件，仅含合成 fixture | 本任务不创建 | 后续执行任务可明确授权写临时副本 |
| 结构化升级 fixture | 模拟特定旧 schema/version 的无敏感测试库 | 当前不存在 | 必须另行定义版本和转换规则后创建 |
| 真实用户 DB | 用户实际 LifeOS 数据库或其含真实内容的副本 | 禁止接触 | 本路线当前不授权 |
| 真实 Vault / 文件能力 | Obsidian Vault、用户文件、真实导出路径 | 禁止接触 | 仍由独立任务与权限边界控制 |

未来文件型验证必须保持：网络关闭；云/第三方模型、向量、同步、多设备、L3、外部用户关闭；不启动 Tauri / IPC；不接受真实路径、正文、用户 ID、Project 名、URL、密钥或可反识别 hash。fixture 只保留验证约束所需的最小合成关系。

## 4. 执行任务硬准入条件

以下项目全部满足才可启动受控执行；任一为 Unknown 即不准入：

- [ ] PM 已创建独立任务卡，明确只写临时隔离目录和合成 fixture。
- [ ] 已确定执行类型：A. 空库/bootstrap；B. 指定旧版本 upgrade。不得混用结论。
- [ ] 若为 B，已有唯一的 source schema/version、target version、逐表转换规则、不可转换处理和幂等策略；否则 Blocked。
- [ ] 候选 SQL、测试脚本、复跑脚本的 SHA-256 与 evidence MANIFEST §4.1 完全一致。
- [ ] 生成结果 hash 按“运行快照”处理，不与稳定源文件 hash 混用。
- [ ] SQLite 版本、编译选项（至少 JSON1、FTS5）、操作系统、journal mode、foreign_keys 状态已记录。
- [ ] fixture 清单经人工确认不含真实用户数据、Vault 路径、URL、密钥、正文或其他敏感标识。
- [ ] 源 fixture 以只读方式保存；所有攻击和 migration 仅在其工作副本上执行。
- [ ] 临时工作目录是新建、空、路径明确的隔离目录；没有指向用户数据库或 Vault 的 symlink。
- [ ] migration 前已生成源文件 hash、SQLite 备份、schema dump 和 `quick_check` / `foreign_key_check` 基线。
- [ ] 已在另一临时副本完成恢复演练，并验证恢复后 hash、schema、行数/关系断言和消费门结果。
- [ ] 退出合同明确：任一 P0/P1 FAIL、hash 不一致或检查 Unknown 均非零退出；不得继续下一阶段。
- [ ] R-0040 明确保持 Open / Conditional；R-0043 / R-0044 / R-0045 的既有关闭范围不被扩大或改写。

## 5. P2-2 / P2-3 / P2-4 验证清单

### 5.1 P2-2｜Tombstone DELETE + INSERT 旁路

- **目的**：确认维护/直接 SQL 路径不能通过删除 tombstone 后以更低 generation 重建而复活已阻断对象。
- **输入前置**：工作副本含 subject generation=5、tombstone generation=5、状态 `active_blocked`，并包含搜索、恢复候选和 outbox 的合成引用；源 fixture 只读。
- **最小反例**：在单一显式事务中尝试 DELETE 该 tombstone，再 INSERT 同 subject、generation=4；分别测试普通 DELETE、`INSERT OR REPLACE`、rollback/commit 两路。
- **推荐目标合同**：DB 直接拒绝 tombstone DELETE；若 PM 选择受控维护例外，必须同时满足不可伪造的维护边界、追加 audit、replacement generation 不降低、全过程消费门持续阻断，且任一步失败整体 rollback。不得仅依赖“正常代码不会 DELETE”。
- **PASS**：攻击被 DB 拒绝且原 tombstone 完整不变；或经 PM 预先确认的受控维护事务满足全部等价不变量。提交后 read/search/suggest/outbox/export/restore 均继续拒绝。
- **FAIL**：DELETE 或 replace 可静默提交；generation 降低；tombstone 短暂/永久消失；任何消费路径返回对象；audit 缺失或失败后出现部分状态。
- **证据**：前后 schema/hash、目标行快照（仅合成 ID）、SQL 错误码、事务退出码、六类消费门结果、rollback 后快照、审计行。

### 5.2 P2-3｜Tombstone status INSERT 旁路

- **目的**：确认新建 tombstone 不能跳过 `accepted → active_blocked → cleanup_*` 的诚实状态流程。
- **输入前置**：不存在该 subject tombstone；目标对象与合成依赖可消费；预期 generation 固定。
- **最小反例**：直接 INSERT 初始状态为 `active_blocked`、`cleaned`、`cleanup_failed`、`vendor_limited`；另测合法 `accepted` 起点与后续转换。
- **推荐目标合同**：普通创建只允许初始 `accepted`。进入 `active_blocked` 必须由应用事务 guard 证明所有消费门已拒绝；cleanup 状态只能走已定义转换矩阵。未知或缺证据一律 fail closed。
- **PASS**：非法初始状态被拒绝且零残留；合法 `accepted` 可创建；未完成全路径证明前不能宣称 `active_blocked`；合法/非法 UPDATE 转换与候选合同一致。
- **FAIL**：直接 INSERT 任意终态成功；状态声称已阻断/已清理但消费仍可达；失败留下半条 tombstone、job 或 audit。
- **证据**：各状态用例矩阵、错误码、零残留查询、消费门断言、合法转换日志、失败注入与 rollback 结果。

### 5.3 P2-4｜Authorization 激活后子表 DELETE

- **目的**：确认删除 active Authorization 的 scope/action/policy 后不会产生权限放宽，同时保留可审计的完整性语义。
- **输入前置**：一条完整 active Authorization，包含 allow 与 deny 反例、scope/action/policy、canonical envelope hash 和合成审计上下文。
- **最小反例**：分别 DELETE 一条 scope、一条 action、policy；再测事务中先删后查询、提交后查询、rollback 和并发旧缓存读取。不得只测试最终行数。
- **最低安全合同**：任何子表缺失或不完整，`strict_intersection` 必须 DENY/AMBIGUOUS；旧缓存不得返回 ALLOW；入队、执行、发布均重算。
- **推荐审计合同**：active Authorization 的子表不允许无审计 DELETE。优先 DB 拒绝；若允许受控变更，必须在同一事务撤销/降级父 Authorization、递增 generation、写最小 audit/outbox，并使旧决定立即失效。
- **PASS**：直接 DELETE 被拒绝；或受控事务提交后父授权不再 active、generation 增长、audit 完整且所有消费门 DENY。rollback 后恢复完整原状态。
- **FAIL**：缺子表的 Authorization 仍 active 且请求 ALLOW；旧缓存/队列可继续消费；DELETE 无审计或父 generation 不变；发生部分提交。
- **证据**：三类子表前后快照、父状态/generation、strict_intersection 结果、缓存/队列重检、audit/outbox、并发/rollback 日志。

## 6. 建议命令边界（仅供未来授权任务）

以下是命令形态，不在本任务执行；路径必须由未来任务解析到新建隔离目录，禁止使用用户 DB/Vault 路径：

```bash
shasum -a 256 <candidate.sql> <test-script> <runner>
sqlite3 -readonly <synthetic-source.db> "PRAGMA quick_check; PRAGMA foreign_key_check;"
sqlite3 <isolated-working-copy.db> < <authorized-migration.sql>
sqlite3 -readonly <isolated-working-copy.db> "PRAGMA integrity_check; PRAGMA foreign_key_check;"
```

执行脚本不得接受未校验的绝对路径、`~`、宽泛目录、网络挂载或 symlink 目标；不得原地修改 source fixture。日志必须脱敏，不回显正文、真实路径、SQL 参数中的敏感值或底层自由错误。

## 7. 建议 evidence 结构

```text
lifeos/engineering/<future-task>/evidence/
  MANIFEST.md
  environment.json
  input/
    source_manifest.json
    source_schema.sql
    source_hashes.txt
  migration/
    candidate_hashes.txt
    apply.log
    rollback.log
    restore_rehearsal.log
  checks/
    integrity_before.txt
    integrity_after.txt
    p2_2_tombstone_delete_insert.json
    p2_3_tombstone_status_insert.json
    p2_4_authorization_child_delete.json
    consumption_gate_results.json
  results/
    test_results.json
    summary.md
```

`MANIFEST.md` 必须记录：任务/授权边界、fixture 合成证明、工具版本、源/目标 schema version、稳定源文件 hash、运行快照 hash、准确命令、退出码、P0/P1/P2/Not Implemented 统计、失败项、恢复演练、未验证项和不可外推声明。完整日志写入 evidence；聊天只报摘要和入口路径。

## 8. PASS / FAIL 与严重级别

- **总体验收 PASS**：所有硬准入项为 Yes；migration 原子完成或安全 rollback；`integrity_check` / `foreign_key_check` 通过；P2-2/3/4 均满足目标合同；P0=0、P1=0、Not Implemented=0；源 fixture 未变；恢复演练通过。
- **P0**：触碰/修改真实用户 DB、Vault 或隔离目录外文件；用户原文/身份/来源被静默改变；删除对象复活；不完整授权产生 ALLOW；migration 部分提交导致权威数据丢失且无法恢复；真实能力误启用。
- **P1**：P2-2/3/4 任一旁路在文件型 DB 中成立但尚未造成已证实消费；hash/version 不匹配；源 fixture 被写；backup/restore 不可证明；migration 非原子；审计或 generation fencing 缺失；结果不可稳定复跑。
- **P2**：日志命名、排序或非关键 hash 展示问题，且不影响可追溯性、语义、退出码和 fail-closed 判断。
- **FAIL**：任一 P0/P1；任一 required test 未实现；任一核心检查为 Unknown；生成 evidence 不足以复核。不得用“P2 原问题”标签自动把验证中证实的可利用旁路继续定为 P2。

## 9. 立即停止并回到 PM

出现以下任一情况必须停止，不就地改 SQL、不改账本、不继续后续用例：

1. 路径解析指向真实用户 DB、Vault、用户文件、网络盘或隔离目录外目标。
2. fixture 发现真实正文、真实标识、路径、URL、密钥或来源不明数据。
3. source/target version 不唯一，或 candidate bootstrap 被要求直接作用于未知非空库。
4. 任何稳定源文件 hash 与已批准 MANIFEST 不一致。
5. backup 无法恢复、恢复 hash/关系断言不一致、`integrity_check` / `foreign_key_check` 失败。
6. migration 出现部分提交、未知 trigger 行为、SQLite 版本/编译选项差异或非确定结果。
7. P2-2/3/4 反例导致消费放行、删除复活、授权放宽、审计断链或数据身份混淆。
8. Tauri / IPC、真实文件导出、云、模型、向量、同步、多设备、L3 或外部用户被启用。
9. 需要修改 Schema/API、核心实体、AI 权限边界、风险状态或冻结状态才能继续。

## 10. PM 验收与独立评审口径

PM 最少复核：任务卡授权；合成 fixture 证明；路径隔离；源/目标版本；稳定 hash；环境；备份与恢复演练；before/after integrity/FK；P2-2/3/4 逐项证据；消费门结果；失败/退出码；不可外推声明。PM 应至少在全新临时副本抽样复跑三项反例和一个 rollback 场景。

发现 P0、任何真实数据/权限/删除语义旁路、需要修改候选 SQL、准备接触真实用户 DB、准备冻结 Schema/API、关闭 R-0040 或进入下一阶段时，必须退出快车道并安排与执行会话隔离的独立评审。执行 Agent 不得独立评审自己的真实 DB 结果。

## 11. 关卡、风险与待确认事项

- Gate 2：**Pass with Conditions（清单层）**。已覆盖 Tombstone、Authorization、来源/身份、备份恢复和不复活；条件是未来执行产生可复核 evidence。
- Gate 3：**Pass with Conditions（清单层）**。P2-4 要求缺失子表 fail closed 且缓存/队列重检；真实 IPC 仍未验证。
- Gate 4：**Pass with Conditions（规划层）**。步骤、停止规则和 evidence 可执行；但 upgrade 版本矩阵、真实文件型结果、WAL/backup 耐久和性能尚不存在。
- R-0040：继续 Open / Conditional，本任务没有关闭证据。
- R-0043 / R-0044 / R-0045：保持既有 Closed 状态和有限关闭范围；本任务不重新打开或关闭。若未来证实残留 P2 可直接利用，应停止并由 PM 按既有失效条件重新评估。

**[需 PM 确认]**：是否接受“下一步仅创建受控文件型 SQLite + 合成 fixture 验证任务”；是否把 DB 直接拒绝作为 P2-2/3 的推荐目标合同、把“父授权降级/撤销 + generation + audit”作为 P2-4 的可接受等价合同；若要验证非空旧库，是否先另立 upgrade version matrix / 转换设计任务。

## 12. 后续任务建议与不可外推声明

**[建议]** 本清单可作为“受控文件型 SQLite migration / 残留 P2 验证执行任务”的输入，边界应限定为：新建隔离目录、合成无敏感 fixture、只读 source、可丢弃工作副本、P2-2/3/4 反例、backup/restore、integrity/FK、完整 evidence。若执行目标为非空旧版本 upgrade，应先补版本矩阵和转换设计，不能直接使用 bootstrap 候选冒充 upgrade migration。

本任务没有执行 SQL、创建或连接数据库，也没有修改工程代码、候选 SQL、测试、脚本、evidence、Stitch 或 PM 账本；没有启用真实 DB/Vault/Tauri/IPC/文件能力、云/第三方模型、向量、同步、多设备、L3 或外部用户。本文及未来合成文件型验证均不得外推为 Schema/API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线冻结，不得外推为真实 Tauri/IPC 通过、R-0040 关闭、正式 MVP 准入或下一阶段准入。

本地预检：`lifeos/local_prechecks/LIFEOS-P3-036_LIFEOS-P3-036_real_db_migration_preflight_checklist_local_precheck.md`。状态为 **Skipped / Local Model Unavailable**（connection reset by peer），符合失败降级规则；未作为技术判断或 PM 验收依据。
