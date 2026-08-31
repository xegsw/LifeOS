# P3-136 IA 与架构基线调和矩阵

本文件只表达 P3-116 原型的产品层调和，不修改或冻结任何 Core Domain、Repository、Schema/API、架构或历史资产。

| 议题 | 历史／架构事实 | P3-116 产品层表达 | 当前处置 | PM 待决策 |
|---|---|---|---|---|
| 一级主体 | 架构目标是用户为唯一中心；历史 V1 以 Project 恢复为第一场景 | Person 是一级主体，Today 按 Person 整体注意力分配 | 以 Person 作为 IA 的根，不否定 Project 的 Core Domain 身份 | 无 |
| Project 与 Context | Core Domain 继续有 `Project` 对象、Repository 与 `ProjectContextChanged` 事件 | Project 是 Context 的一种类型；Context 还覆盖 Period/Program、Goal-related、Life Event、Observed Context | “产品导航层级”与“Core 对象类型”分层；不把 Context 写成新 Core 实体或 Schema | 无 |
| Today 完成定义 | 历史 Today/PRD 是 Project 恢复的工作领域基线，曾允许 0–1 候选下一步与 1–3 呈现限制 | 最多一个 Today's Focus；Today 还包含整体状态、noticed、确认安排和 Recent | D-0468 已明确旧完成定义不再是当前候选；保留历史 Frozen 事实，只做新 ABF 任务 | 无 |
| 一级 IA | 历史 IA 的 Today/Inbox/Projects/找回/数据权限是旧工作领域输入 | 仅 Today、Me、Contexts、Memory；Settings 弱化；AI 为全局层 | 不把 Domain、Project、Task、Calendar、Agent 变成一级 App | 无 |
| Memory 与领域对象 | Core Domain 有 Source、Artifact、Decision、Action、Derivation、Feedback、Authorization、AuditEntry、Link | Memory 是这些身份与证据关系的浏览器；显示用户原文、确认事实、Observation、Inference、Decision、Derivation、External Source | 产品页不宣称具体持久化映射或 DB 表；身份可追溯合同与 Core 原则一致 | 无 |
| Global AI／Orchestrator | 架构定义 Orchestrator 负责 Context 组装、确认和能力路由；Model／Agent 为独立 Port | Global AI 展示 Person/Page/Selection Context；Settings 弱入口承接可替换 Provider 的保存、加密本地 SQLite API Key、连接测试与启用 | UI 仅通过固定 IPC 到 App/ModelPort；Cloud API Key 仅能显式保存、更新或删除，跨重启保留且不回显；每次模型请求须由用户显式发送，输出仅为 Observation/Suggestion，不自动创建 Action | 无 |
| Work + Health | P3-113/P3-114 形成的 Not Frozen 人本双领域候选已获采纳 | Work 与 Health/Fitness 可有深度智能；其他 Domain 只承接、未启用 | 原型不外推健康建议、诊断或真实价值；第三 Domain 的四 Gate 未满足时关闭 | 无 |
| 核心信任边界 | Frozen L1、AI 信任原则要求身份分离、用户确认、证据与撤回 | 所有候选对象提供确认／编辑／拒绝／忽略／纠正；移除 Context 不改持久事实 | 仅为 in-memory UI 演示；不替代 Authorization／Feedback／Audit 实现 | 无 |
| 历史 P3-115 | P3-115 原 ABF 下 PM Pass 是历史事实，未被采纳为当前目标 | 本候选改用新 IA 和 ABF；不复制旧页面完成定义 | 旧目录、Evidence、Review 与交付物严格只读 | 无 |

## 调和结论

没有发现需要覆盖 Frozen 产品宪法、AI 信任原则、技术架构 V1 或历史事实的不可调和冲突。P3-136 将可替换 Provider 保持在 ModelPort 适配层：它不是新的 Core 实体、Repository、Schema/API 或权限模型。任何真实 Provider 激活、凭据持久化、网络策略调整、风险关闭或冻结结论均超出本任务并须由 PM 新建任务决定。
