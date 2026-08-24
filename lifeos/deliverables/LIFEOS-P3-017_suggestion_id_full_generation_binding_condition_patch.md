# LIFEOS-P3-017｜suggestion ID 完整 generation 绑定条件补丁报告

## 任务信息

- 任务 ID：LIFEOS-P3-017
- 任务名称：P1-8 条件补丁：suggestion ID 完整 generation 绑定
- 执行 Agent：Codex
- 任务类型：P3 Engineering Fast Lane / P1 条件补丁 / 工程硬化 / 回归测试
- 更新时间：2026-08-11
- 专项结论：**Pass（需 PM 验收）**

## 修复 / 验证目标

- 让新 suggestion ID 稳定绑定 Project 与完整可消费输入集合，而非首个或主证据。
- 每个输入绑定 evidence version、Artifact、Source、Artifact generation 与 Source generation。
- 保证同一集合顺序变化时 ID 不变，集合或任一非主输入 generation 变化时不复用旧 ID。
- 保持已确认 suggestion 的状态和反馈、P3-015 消费门、P1-4 staling 及既有 21 项回归。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`
- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-009/evidence/invariant_migration_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/architecture_conformance.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/default_off_matrix.md`（验证脚本重生成，关闭状态无变化）

未修改 `src/store.ts` 或 `src/types.ts`：现有 `derivation_input` 字段已足以表达完整绑定，无需变更 Schema 或类型。

## P1-8 条件关闭说明

**[已验证事实]** `suggest()` 先对目标 Project 本次传入的 evidence 执行 fail-closed 检查，再从可消费输入构造规范绑定元组。每个元组包含 `evidenceVersionId`、`artifactId`、数据库读取的 `sourceId`、`artifactGeneration` 与 `sourceGeneration`；元组去重后按确定性字节序排序，并连同 `projectId` 形成 JSON payload，使用 Node 内置 SHA-256 生成 `suggestion:v2:<hash>`。未新增外部依赖，也不再使用 `artifact_generation ?? 1` fallback。

**[已验证事实]** 顺序回归证明同一完整集合倒序调用仍得到同一 ID，且仅保留一条 Derivation 和两条规范输入。Artifact / Source 两类 generation 回归均修改非主输入 `artifact-1`：刷新合法上下文后生成的新 suggestion ID 与旧 ID 不同；旧 Derivation 先由 P1-4 机制置为 `stale`，随后 feedback 与 export 均继续阻断。输入集合从两项缩减为仅主输入时生成不同 ID，并分别保留 2 项与 1 项 `derivation_input`，不会冒充同一建议。

**[已验证事实]** 首轮实现曾暴露 invalid 非主输入被 `recovery()` 过滤后可能以缩减集合创建新候选；已用目标 Project evidence 调用级 fail-closed 修正。P3-015 direct-deny、P1-4 generation mismatch 与 revoke/delete 回归现均通过。已确认 suggestion 的重复调用仍复用同一 ID、保持 `confirmed` 状态及 active feedback，未静默重置为 candidate。

**[合理推断]** 在当前合成、单进程、受控 SQLite 骨架内，ID 已能表达“这一建议基于哪一个 Project、哪组输入及哪一代来源”的稳定身份。该结论不外推到真实 IPC、Vault、模型或生产并发语义。

## 新增 / 修改测试

- `P1-8 suggestion ID is stable across complete evidence order`
- `P1-8 non-primary artifact generation changes suggestion ID and stales old derivation`
- `P1-8 non-primary source generation changes suggestion ID and stales old derivation`
- `P1-8 complete evidence set change cannot reuse suggestion ID`

## 测试摘要

- 直接复跑：`node --experimental-strip-types --test tests/invariants.test.ts`
- Evidence 生成：`node scripts/validate.mjs`
- 最终结果：**25 PASS / 0 FAIL；P0 FAIL=0**。
- 原有回归：21/21；P1-8 新增：4/4；P1-3 / P1-5：4/4；P3-015：1/1；P1-4：2/2；H1-H9 / T-ARCH 全部通过。
- Snapshot：`9a3136bf9ba1f92ea501e0401665ea3b873d1afae303a5a4cf541dfb2c2ce95a`。
- P3-001 独立快照核对：7/7 匹配，未修改。
- 异常：仅有 `node:sqlite` experimental warning，不作为生产能力或技术冻结依据。

## Evidence

- Manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- 原始日志：`lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- 矩阵：`invariant_migration_matrix.md`、`architecture_conformance.md`、`default_off_matrix.md`

Manifest、JSON、日志和矩阵来自同次验证，25/0、分类统计和 snapshot 一致；八类默认关闭能力未被破坏。

## 非范围与剩余风险

- 未改变产品定位、V1 范围、技术架构 V0.1 冻结合同、核心领域模型或 AI 权限边界。
- 未启用真实数据、真实 Vault、真实 Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- 未修改 P3-001 或项目账本；不关闭 R-0040，不恢复工程基线，不进入下一阶段。
- P1-6 restore candidates / 权威投影 / 旧包不复活与 P1-7 `expires_at` / `retract_feedback` 仍未迁移。
- 未处理 `feedback()` 的 `INSERT OR REPLACE`、导出/恢复格式、自引用 Link、夹具多样性或其它 P2 清洁项。

## 角色与关卡

- 工程负责人：**Pass**；代码集中在 ID 规范化、哈希及调用级 fail-closed，既有 21 项全通过。
- 数据与权限负责人：**Pass（受控边界）**；完整绑定 evidence version、Artifact、Source 与双级 generation，并覆盖非主输入。
- AI 信任与安全负责人：**Pass（受控边界）**；集合或 generation 变化不会静默冒充同一建议，旧建议继续 stale / 阻断，内容身份与反馈身份未改变。
- QA / 测试负责人：**Pass**；顺序、两类非主 generation、集合变化、确认保留、旧消费门与默认关闭均有可复跑证据。
- 技术架构负责人：**Pass with Conditions**；仅使用 Node 内置 hash，未改变 Schema/API/模块冻结或启用真实能力；R-0040 保持 Open / Conditional。
- 已覆盖关卡：P1-8 完整绑定、P1-4、P3-015、P1-3 / P1-5、H1-H9 / T-ARCH、evidence manifest、默认关闭能力回归。

## 本地预检

已按规则调用，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景，不阻塞工程交付。报告：`lifeos/local_prechecks/LIFEOS-P3-017_LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch_local_precheck.md`。该结果不替代 PM Review。

## 结论

**Pass（需 PM 验收）。** P1-8 已在任务授权边界内完成：suggestion ID 稳定绑定 Project 和完整排序输入集合的 version / Artifact / Source / 双级 generation；25 PASS / 0 FAIL、P0=0。无需用户级产品/范围/架构决策或独立复评，但任务是否正式接受仍需 PM 主会话验收。
