# P3-154 已有资料与持续理解的真实使用闭环

状态：Draft，尚未执行工程或真实操作。唯一用户结果：在现有完整App上，使用已接入资料与DeepSeek自然提问，必要时澄清；回答/纠正影响后续建议，拒绝/暂缓与重启连续，用户无需重复录入或手工组装上下文。

风险L3。独立评审按用户当前指示继续暂停，必须保留工程安全验证、PM验收及用户真实结果；不宣称Independent Pass。实现、回归、动态验证、同范围修复、安全切换和验收为一个任务，不拆微任务。本合同首次列出的真实读写及切换边界须用户一次明确批准；当前“继续下一步”仅覆盖同步与合同准备。

## 累积基线与责任

主责Codex工程，建议顺序复用已结束153的b3f6工程会话；PM负责账本与验收。不得双Agent修改同一候选，不指定模型。

离线最终基线：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-153/closure-1/candidate`，163文件，摘要`6e4e2be788d1af9d3f0c4bfffcab2dfebe68647f479066eb2a637193fb0a6a61`。只读合同输入为其上级FINAL_MANIFEST.json及153 PM最终验收。

真实接线只读依据：同工程树P3-152/settings-baseline-restoration/candidate与152最终PM验收。不得把153的真实feature拒绝简单删掉就视为完成；须比对152真实路径/凭据/来源/披露守卫与153持续理解增量，建立接线和兼容矩阵后逐项接回。最终交付为完整累积candidate/Cargo.toml构建，不是单项样机。

必须保留：Shell、设置与模型列表、保存/测试/选择/启用分离、密文持久与无Key TTL、来源管理/检索/原文、健康导入/查看、草稿、对话及最小披露。不重绘UI、不改成看板、不删旧功能。本轮只新增真实路径上的153行为与必要状态文案。

## 拟授权真实目标（仅App处理，不向Agent暴露正文）

| 精确目标 | 允许动作与限制 |
|---|---|
| `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/conversation.sqlite` | 复用现有表和协议，App读取有限相关内容并事务保存用户问题/回答/纠正/反馈/问题生命周期；保留原文历史，派生失效按153语义；不迁移/清空/重建库 |
| 同目录`provider.sqlite` | 复用已有加密凭据及非敏感配置；不复制到新库、不重置、不改TTL、不强迫重新输入Key。用户可手动使用现有设置功能 |
| OS Credential Port | 仅复用`com.lifeos.p3-152.aead-key.v1`及候选中与此服务绑定的既有account；工程先静态列明account，禁止枚举Keychain或回退历史144服务。缺密钥时明确阻断，禁止生成替代密钥覆盖旧密文 |
| 同目录`source-engine-v1/sources.sqlite`及既有artifacts/tmp/.runtime | 复用来源索引、片段与授权；只允许既有业务必要写入、锁与状态，不新建平行来源库、不复制全库 |
| `/Users/xxe/IT-obstain` | 仅App按既有SourcePort授权读取或在用户手动刷新时更新索引；无启动扫描、根外目标或外链跟随，不修改原文件 |
| `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite` | 本次真实验收仅只读查询既有睡眠/步数/Apple运动时间相关信息，不重新导入、不写入或迁移 |
| 父目录既有`.lifeos-p3-152-owner.json`、`.runtime/conversation.lock`及既有SQLite副文件 | 保留身份；仅正常运行锁和SQLite事务必要副文件，按旧守卫精确校验，不因新任务号强制改marker或重新建库 |

健康导入功能保持源码与合成回归，本次不操作`/Users/xxe/Downloads/导出.zip`，不重新导入已有资料。任何表结构、account或存储兼容差异先报PM，不探测更多目录、改owner或迁移。用户隐私内容不得进入Agent、日志、截图/AX、Evidence或hash；仅App内部按已授权既有内容完整性语义处理。Agent只看合成数据与固定非内容状态。

## 网络与交互

唯一真实Provider：DeepSeek `https://api.deepseek.com`。模型由已有设置和用户选择确定，不固定新模型名，不缩减Provider选项。仅用户手动测试读取/models及每次披露确认后的chat/completions；不自动测试、重试、fallback或调用其他Provider。用户阅读实际最小内容及接收方/模型后亲自确认，Agent不得代点。最多3来源+2状态/确认记忆、4096字节等原预算保持，不全量总结历史。

本地能回答的澄清不联网。回答、忽略、暂缓30分钟、拒绝、显式重新讨论沿153规则；沉默不是确认，临时状态不自动长期化。来源/状态失效及确认前/返回时过期须二次校验，晚到回答stale且不自动重发。旧回答过一次不阻止当日新的必要询问；有效替代资料仍存在则不问。

## 工程、运行及切换

拟定工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/`。唯一合成/构建根：`/private/tmp/lifeos-p3-154-real-continuity-v1`，独占创建0700及0600marker；不接管已有外来根。所有真实模式合成测试须使用明确隔离依赖，不可将任意路径/时钟覆盖暴露为生产接口。

先完成离线集成及安全回归，后切换。拟授权正常退出已确认身份的旧152 App，启动新完整App；旧bundle、源代码、数据库和凭据保留，不卸载、不删除、不强杀模糊PID。不同时持有同一库锁。切换前固定source/binary/bundle身份并记录非内容检查点；兼容检查或启动失败则停止新实例，数据未迁移的前提下允许恢复原152实例。不得把153旧合成App当新真实版。

本轮禁止清理任何真实/历史资产、导出/备份上传/同步个人数据、工具调用、麦克风、通知、后台采集、新来源或新领域。无风险关闭、产品/架构冻结、Stage切换或自动合并main。

## 验收合同

本L3逐行矩阵采用同目录`LIFEOS-P3-154_acceptance_basis.md`，用户确认后锁定其内容；独立评审暂停例外单列，不减少以下验证。

1. 163完整基线及152真实接线有差异和继承矩阵；Settings/Shell/所有既有链路不退化。
2. 合成既有Schema/密文/marker旧ID兼容，关闭重开保持；不执行生产迁移。
3. 直接提问自动使用有限获准上下文，不要求手工组装。
4. 已知信息不重复问，缺口最多一个；沉默/忽略/暂缓/拒绝/重开各自正确。
5. 回答与纠正更新适当状态，旧历史保留，过期/撤权/墓碑/有效替代规则正确。
6. 准备/确认/返回三处时效及版本变化失败关闭；一次确认只消费一次，失败不重发。
7. Key持久与掩码、设置生命周期、无Key日志/HTTP错误泄漏，缺密钥不覆盖；其他Provider不发送。
8. 独立进程重启与两离线Adapter连续性；真实重启不自动读模型/采集/发送。
9. 完整可构建App、安全单实例切换及可恢复检查点；窄窗只检受影响合成状态。
10. 用户实际完成一次提问→必要澄清或已有依据→回答/纠正→后续变化→重启保持，按现有内容选择最少操作；只要求成功/错误码反馈，不索取正文截图。没有该结果不宣称真实完成。

L3工程Evidence：逐行正负矩阵、hash/Manifest、关键失败守卫mutation、原历史保全，真实仅固定非内容收据与用户声明。无关已验证部分说明依据后复用；锁屏或GUI环境故障Paused—Resumable，只补影响阶段，不失效整包。普通同范围缺陷直接Closure，不新建微任务。范围内五类计数诚实；独立评审暂停不写作通过。

## 输入与交付

读取最新AGENTS、CURRENT_STATUS、本卡、验收依据、SESSION_REPORT_TEMPLATE；PM树`/Users/xxe/.codex/worktrees/5ed8/No.2`的152/153最终Review；上述两完整候选与最终报告。定向补读PM_OPERATING_MODEL/ROLE_MATRIX/STAGE_GATES/ACCEPTANCE_GOVERNANCE关于L3真实数据、权限、凭据及评审例外；CI_CD_GOVERNANCE及D-0648/0649；架构LifeOS架构基线V1.0.md的Ports/授权/Orchestrator、IA全局对话章节。不读无关历史或真实正文。

交付b3f6树`lifeos/deliverables/LIFEOS-P3-154_real_continuous_understanding_integration.md`，完整candidate、继承/影响/兼容矩阵、合成测试、Manifest、checkpoint、单命令复跑与切换说明。PM验收后由用户确认真实结果，安全代码文档才同步任务分支，真实资产不上传。新增真实目标/迁移/权限/关键Schema才另确认；不自动创建后继。
