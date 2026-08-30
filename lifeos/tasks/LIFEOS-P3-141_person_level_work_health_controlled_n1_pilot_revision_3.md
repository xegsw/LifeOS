# LIFEOS-P3-141｜模型设置权威基线恢复与受控 Pilot Closure — Revision 3

## 状态

- 同一任务：LIFEOS-P3-141
- 风险等级：L3；Mandatory Independent Review
- 状态：Closure Cycle / Phase C Paused / User Confirmed / Product Not Frozen
- 生效决策：D-0621
- 权威产品输入：`lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
- 被替代正向依据：Revision 2、ABF-P3-141-v2及D-0620当前正向效力；全部只读保留。

## 修订原因

PM在P3-136把用户要求的“API Key本地数据库加密永久保存”错误转写为“仅会话内存／环境变量引用”，并把高保真图中的“密钥已保存”错误认定为不继承占位。用户随后明确纠正且工程候选曾实现加密持久化，但账本和Frozen ABF未同步。P3-141又继承该错误，并将DeepSeek／Kimi合并隐藏在Custom文案中。两项均属于已确认产品能力回退。

## 唯一结果

在不改变P3-141 Person-level Work＋Health、20 IPC总量、Pilot-6数据额度、最小披露、Health安全和单Provider真实发送约束的前提下，恢复模型设置权威基线：

1. Cloud Provider用户可见选项严格为OpenAI、Anthropic、DeepSeek、Kimi、自定义OpenAI-compatible。
2. Local Provider用户可见选项严格为Ollama、LM Studio、自定义本地兼容服务。
3. Cloud／Local的Provider、endpoint、测试状态、模型列表和启用状态分离，不得串用。
4. API Key以密文写入本地SQLite并跨重启保留；支持更新、删除；UI只显示掩码和有限尾号。
5. 不提供“仅本次会话／环境变量引用”产品选项。
6. 保存→测试→选择→启用→发送保持分离；无自动fallback、后台发送或隐式重试。

## IPC与实现边界

- Runtime总数仍为恰好20项。
- 原`set_ai_provider_session_credential`不再是有效产品合同；在保持总数20的前提下，以固定窄`save_ai_provider_credential`替换，DTO只允许`store_or_update`／`delete`，不得暴露任意SQL、path、secret readback或generic credential能力。
- 其他19项IPC名称和语义不得回归。
- API Key密文写入Pilot数据库；明文只允许存在于完成当次加密／调用所需的最短进程内存生命周期，不得持久化、回显或进入Evidence。
- 加密密钥不得与密文以可直接还原形式共同存放在同一DB。工程必须在接触真实Pilot或真实凭据前提交明确的本地密钥管理与失败关闭设计；任何新增Keychain／Vault／系统权限访问必须按其实际边界另行确认。

## 允许与禁止范围

- 允许写入：`lifeos/engineering/LIFEOS-P3-141/`；新的Revision-3合成临时根与独立评审根须在工程投递前唯一固定。
- Revision 2候选、Review、Evidence、Manifest、receipt、PM Review和全部失败历史只读。
- Closure期间禁止对Pilot-6、capture.sqlite、真实文本、Health值、真实Provider、API Key或网络进行任何access／exists／stat／hash／read／write／create／cleanup。
- 不改变Pilot根、数据额度、Memory／State／Context语义、Health安全、风险、产品冻结或Stage状态。
- Phase C在Revision-3合成工程、全新隔离独立评审和PM复核全部Pass前保持暂停。

## Acceptance Contract

| ID | 冻结结果 | 必须Evidence | 级别 |
|---|---|---|---|
| MS-01 | Cloud五个可见选项精确且DeepSeek／Kimi独立 | DOM／actual-Tauri／mutation | P0 |
| MS-02 | Local三个可见选项精确 | DOM／actual-Tauri／mutation | P0 |
| MS-03 | Cloud／Local配置与状态完全隔离 | mode-switch lifecycle matrix | P0 |
| MS-04 | API Key密文入库、明文零持久化 | DB字节／字段／taint反例，不记录真实Key | P0 |
| MS-05 | 重启后凭据仍可用且不要求重贴 | clean restart synthetic-secret matrix | P0 |
| MS-06 | 更新／删除闭合，删除后旧凭据不可用 | lifecycle／stale／rollback matrix | P0 |
| MS-07 | 加密密钥与密文分离，错误／篡改写前关闭 | key-management design + mutations | P0 |
| MS-08 | 保存→测试→选择→启用→发送分离 | state-machine + negative controls | P0 |
| MS-09 | 20 IPC精确，凭据IPC完成窄替换，其余19项无回归 | source／runtime enumeration | P0 |
| MS-10 | 三档actual-Tauri保持既有高保真设置页与Rail | direct PID native Evidence | P0 |
| MS-11 | 已确认基线逐项谱系闭合，回退mutation必失败 | baseline lineage matrix | P0 |
| MS-12 | Pilot-6零触达、历史保全、临时根精确清理 | prohibited attestation／Manifest／cleanup | P0 |

Pass公式：MS-01～12全部PASS；P0／P1／Unknown／Not Implemented均为0；不同全新隔离独立评审Pass；PM复核后才可恢复Phase C。
