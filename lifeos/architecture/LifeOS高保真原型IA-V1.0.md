# LifeOS 高保真原型 IA V1.0

> 状态：Prototype IA Baseline Draft
> 用途：固定当前已确认的“以人为主体”高保真原型信息架构、Global Shell、核心页面集合与交互原则。
> 注意：本文用于后续高保真原型设计，不自动修改既有项目治理文件中的 Frozen / Accepted / Risk 状态。

## 1. 领域规则

本原型不冻结“一共有多少个领域”，冻结以下四条原则：

1. **Person 是一级主体，Domain 是长期生活视角，Project 只是领域内对象。**
2. **1.0 广泛承接人生数据，但只在工作和健康两个领域做深度智能。**
3. **新领域一次只激活一个，通过数据、价值、反馈和安全关卡后再加入。**
4. **首页按人的整体优先级分配注意力，不按领域平均发卡片。**

Domain 是理解 Person 的长期视角，不是固定数量的一级 App。新 Domain 的“激活”意味着形成相应的深度理解、主动策略、反馈机制和安全边界，而不是简单增加一个导航入口。

## 2. 产品世界观

```text
Person
  ├─ Domain：长期生活视角
  │    ├─ Work（1.0 深度智能）
  │    ├─ Health（1.0 深度智能）
  │    └─ Other Life Data（广泛承接，暂不深度智能）
  │
  ├─ Context：当前正在经历、推进或持续关注的事情
  │    ├─ Project
  │    ├─ Period / Program
  │    ├─ Goal-related Context
  │    ├─ Life Event
  │    └─ Observed Context
  │
  └─ Memory：长期记忆与证据

Global AI 贯穿所有页面，并可展开为 AI Workspace。
```

## 3. 一级信息架构

一级导航保持极简：

- Today
- Me
- Contexts
- Memory
- Settings（辅助区，弱化）

AI 不作为普通一级 App 与上述页面并列，而采用两种形态：

- **Global AI**：所有页面永久可达、上下文感知的自然语言交互层。
- **AI Workspace**：Global AI 的深度展开形态，用于复杂分析、跨领域问题、规划和未来 Agent Task。

Work、Health、Project、Task、Calendar、Agent 不进入一级导航；它们是围绕 Person 的视角、对象或能力。

## 4. Global Shell

桌面端基础结构：

```text
┌────────────┬──────────────────────────────────────────────┐
│            │                                              │
│ Today      │                                              │
│ Me         │                 当前页面                     │
│ Contexts   │                                              │
│ Memory     │                                              │
│            │                                              │
│ Settings   │                                              │
│            ├──────────────────────────────────────────────┤
│            │ ✦ 问 LifeOS…                      🎙  +  ↑  │
└────────────┴──────────────────────────────────────────────┘
```

### Global AI 原则

- AI 全局可达，不要求用户离开当前页面。
- AI 自动继承三层 Context：Person Context、Page Context、Selection Context。
- 当前 Context 对用户可见、可检查、可移除。
- 简单对话从右侧渐进展开，不强制跳转。
- 复杂任务可进入完整 AI Workspace。
- AI 输出可以形成 Observation、Suggestion、candidate Action、candidate Decision、Plan、关联发现和未来 Agent Task。
- AI 输出不能替用户完成确认；候选对象必须由用户确认、编辑、拒绝或忽略。

Global AI 是 LifeOS 的自然语言命令与理解入口，不是客服气泡。

## 5. Today

核心问题：**此刻什么最值得这个人的注意？**

Today 不展示领域 Dashboard，不按 Work / Health / 其他领域平均分卡片。

信息优先级：

1. **整体状态**：一句克制的全局状态理解；允许“今天没有特别需要处理的事情”。
2. **Today's Focus**：最多一个当前最值得推进的重点，并说明“为什么现在值得做”。
3. **LifeOS noticed**：主动引擎发现的可能值得关注的变化、异常或关联；必须区分事实、观察与推断，允许证据不足。
4. **Today / 已确认安排**：仅展示用户已经确认的 Action / Commitment / Schedule；未确认 AI 候选不得混入。
5. **Recent**：最近有意义的痕迹，用于快速恢复 Context，不做信息流。
6. **Global AI Bar**：永久存在。

关键原则：

- Today's Focus 最多一个，不为填充页面强行凑建议。
- 每个重要建议都应可查看依据。
- “没有什么需要你操心”是合法且有价值的首页状态。
- 首页按 Person 的整体优先级分配注意力。

## 6. Me

核心问题：**LifeOS 现在如何理解这个人？**

Me 不是 Profile / 个人资料页，而是 Person 的长期状态视图。

主要结构：

1. **Current Self / 你现在**：当前阶段和整体状态的动态摘要。
2. **当前关注**：当前主要投入和关注对象，以状态表达，不伪造精确 KPI。
3. **长期视角 / Domains**：从 Work、Health 等已激活 Domain 看 Person 的长期状态。
4. **其他人生数据**：明确显示“已承接，但尚未启用深度智能”。
5. **最近变化**：Person 最近发生的有意义变化。

所有 LifeOS 对 Person 的理解都必须：

- 可查看依据。
- 标明是用户事实还是 AI Derivation。
- 可由用户确认、纠正、拒绝或撤回。

Person 是系统权威主体，不是被静默画像的对象。

## 7. Contexts

Context 定义：**这个人当前正在经历、推进或持续关注的一件事情的上下文容器。**

Project 是 Context 的一种，但 Context 不等于 Project。

示例：

- LifeOS 产品开发：Work · Project
- 训练恢复：Health · Ongoing / Program
- 最近睡眠：Health · Observed Context
- 搬家：Life Event

Contexts 首页不采用 Kanban，也不按 Domain 分栏，优先按照 Person 与事情的当前关系组织：

- Active / 正在进行
- Watching / 持续关注
- Past / 已结束

### Context Detail

稳定信息结构：

1. **现在**：Context 当前状态。
2. **Next**：当前已确认下一步。
3. **最近发生**：时间线式重要变化。
4. **LifeOS understands**：AI 对当前 Context 的理解，可追溯、可反馈。
5. **Related / Evidence**：相关记录、Decision、Action、Source 等。
6. **Global AI**：自动继承当前 Context。

Context 可以由 LifeOS 提议创建，但不能静默创建。建议生命周期语义：Candidate → 用户确认 → Active → Watching → Closed；UI 可使用更自然的“正在进行 / 持续关注 / 已结束”。

## 8. Memory

核心问题：**LifeOS 关于我的这些认识，到底从哪里来？**

Memory 是长期记忆与证据浏览器，不是笔记软件或文件夹知识库。

默认组织不以文件夹为底层世界观，而通过 Person、Domain、Context、Source、Time、Link 建立关系。

Memory 必须视觉和语义上区分：

- 用户原文
- 用户已确认事实
- AI Observation
- AI Inference
- Decision
- Derivation
- 外部 Source

### Memory Detail

重要 AI 记忆 / 观察详情至少应展示：

- 内容与类型
- 当前确认状态
- LifeOS 为什么这么认为
- 输入证据和来源
- 生成时间
- 处理范围 / Domain
- 用途
- 全部输入入口
- 用户反馈：准确 / 不准确 / 纠正

Memory 搜索不仅返回文档列表；对于“我之前为什么这么决定”类问题，应优先恢复 Decision、理由和原始证据链。

Memory 可以很深，但默认页面应保持安静；它的价值是长期可信、可追溯和可恢复，而不是提高访问频率。

## 9. AI Workspace

AI Workspace 是 Global AI 的深度展开态，不是独立聊天产品。

推荐桌面结构：

```text
┌────────────┬──────────────────────────────┬────────────────────┐
│ Navigation │ Conversation + Work          │ Context Inspector  │
│            │                              │                    │
│ Today      │ AI 判断 / 分析               │ Person             │
│ Me         │ Evidence                     │ Domains            │
│ Contexts   │ Suggested Action             │ Contexts           │
│ Memory     │ Decision Candidate           │ Sources            │
│            │ Plan / Agent Task            │ Permissions        │
│            │                              │                    │
│            │ ✦ 继续问 LifeOS…             │ Manage Context     │
└────────────┴──────────────────────────────┴────────────────────┘
```

### Conversation + Work

对话中可直接嵌入 LifeOS 原生对象：Observation、Evidence、Suggested Action、Decision Candidate、Plan、未来 Agent Task。对话应能推进 LifeOS 状态，而不是聊完即消失。

### Context Inspector

用户始终可见本次 AI 使用了什么：

- Person
- Domains
- Contexts
- Memory / Sources
- Permissions

用户可以临时移除某类 Context，例如“这次不要参考健康数据”，系统应据此重新回答。

### 跨领域智能

MVP 1.0 重点验证 Work + Health 的跨领域理解。AI 应区分：观察到什么、没有观察到什么、哪些只是推断、依据是什么、建议如何验证；避免无证据的泛化建议。

### Future Agent Task

Agent 不作为一级导航。未来 Agent Task 在 AI Workspace 中表现为一种执行能力：显示执行者/能力、任务目标、允许权限、执行状态、证据、变更、接受/撤销等。

Agent 不能绕过 LifeOS Authorization。

## 10. 页面集合

第一轮完整核心页面集合：

1. Global Shell
2. Today
3. Me
4. Contexts
5. Context Detail
6. Memory
7. Memory Detail
8. Global AI Side Panel
9. AI Workspace

高保真第一批优先制作：

1. **Global Shell**
2. **Today**
3. **Me**

第二批：Contexts + Context Detail。

第三批：Memory + Memory Detail。

第四批：Global AI Side Panel + AI Workspace。

## 11. 原型必须跑通的关键流程

### Flow A：打开 LifeOS

Today → 查看整体状态 → Today's Focus → 查看依据 → 进入 Context → 确认 / 调整下一步。

验证：主动智能、注意力分配、证据链。

### Flow B：快速捕获

任意页面 → Global AI / Quick Capture → 输入文本/链接/文件 → 保存原文 → LifeOS 提议关联 Domain / Context → 用户确认或忽略 → 进入 Memory / Context。

验证：长期外脑、原文保护、来源与 Context 关联。

### Flow C：跨领域问题

Global AI / AI Workspace → Work + Health Context → 查看依据 → AI 区分 Observation / Inference → 给出候选建议 → 用户确认 Action / Feedback。

验证：Person 主体、跨领域理解、可信 AI。

### Flow D：Context 恢复

Contexts → 进入某 Context → 查看“现在 / Next / 最近发生 / LifeOS understands / Evidence” → 继续工作。

验证：上下文恢复。

### Flow E：追溯记忆

Memory / Global AI → 提问“为什么当时这么决定” → Decision → 理由 → Source / 原始记录 → 用户核对。

验证：长期记忆与可追溯性。

## 12. 视觉与体验方向

- 安静、克制、个人空间感，不做企业后台或运维 Dashboard。
- 避免卡片墙、KPI 墙和领域平均分配。
- AI 不使用“神谕式”视觉；重要结论旁边始终允许查看依据。
- AI 不确定时明确表达证据不足。
- 页面允许大量留白；没有问题时页面可以很空。
- AI 候选与用户确认内容必须视觉可区分。
- 原文、事实、AI 观察、AI 推断、Decision 应具有清晰的信息身份。

## 13. 当前高保真下一步

基于本 IA，下一步进入第一批高保真设计：

**Global Shell + Today + Me**。

第一轮高保真应优先验证信息层级、Person 主体感、Global AI 常驻方式、AI/用户权威区分和 Today 注意力分配，而不是追求完整功能数量。
