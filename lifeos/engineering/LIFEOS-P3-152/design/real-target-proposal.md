# P3-152 精确真实目标与动作清单（待PM转用户一次性确认）

以下是从工程源代码推导的路径与方案，**没有执行exists/stat/read/open/Keychain查找**；不声称旧凭据配置实际存在或可用。

## 已经授权，不重复确认

- `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite`：程序内只读睡眠、步数、Apple运动时间及必要来源/时效元数据，不写、迁移或导入。程序不向Agent输出行内容或hash。
- `https://api.deepseek.com/chat/completions`：仅用户在真实App看到精确预览并亲自确认后的单次请求。禁止models/测试连接/后台/fallback/自动重发。

## 尚需精确授权

建议将以下未定目标一次性给用户确认，工程暂不执行。

1. 旧配置候选：`/Users/xxe/Documents/LifeOS-Source-Pilot-1/p3-148-provider.sqlite`。依据148 candidate/root_profiles.json 的source-pilot-1 root和provider_store.rs:79–91的固定文件名。只允许App读取provider_profile的模型列表/当前选择/加密envelope及必要pending-operation状态，不扫描该目录，不打开原source/capture库。文件/父目录元数据与实际存在的同名SQLite sidecars（-wal/-shm/-journal）限安全只读检查；不创建/写旧文件。建议仅在用户App主动选择“复用已有配置”时读取；不存在/不兼容时诚实失败，不探测其他位置。
2. 对应旧Keychain精确命名空间：默认macOS Keychain中service `com.lifeos.p3-148.aead-key.v1`，account仅上述envelope中`p3-148-key-`加32位小写hex的精确reference。仅App解密时读取该项密钥材料，不枚举、不写、不删除旧项。依据secure_credentials.rs:11/17/75–110及provider_store.rs:224–260。DB含encrypted API Key，Keychain保存AEAD密钥材料；不能仅复制DB就假定可解密。
3. 建议新增持久根：`/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1`，0700。创建`.lifeos-p3-152-owner.json`0600；仅用户批准后由App固定路径独占创建，发现外来根/文件拒绝覆盖。
4. 新会话库：该根`conversation.sqlite`及其必要SQLite sidecars，0600。保存用户问题/草稿、已确认最小披露、回答、状态与事务幂等元数据；不写回健康源。不创建第二记忆体系，沿用151表语义；业务库为本地明文SQLite，不能冒称内容已加密。
5. 新配置库：该根`provider.sqlite`及必要sidecars，0600。沿用既有加密持久方式；用户主动复用旧配置时仅程序内读取/复制必要模型配置和encrypted envelope，不改旧DB。旧envelope/AAD/reference保持可验证谱系，旧密钥不删除。用户也可直接在App输入Key建立本任务新加密配置；不在聊天索取。
6. 本任务新Keychain命名空间：service `com.lifeos.p3-152.aead-key.v1`、account `p3-152-key-<32lowerhex>`。仅本任务用户明确保存/替换/删除凭据时增、读、删本任务项；删除当前配置不得回退或重新导入旧Key。禁止修改148服务项。
7. 新根`.runtime`与`tmp`0700仅非内容锁/临时系统资源；不落盘请求/回答/Key明文临时文件。App包与编译产物仍在已授权152合成工程临时根，真实数据只进入新批准持久根。

旧配置复用是可选项；若用户仅批准新根与新凭据，152不用旧路径或旧Keychain。若用户指定另一旧配置路径，须给出精确目标，不能自行搜索。

## 工程差异与未决

- 148 provider_store.open使用READ_WRITE并依赖旧runtime.verify，不能直接调用来做上述只读复用；152需新的限目标只读适配，复用加密算法/Port与envelope语义。
- 模型从已有配置列表/选择或App本地输入选择；不执行models()，不强制旧testReceipt作为网络前置。每次确认绑定选定模型与凭据revision；变更使预览失效。
- 不默认将新的真实记录放到/tmp合成根，不默认打开旧库获取更多目录信息。
- 当前尚缺任务L3独立ABF精确路径/hash；已向PM报缺口。独立评审暂停例外按用户指示保留，不以此宣称安全Pass。
