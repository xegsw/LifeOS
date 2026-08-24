# SP-07 合成夹具说明

- 固定种子：`20260809`。
- 内容单元：60 条；Project：4 个，每个 15 条。
- 语义覆盖：Source、Artifact、ArtifactVersion、Derivation、Decision、Action、Link、Feedback、Authorization、AuditEntry。
- 状态覆盖：正常、证据冲突、来源不可达、权限拒绝、撤回、删除、断源、唯一证据失效、旧队列 generation、跨 Project 相似内容、仅本地搜索用途。
- 查询覆盖：精确、同义、最近变化、确认 Decision、开放 Action、反馈后候选、冲突、不可达、权限排除、跨 Project、删除/撤回/断源、旧队列。

最小状态模型只是验证夹具：每个内容单元携带 Project、来源、精确 ArtifactVersion、Derivation、Link、Feedback、Authorization、确认、证据、冲突、墓碑、Source 状态和 queue generation。它用于验证不变量，不代表数据库表、正式 Schema 或 API。

所有文本均为人为构造的通用项目词汇，不含真实笔记、真实 Vault 名、真实路径、真实凭据或真实模型输出。

