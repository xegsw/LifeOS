# P3-152 真实阶段最小验收补充（供PM核对，尚未实际启用）

承接合成ABF A01–A09。用户已确认新配置方案；旧根/旧凭据复用未授权。独立评审暂停。此提案不自行冻结或宣称真实Pass。

| ID | 真实阶段增量与通过依据 |
|---|---|
| R01 | 编译时受控real模式，固定新根/marker/owner/权限；不存在则App严格create_new，不覆盖已有外来文件。真实根仅 /Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1。合成driver禁止real编译。模式不能由UI/IPC改写。 |
| R02 | 新根0700及.runtime/tmp0700；.lifeos-p3-152-owner.json、conversation.sqlite、provider.sqlite和必要sidecars0600。对话库按用户已知为未加密业务库；provider库仅加密Key。启动不导出内容、统计内容或计算真实库/正文hash。 |
| R03 | 健康读取只限 /Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite，经既有Reader的只读/no-follow/sidecar拒绝语义；不seed真实健康或会话演示数据。真实缺失、未知、过期不以合成数据填充。 |
| R04 | 新Keychain service com.lifeos.p3-152.aead-key.v1，account仅p3-152-key-32lowerhex，envelope严格同任务。只在用户App保存/替换/删除或已明确确认的发送解密时调用CredentialPort；页面读取仅元数据，无自动测试/模型查询。 |
| R05 | IPC仍使用已批准version4本地流程与version5披露/确认/设置；snapshot.mode从synthetic变为real，UI相应显式接收方/真实发送、隐私提示。没有新command/字段、核心表或跨任务凭据兼容。真实候选回答只允许Host ModelPort写入；本地澄清/状态不冒称模型回复。 |
| R06 | DeepSeek仅固定chat/completions；预览实际body、再次验证、单次消费及取消/超时/手动重试沿合成合同。只能用户逐次点击“确认发送给DeepSeek”。Agent不点击，不测试网络，不读模型列表。 |
| R07 | 真实stdout仅固定启动状态/固定错误码；关闭panic/core/stdout/stderr内容输出。禁Agent读取真实DB/文件内容、AX、截图、真实正文/Key/hash。启动工具只检查已构建二进制和固定状态，不检查真实根内容。真实成功以用户App体验确认，不要求截图。 |
| R08 | 新代码在synthetic构建补测无种子泄入real、mode/路径/端口选择与编译门禁；真实二进制只构建，不在自动测试或GUI运行。PM核对后才启动；成功启动记Awaiting user action，未经用户确认不记真实闭环完成。 |

## 精确工程与启动

增量候选：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/real-stage/candidate/；不改已交付合成candidate。
构建输出：/private/tmp/lifeos-p3-152-health-conversation-v1/real-target（只有工程二进制，无真实数据）。
真实App bundle：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Controlled.app，bundle ID local.lifeos.p3-152.controlled，窗口标题 LifeOS P3-152 - Controlled Conversation。
启动脚本：real-stage/tools/launch_controlled.py，仅PM核对后执行；直接启动固定二进制，仅接固定启动状态，不读真实目录/DB/Keychain、不取AX或截图。
现有synthetic App可保留但不混用；真实证据仅启动二进制身份、固定状态和用户操作确认。不捕获真实数据内容/日期/来源/回答，平台Keychain提示由用户处理。

## 需要PM核对的差异

真实分支加入固定root与provider.sqlite路径、禁止seed、snapshot.mode=real、真实文案及本地澄清回包标识；既有IPC字段和存储表保持不变。请核对本增量后允许实际启动。实际启用前不接触真实目标。
