# LIFEOS-P3-053｜R-0048 Outbox 来源／重放与生命周期初始值整改

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定工作区、候选代码和合成测试数据，用于防御性代码审查、缺陷修复与本地回归测试；不授权访问外部或第三方目标、真实用户数据或真实凭据，也不涉及未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“攻击、反例、旁路、权限”等术语仅指本地合成环境中的负向验证。既有只读、用户确认、独立性和停止条件继续有效。

## 任务信息

- 任务 ID：LIFEOS-P3-053
- 优先级：P0
- 任务类型：R-0048 窄范围候选 SQL 整改与回归
- 是否适用 P3 Engineering Fast Lane：No；P1 风险整改
- 推荐执行 Agent：Codex 新建工程会话
- 推荐模型 / 推理强度：`gpt-5.6-terra` + `xhigh`
- 允许降级模型 / 后备模型：None / None
- 禁止降级条件：P1 生命周期证据、Outbox provenance/replay、权限与撤回边界；不得降低验证强度。
- 必须升级条件：证据、事务语义或 SQLite trigger 判断冲突时，在同一会话升级 `gpt-5.6-terra` + `max`；仍无法判断则停止回报 PM。
- 是否需要后续独立评审：Yes，必须由未参与本任务执行的全新隔离会话完成。
- 允许修改：仅 P3-031 当前候选 SQL、相关合同测试/runner、P3-053 交付物与工程 Evidence。
- 只读：P3-046/P3-047/P3-048/P3-049/P3-050/P3-051/P3-052 的任务、Review、Evidence 与 PM Evidence；所有主账本。
- 禁止：关闭 R-0048、修改 R-0049、冻结资产、恢复基线、真实 DB/Vault/Tauri/IPC/云/外部能力或阶段推进。
- 主责角色：技术架构负责人、AI 信任与安全负责人、QA / Evidence Reviewer
- 必须通过关卡：Gate 2、Gate 3、Gate 4
- 状态：In Progress
- 实际派发：全新 Codex 任务 `01a021fd-8560-7af1-95ee-880078ba3aa9`，host `local`，`gpt-5.6-terra` + `xhigh`，2026-08-21 CST。

## 整改范围

1. 禁止直接伪造 `authorization_state_change` Outbox；其插入须可验证地绑定匹配 lifecycle command、terminal Authorization、唯一 AuditEntry、correlation/idempotency、subject generation 与 payload 的同事务来源。
2. retention 删除后保留 lifecycle job replay fence；不得以已删除 job 的 ID/idempotency/correlation 重插不同 payload，同时不得误伤 generic/非 lifecycle job 的合法清理。
3. 强制新 Authorization 初始 generation=1，并拒绝 non-revoked 状态预写 `revoked_at_ms`；覆盖 INSERT、activation、terminal、REPLACE/冲突与八配置。
4. 迁移 P3-052 四类反例、PM-CE-01 至 PM-CE-05、P3-031 回归、memory/file/FK/recursive 矩阵、事务原子性和文件完整性。

## 验收规则

- 任何 P0/P1、明确 P2 bypass、Evidence 冲突、历史资产覆盖或真实能力触达：停止并报告 Rework/Blocked。
- 执行回归通过也只构成独立复评输入；不得关闭 R-0048。
- 交付物：`lifeos/deliverables/LIFEOS-P3-053_r0048_outbox_provenance_replay_and_lifecycle_initialization_remediation.md`；工程 Evidence：`lifeos/engineering/LIFEOS-P3-053/evidence/MANIFEST.md`；PM 验收前不得启动后续任务。
