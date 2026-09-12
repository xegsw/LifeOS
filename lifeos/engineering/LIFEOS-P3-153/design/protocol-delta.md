# P3-153 最小协议差异（待 PM 明确裁决，未实施）

事实：现有 `decide_understanding_feedback` / version 4 / `clarification_decision` 的 decision 只接受 `ignore`、`defer`。AC-04 要求明确拒绝与明确重开，现有协议无法表达。

建议最小变更：

- 保留 IPC 名称、version、请求字段、幂等请求 ID，decision 增加 `reject`、`reopen`。旧请求仍兼容；不新增公共命令、表或 SQL 迁移。
- questions 原 JSON 的 status 增加 `rejected`；明确 reopen 改回 pending。已有 feedback 记录该动作和时间；拒绝不会写状态或长期记忆，普通后续问题不能隐式重开。
- 新问题 ID 增加 basisTurn 实例后缀，保留旧字符串 ID 的读取/决策兼容。不再用固定领域/字段 ID 覆盖历史问题。
- 读取时按领域/字段取最新有效生命周期，避免固定八条历史窗口让拒绝失效；仍遵守原公开响应预算。已答信息仍有效则不再问；暂缓到既定条件、忽略只针对本次，拒绝持续至显式重开。
- UI 只在既有对话问题下增“不要再问”以及拒绝态的“重新讨论”，不改 Settings 或 Shell。

待确认问题：PM 是否批准上述兼容枚举与实例身份变更？批准前不实现该协议；其他合成实现/回归已继续推进。

保持边界：不启用真实模式，不接触真实数据、Keychain、网络；不改 Schema 核心实体、冻结或权限。

## 批准记录

D-0652：用户明确回复“允许协议补充”，PM已将批准范围写入5ed8原任务卡并派发恢复。以上最小差异获批，现按该范围实现；原待决记录保留。
