# LIFEOS-P3-054｜R-0048 Outbox／生命周期整改全新隔离独立复评

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定工作区、候选代码和合成测试数据，用于防御性代码审查、缺陷验证与本地回归测试；不涉及外部目标、真实数据/凭据、未授权访问、网络扫描、真实攻击、持久化、数据获取或安全控制规避。所有“攻击、反例、旁路、权限”仅指本地合成负向验证；既有安全关卡、只读与用户确认继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-054
- 优先级：P0
- 类型：P3-053 整改后的全新隔离独立工程复评
- 推荐 Agent：Codex 新建隔离会话；WorkBuddy 无额度。
- 推荐模型 / 推理强度：`gpt-5.6-terra` + `xhigh`
- 允许降级 / 后备：None / None
- 禁止降级：P1 Outbox 证据、权限/撤回、重放与生命周期边界必须保持高强度独立验证。
- 必须升级：若不能独立判断 SQLite trigger、事务、Evidence/hash，升级 `gpt-5.6-terra` + `max`；仍无法判断则 Blocked。
- 工程与账本：严格只读；仅可写 P3-054 自身 deliverable/review/evidence/precheck。
- 必须关卡：Gate 2、Gate 3、Gate 4；本任务本身为独立复评。
- 状态：In Progress
- 实际派发：全新 Codex 任务 `01a0223a-f42c-7132-80e4-3c4ccce44072`，host `local`，`gpt-5.6-terra` + `xhigh`，2026-08-21 CST。

## 隔离与核查

- 必须使用未承载任何 LifeOS 工作的新会话；禁止复用 P3-053 执行会话、P3-052、P3-050、P3-051 或 PM 会话。
- 在读取 P3-053 具体反例脚本、结果、review 前，先按任务卡、P3-052 PM Review 与当前候选 SQL封存独立攻击计划。
- 自建脚本不得 import/call P3-053/P3-052 runner、helper 或场景表；历史 runner 仅可用于等价回归。
- 复核 P3-052 历史失败 Evidence 和 P3-053 输入/执行 Evidence 没有被覆盖。

## 必测范围与判定

1. `authorization_state_change` Outbox 的伪造 INSERT/REPLACE、claim/complete、command/audit/submission/correlation/generation/payload/canonical identity 全链路。
2. retention 后 job ID/idempotency/correlation/payload replay，以及 generic terminal job 合法清理不回退。
3. Authorization initial generation=1、non-revoked `revoked_at_ms=NULL`，含 INSERT、REPLACE、conflict、activation 和三终态配对。
4. memory/file、FK ON/OFF、recursive triggers ON/OFF、事务/多行/rollback、文件完整性；P3-031、PM-CE-01 至 PM-CE-05 回归。
5. Pass：0 P0/P1/明确 P2 bypass，0 Not Implemented/Unknown，独立性/hash/回归成立；只作为 R-0048 风险决策输入。否则 Rework/Blocked。

不得关闭 R-0048、重新打开 R-0049、冻结资产、恢复基线、启用真实能力或进入下一阶段。
