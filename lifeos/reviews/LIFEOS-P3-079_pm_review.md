# LIFEOS-P3-079 PM Review｜本地 MVP 整合受控能力包

## 验收信息

- 任务 ID：LIFEOS-P3-079
- 是否为受控能力包：Yes
- 对应交付物：`lifeos/deliverables/LIFEOS-P3-079_local_mvp_integrated_controlled_capability_package.md`
- PM Review 路径：本文件
- 执行授权证据核验：交付物记录用户已按 D-0319 投递任务卡至新隔离 Codex 工程会话；本卡无投递前单独确认例外。
- 任务验收状态：**Accepted / PM Adjusted to Rework**
- 资产冻结状态：**Not Accepted as Independent-review Input**
- 是否允许进入下一任务：No
- 是否允许进入下一阶段：No
- 更新时间：2026-08-21

## PM 结论

- 执行侧的干净副本自检为 16 PASS / 0 FAIL，覆盖保存、来源／状态、默认拒绝、grant／deny、恢复、重启、原子失败与关闭态；但其未覆盖撤回幂等键跨权限冲突。
- PM 定向反例稳定复现：已用于撤回 permission A 的幂等键可用于请求撤回 permission B，并错误回报 permission B 已成功幂等撤回，而 B 仍为 current。此为 P1。
- 因此“重复命令幂等且冲突可见”的明确验收标准未满足；不得以其它 16 项通过抵消。
- PM 另记录一次自身复跑错误写入工程侧 Evidence，导致提交 Manifest 的 `self_check_results.json`、`self_check.log` 与 `operator_snapshot.json` hash 漂移。该变动不涉及候选源码或历史只读资产，但形成 P2 Evidence 完整性问题。
- P0=0、P1=1、P2=1、Unknown=0、Not Implemented=0。本地预检因模型不可用跳过，未参与结论。

## 允许的包内 Rework（需用户确认后执行）

仅在 P3-079 原隔离工程范围内：

1. 将撤回幂等键绑定至 permission ID 与请求语义；不同 permission 的同键请求必须 `idempotency_conflict` 且不得声称成功。
2. 增加同键同对象重复与同键异对象冲突、重启后重放、审计回执一致性的正负测试和 CLI／runner Evidence。
3. 保留当前提交 Evidence 为只读历史；在新的 Rework Evidence 子目录生成新的逐项结果、日志、快照、hash 与 Manifest。

不得扩大到真实数据／DB／路径／文件、Tauri/IPC、网络、云、导出、同步、多设备、L3、外部用户、风险、冻结、基线或 Stage 4。修复后仍须重新 PM 验收和一次全新隔离独立复评。

## 用户确认

是否授权在 P3-079 原能力包内执行上述窄 Rework？不确认则任务保持 Rework，不能进入独立复评。

---

## D-0328 Rework PM 复验（2026-08-21）

### 验收结论

- **任务验收状态：Accepted / PM Pass / Awaiting Fresh Isolated Independent Re-review。** 原 P1 已修复：撤回幂等回执现在绑定 `permission_id`、`REVOKE` 确认值与 `permission_revoke` 操作语义；同键异 permission 返回可见的 `idempotency_conflict`，不会撤回目标 permission 或报告成功。
- PM 在全新临时副本中复跑 D-0328 runner：20 PASS / 0 FAIL；随后以独立定向断言验证“同对象同键重放 → `idempotent_repeat`、跨 permission 同键 → `idempotency_conflict`、重启后同一冲突仍保持、目标 permission 仍为 `current`”。
- `evidence/rework/MANIFEST.md` 所列 10 项新 Rework Evidence／候选源码 hash 已逐项重新计算并一致。新 runner 只在临时副本运行，PM 复验没有再次写入工程 Evidence。
- P0=0、P1=0、当前 Rework 实现／Evidence P2=0、Unknown=0、Not Implemented=0。D-0327 中 PM 曾误写父 Evidence 的 P2 完整性事件继续作为历史事实保留；它已由新的隔离 Rework Evidence 与基线 hash 记录隔离，不是未处理的当前实现缺陷。
- 本地预检于本次提交后重跑，但本地模型不可用，按规则跳过；预检未参与此 PM 结论。

### 受控能力包关卡

- 包内实现、回归、补测、Evidence 与文案对齐：通过。
- 干净副本首次／幂等／重启演练：通过；原子失败、拒绝／阻断、审计追溯与禁止能力关闭态继续由 16 项既有测试覆盖，新添 4 项撤回语义测试。
- 验收标准→测试→Evidence：新 Evidence 含 runner、逐项结构化结果、日志、CLI 链、快照、父 Evidence 历史 hash 与 Manifest，可复跑。
- 历史资产：P3-063／067／075／077 仍为只读输入，未发现覆盖；父 P3-079 Evidence 的既有 P2 漂移不被掩盖或回写。

### 后续关卡与限制

- 必须进行一次**全新隔离**独立安全／体验复评；该会话不得复用 P3-079 工程执行或本 PM 会话，不得调用执行侧 rework runner 作为其主反例。
- P3-079 资产为 **Accepted but Not Frozen**。不得关闭／重开风险、恢复工程基线、冻结任何资产、启用真实能力或进入 Stage 4。
- 用户需决定是否采纳本 PM Pass 并授权 PM 创建该全新隔离独立复评；在此之前不自动创建后续任务。

### PM 复验 Evidence

- `lifeos/reviews/LIFEOS-P3-079/pm_evidence/rework/verification.json`
- `lifeos/reviews/LIFEOS-P3-079/pm_evidence/rework/MANIFEST.md`
- 本地预检（Skipped / Local Model Unavailable）：`lifeos/local_prechecks/LIFEOS-P3-079_LIFEOS-P3-079_local_mvp_integrated_controlled_capability_package_local_precheck.md`
