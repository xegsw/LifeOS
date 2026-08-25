# LifeOS 架构基线 V1.0

> 状态：Architecture Baseline Draft
> 用途：固定当前已确认的逻辑架构、技术架构与核心 Port 设计，作为后续实现与架构演进输入。
> 注意：本文不自动修改既有项目治理文件中的 Frozen / Accepted / Risk 状态；若与正式主账本冲突，以正式主账本为准。

## 1. 架构目标

LifeOS 长期目标是成为以用户为唯一中心、可长期演进的个人操作系统 / 个人智能基础设施，而不是单一 AI 聊天应用。

核心原则：Local-first；核心领域与 UI、数据库、模型供应商、Agent、外部设备解耦；外部能力通过 Port / Adapter 接入；AI 不得绕过权限与用户确认；支持未来 Desktop、Web、Mobile、Voice、AR、Hardware、Agent 与智能家居扩展。

核心判断：如果未来替换模型、数据库、Agent、设备、供应商或 UI，LifeOS Core 不应大规模修改，理想情况下只替换 Adapter 或 Infrastructure 实现。

## 2. MVP 技术主闭环

```text
捕获 → 可靠保存 → AI 整理/派生 → 找回/今日/Project 上下文恢复 → 候选下一步 → 用户确认/编辑/拒绝/忽略 → Feedback 沉淀
```

架构底线：原始内容与 AI 派生分离；Source 与 Artifact 分离；重要 AI 输出可追溯；AI 不替用户确认事实、决定、承诺或重大动作；证据不足允许无建议；V1 本地/单设备优先；SQLite + FTS-first；向量搜索不是 MVP 前提。

## 3. 逻辑架构

```text
Interaction Layer
Desktop | Web | Mobile | Voice | AR | Hardware
        ↓
Application Layer
Capture | Today | Project | Search | Feedback | Authorization
        ↓ (复杂智能请求)
LifeOS Orchestrator
Intent | Context | Planning | Routing | Confirmation
        ↓
Core Domain + Core Capabilities
        ↓
Ports / Contracts
Repository | Search | Source | Model | Agent | ...
        ↓
Adapters
SQLite | FTS5 | Obsidian | OpenAI | Claude | Codex | GitHub | Calendar | Home Assistant | ...
        ↓
Infrastructure
SQLite | Files | OS APIs | Workers | Future Cloud
```

### Interaction Layer
只负责用户交互与展示，不承载核心业务逻辑。长期入口包括 Desktop、Web、Mobile、Voice、AR Glasses、Hardware Console。

### Application Layer
负责确定性 Use Case，例如 Capture、Project、Today、Search、Feedback、Authorization。确定性操作不默认交给 AI。

### LifeOS Orchestrator
负责意图理解、Context 组装、任务拆解、能力路由、Model / Agent 协调、权限与确认流程协调、输出汇总。Orchestrator 不拥有核心业务数据。

### Core Domain
继续继承既有核心领域语义：Project、Artifact、Source、Assertion、Decision、Action、Event、Derivation、Feedback、Authorization、AuditEntry、Link。Core Domain 不依赖 SQLite、Tauri、OpenAI、Claude、Codex 或其他外部供应商。

### Core Capabilities
Search、Context Engine、Permission、Audit、Automation、Notification、Proactive Engine、Export / Recovery、Background Jobs。

Proactive Engine 长期输出边界：Silence / Surface / Notify / Execute；Execute 必须再次经过 Authorization。

## 4. 技术架构 V1

总体模式：**Local-first Modular Monolith + Hexagonal Architecture + Internal Event-driven + Adapter/Plugin Extension**。

### Desktop
目标桌面栈：Tauri 2 + React + TypeScript + Vite。

Rust / Tauri 负责 Host、Security Boundary、OS Capability、IPC、文件系统边界、窗口/进程生命周期和 Native Integration。TypeScript 承载 LifeOS Domain、Application、Orchestration、Capabilities、Ports 与大部分 Adapter。核心产品逻辑不整体绑定到 Rust。

### Local Data
SQLite 是 V1 本地权威数据 / 控制账本；FTS5 是第一搜索路径；派生数据可失效、删除和重建；向量能力后置。业务代码通过 Repository Ports 访问领域数据，不直接依赖 SQL。

### Files
文件通过 FilePort / File capability 管理。数据库保存 identity、metadata、source、hash、path/reference、authorization 等必要信息，避免核心业务依赖具体文件系统。

### Background Jobs
V1 不以 Kafka、Kubernetes、Redis 为前置。当前可采用本地 job table + Background Worker + Persistent Outbox；未来通过 JobPort 替换为 Postgres Queue、Redis、Temporal 等实现。

### Internal Events
从早期保留 Domain Event 语义，例如 ArtifactCaptured、ArtifactUpdated、FeedbackConfirmed、AuthorizationRevoked、ActionCompleted、ProjectContextChanged。V1 可采用 In-process Event Bus，未来演进为 Persistent Outbox / Distributed Event Bus。

### Future Server
当前不把服务端作为 MVP 前置，只预留 SyncPort / API 边界。Fastify、PostgreSQL、对象存储、Redis、Temporal 等属于未来候选实现，不成为 Core 不可替换依赖。

## 5. 第一批核心 Ports

### Repository / Storage Ports
不暴露 SQL、SQLite handle 或表名；接收/返回 Domain Object 或明确 Domain DTO；查询按业务语义命名；事务边界由 Application 定义、Adapter 实现；一对象一 Repository，不采用万能动态 Repository。

候选：ProjectRepository、ArtifactRepository、SourceRepository、AssertionRepository、DecisionRepository、ActionRepository、EventRepository、DerivationRepository、FeedbackRepository、AuthorizationRepository、AuditRepository、LinkRepository。

### Search Port
向上层提供统一搜索能力，不暴露具体搜索实现。SearchResult 至少表达 objectId、objectType、projectId?、sourceId?、excerpt、evidenceRefs、score、matchedBy。

Search 是派生能力，不是权威事实来源。FTS / Vector / Metadata / Rerank 属于 Adapter 实现细节。搜索结果消费前必须重新检查 Authorization、Source validity、version、tombstone、generation 等权威状态。

### Source Port
负责连接状态、内容发现、内容读取、变化同步，把外部世界转换为标准化、可追踪输入。SourceItem 可包含 externalId、sourceId、sourceType、title、content/contentRef、mimeType、createdAt/updatedAt、parentRef、metadata、contentHash。

Source Adapter 不直接写 Core Domain。正确路径：Source Adapter → SourceItem → Ingestion Application Service → Authorization → Domain → Repository。Source 默认最小权限、默认只读；外部写操作使用独立 Capability / Authorization。

### Model Port
Model 是推理/生成能力，不是 Agent。核心能力：generate、generateStructured、stream、embed。模型选择通过 ModelRouter 完成，业务代码不写死供应商品牌。

重要调用保留 modelId、provider、requestId、startedAt/finishedAt、usage、inputRefs、outputId 等标准元数据；重要 AI 输出进入 Derivation。Model 不拥有执行权限，不直接操作 Repository、文件、日历或设备。

### Agent Port
Agent 是接受目标、使用工具/环境执行任务并返回过程与结果的外部执行者。

AgentTask 至少表达 taskId、goal、taskType、contextRefs、allowedCapabilities、authorization、constraints、expectedOutput、timeout。

AgentResult 至少表达 taskId、status、summary、artifacts、actionsTaken、evidence、errors、warnings、startedAt/finishedAt、agentId/agentVersion。

权限跟随任务而不是永久跟随 Agent；AgentRouter 根据 capability 选择 Agent；Agent 不得绕过 LifeOS Authorization；重要结果进入 Artifact / Derivation / Event / AuditEntry。

## 6. Model 与 Agent 边界

```text
Model = 输入 → 推理/生成 → 输出
Agent = 目标 → 使用工具/环境执行 → 过程 + 结果
```

二者保持独立 Port。具体 Agent Framework、模型厂商 Agents API 或某个 Agent SDK 不能成为 LifeOS Core 的架构中心，只能作为 Adapter / Runtime 实现。

## 7. Adapter 原则

长期形成统一 LifeOS Adapter / Capability Contract。候选类型：ModelAdapter、AgentAdapter、SourceAdapter、StorageAdapter、SearchAdapter、FileAdapter、DeviceAdapter、CalendarAdapter、NotificationAdapter。

候选实现：SQLiteAdapter、FTS5Adapter、LocalFileAdapter、ObsidianAdapter、OpenAIAdapter、ClaudeAdapter、CodexAdapter、GitHubAdapter、CalendarAdapter、HomeAssistantAdapter、XiaomiAdapter。

未来可逐步形成 `@lifeos/sdk` 或等价插件 SDK，使第三方能力接入 LifeOS 而不修改 Core。

## 8. 目标工程结构

```text
lifeos/
  apps/
    desktop/
      src/
      src-tauri/
    web/       # future
    mobile/    # future

  packages/
    domain/
    application/
    orchestrator/
    capabilities/
    ports/
    adapters/
    contracts/
    sdk/

  tools/
    migrations/
    dev/

  spikes/
    ...
```

这是目标结构，不要求立即迁移或删除现有 Spike、Evidence 和治理资产。

## 9. 当前固定与后置边界

### 架构基线固定
Local-first；Modular Monolith；Hexagonal / Ports & Adapters；Domain 与 Infrastructure 分离；Application Layer；独立 Orchestrator；Model / Agent 分离；TypeScript Core；Tauri 2 桌面方向；React + TypeScript UI；SQLite V1 本地权威数据；FTS-first；派生可重建；外部能力 Adapter 化；Authorization 位于重要消费/执行路径。

### 暂不冻结实现细节
SQLite Schema；Domain→Table 映射；IPC command signature；Tauri capability 具体配置；FTS 表结构/PRAGMA；Adapter API 最终函数签名；Model/Agent 具体供应商；Vector DB；Redis；Temporal；PostgreSQL Cloud；云同步协议；Smart Home protocol；AR 技术方案；生产 SLA。

## 10. 下一条架构验证主链

```text
UI
 ↓
CaptureApplicationService
 ↓
Domain
 ↓
RepositoryPort
 ↓
SQLiteAdapter
 ↓
Domain Event
 ↓
Search / Context
 ↓
Orchestrator
 ↓
ModelPort
 ↓
Derivation / candidate Action
 ↓
User Confirmation
 ↓
FeedbackApplicationService
 ↓
Feedback + Audit
```

后续优先用这条真实 MVP 主链验证架构，而不是继续无边界增加抽象层。
