# LifeOS 模型设置产品基线 V1

## 权威状态

- 状态：User Confirmed Forward Product Baseline
- 生效决策：D-0621
- 适用范围：所有继承或修改 LifeOS 模型设置、Provider、凭据和模型启用流程的后续任务
- 本基线只冻结产品行为与继承义务；具体实现候选、数据库 Schema、加密算法和工程基线仍须通过相应 Task Contract、L3 Evidence 与独立评审。

## 页面与导航

- 左侧既有窄 Icon Rail、页面空间关系和高保真设计保持不变。
- Settings 是弱化辅助入口；模型设置主区包含运行模式、连接配置、连接状态、当前启用模型和折叠高级参数。
- 保存、测试连接、选择模型、显式启用是分离动作；任何一步不得自动发送个人 Context。

## Cloud／Local Provider 可见选项

运行模式切换时，Provider 下拉列表必须同步切换，两个集合不得混合、复用状态或相互污染。

### Cloud

1. OpenAI
2. Anthropic
3. DeepSeek
4. Kimi
5. 自定义 OpenAI-compatible

### Local

1. Ollama
2. LM Studio
3. 自定义本地兼容服务

DeepSeek 与 Kimi 必须是用户可见的独立 Provider 选项。底层可以复用 OpenAI-compatible Adapter，但不得因此把二者隐藏在 Custom 文案中。Cloud Custom 与 Local Custom 必须具有不同的可见身份、endpoint 校验和状态空间。

## API Key 持久化

- Cloud API Key 由用户输入后，以密文写入 LifeOS 本地 SQLite 数据库并跨 App 重启保留。
- 产品不提供“仅本次会话”或“环境变量引用”作为用户设置选项。
- 数据库、设置文件、日志、Evidence、截图、Manifest、错误文本和聊天均不得出现 API Key 明文。
- UI 只显示固定掩码和有限尾号；不得泄露完整值、前缀、长度或可逆派生。
- 用户可以更新或删除已保存的 API Key。删除后旧密文、可用引用和运行时副本均不可继续使用。
- 加密密钥不得与凭据密文以可直接还原的形式共同存放在同一数据库。具体密钥管理方案必须在工程合同中明确并接受独立安全评审。
- Local Provider 默认不显示或索取 API Key；只有未来单独确认的本地兼容协议确有需要时才可修改此规则。

## 启用和调用不变量

- 切换运行模式、Provider、endpoint、API Key、模型或关键高级参数后，必须重新测试连接。
- 模型列表只来自刚刚成功完成的用户触发测试；不得后台发现或自动选择。
- 用户显式选择并启用模型后才可发送；不得自动 fallback、并用 Provider、后台发送或重试不确定请求。
- Pilot 首次真实发送后的 Provider 锁定属于该 Pilot 的安全约束，不得解释为删除设置页面中的其他 Provider 能力。

## 强制继承规则

- 后继任务必须逐项引用本文件并提交 `baseline lineage matrix`。
- 未经用户看到明确的“删除／替换能力差异”并单独确认，任何任务卡、ABF、工程候选、Review 或 Closure 不得删除、隐藏、合并、改名或弱化上述能力。
- 长任务卡中的笼统“确认完整合同”不得覆盖与本基线冲突但未单独展示的变化。
- 若发现回退，当前正向 Pass 必须立即撤回，历史资产只读保留，并在继续真实运行前完成同任务或明确后继任务的修复与独立复评。
