# ABF-P3-141-v3｜模型设置权威基线恢复

## 冻结信息

- 任务：LIFEOS-P3-141
- ABF：ABF-P3-141-v3
- 生效决策：D-0621
- 状态：Frozen / Supersedes ABF-P3-141-v2 for positive acceptance
- 用户确认：`lifeos/tasks/LIFEOS-P3-141_model_settings_baseline_user_confirmation.md`
- 权威产品基线：`lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
- 固定输入清单：`lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory_revision_3.json`
- v1／v2 Task、ABF、候选、Review、Evidence和Decision均只读保留，不改写。

## 冻结不变量

| ID | 不变量 | 预期 |
|---|---|---|
| ABF3-M-001 | Cloud Provider集合 | OpenAI、Anthropic、DeepSeek、Kimi、自定义OpenAI-compatible五个独立可见选项 |
| ABF3-M-002 | Local Provider集合 | Ollama、LM Studio、自定义本地兼容服务三个独立可见选项 |
| ABF3-M-003 | 模式隔离 | Cloud／Local配置、endpoint、测试、模型和启用状态不串用 |
| ABF3-M-004 | 凭据持久化 | API Key密文写入本地SQLite，跨重启保留，可更新、删除 |
| ABF3-M-005 | 明文排除 | DB／设置／日志／Evidence／截图／Manifest／错误／聊天无明文 |
| ABF3-M-006 | 密钥管理 | 密钥与密文不以可直接还原形式共存于同一DB；篡改与不可用失败关闭 |
| ABF3-M-007 | 用户流程 | 保存、测试、选择、启用、发送分离；无fallback／后台发送 |
| ABF3-M-008 | IPC | 恰好20项；凭据IPC窄替换，其他19项保持 |
| ABF3-M-009 | 视觉 | 既有高保真Rail、布局、三档响应式不回退 |
| ABF3-M-010 | 继承防回退 | baseline lineage逐项通过；删除／合并／会话化mutation均被捕获 |
| ABF3-M-011 | 独立性与历史 | 新候选、新Manifest、新独立评审；v1／v2历史只读 |
| ABF3-M-012 | 数据边界 | Closure期间Pilot-6零触达；只用全新合成凭据夹具与临时根 |

## Pass公式

ABF3-M-001～012全部PASS；P0／P1／Unknown／Not Implemented均为0；任何P2不得影响凭据机密性、持久性、Provider集合、状态隔离、用户控制、20 IPC或历史可信度。只有全新隔离独立评审和PM复核后才可恢复Phase C。
