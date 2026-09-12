# LIFEOS-P3-148 来源支撑的 AI 对话：合同设计阶段报告

2026-09-08。执行Agent：Codex。状态：**当前只读合同设计已完成，完整任务Partial / 等待PM合同核对**。当前风险L0，完整结果L3；本阶段ABF N/A。这不是完整任务Pass、工程Pass、真实能力启用或Independent Pass。

## 执行摘要

1. 固定输入为b3f6提交`5c26431ca43d68b77ab3d91a715dd59444a62e2e`的P3-147 candidate/design/最终报告/非内容状态；本轮未修改147，未构建、测试或启动App，未探测真实/旧临时根、DB、来源或凭据，未访问网络。
2. 已逐项核对25 IPC。推荐保留旧契约，新增独立`send_source_ai_request`使总数26，并给11项既有命令新增严格v3操作；全部DTO、返回与固定错误码具体列出，当前仅提案。
3. 复用records/drafts/packets/derivations/feedback等已有业务表，**不新增对话表、不先迁移真实库**。现有200字/三条限制、隐式DDL、snapshot和幂等不能直接套新会话；明确新增JSON语义及专用已有库打开路径。推荐单独新provider库2表保存配置/密文与非秘密操作日志。
4. 保持AES-256-GCM密文跨重启持久化，使用新的148 OS service/reference；不链接旧144/145命名空间。明确保存→测试→选择→启用→每次发送，处理OS/DB跨系统失败和定向清理。
5. 明确检索→精确预览→确认→发送→回答→引用→纠正→重启；不确定发送不自动重试。完整T01–T25离线矩阵、F01–F07纯虚构夹具、拟复跑/恢复入口、一次真实批准清单已交付，全部动态结果Not Run。

## 五项交付物

以下均Created，仅位于当前允许的design目录：

- [01 IPC、DTO与错误码](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/01-ipc-contract.md)
- [02 存储映射与无旧库DDL方案](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/02-storage-mapping.md)
- [03 凭据与Transport设计](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/03-credentials-and-transport.md)
- [04 状态机与幂等](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/04-state-machine.md)
- [05 验收与一次批准清单](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/05-validation-and-approval.md)

## 事实、建议与未知

PM两项自洽性补正已在原包完成：①启动/被动读取零OS访问，仅本地激活后显示待恢复；OS恢复仅用户明确恢复/保存/删除触发，01显式补列拟`recover_credentials` operation，仍26IPC/11项v3命令。②`p3-148-session.lock`只约束多个148实例，不能约束147或自动阻止重开；用户先关闭147并在148使用期间不重开是操作前提，跨版本并发安全未证明。02–05已同步存储、状态机、T20/T23/T25及一次批准清单。不修改147、不扩大进程探测。本次为同包设计一致化，不是Rework或动态重跑。

文档静态自检8/8通过：[design-self-check.json](/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/design/design-self-check.json)。核对现有25IPC与固定main逐项同序、五份设计、T01–T25/A01–A09/F01–F07覆盖、报告链接、HEAD及已跟踪文件未变。范围检查仅新增本报告、五份设计和静态结果共7文件；未提交Git，未运行产品测试，静态自检不证明动态行为。

源码事实：main未链接凭据/Provider；旧repository::open隐式DDL和fixture seed；旧draft同revision异文可覆盖；来源检索是有界词项匹配不是语义模型/FTS5；历史deepseek提示2000字符且响应读取未设本任务所需上限。这些来自固定代码静态读取，不是新动态缺陷发现，也未判定候选安全P0/P1。

设计建议：26号独立副作用命令、v3封闭DTO、同库业务表复用、新provider库和148专用OS引用、授权后只打开已导入库不重扫、用户精确确认单次最小披露。架构保持UI→Application/Orchestrator→Ports→Adapters及Source/Model权限隔离，不冻结具体Schema。

Unknown：真实库结构/所有权/写入者，Keychain可用性、真实模型列表及参数兼容性、网络/真实效果、新安全边界独立评审结果。未核验的实时磁盘来源变化不能作为预览失效检测能力声称；本方案绑定本地已导入版本。未实现：全部148产品代码、合成验证、GUI和真实闭环，均按当前阶段范围明确后置。

## 角色与关卡

主责：专项技术合同执行；PM是合同/任务分派与账本唯一权威。协审视角覆盖数据生命周期、来源授权、凭据与网络、交互及证据，未派生独立Agent或作独立评审。当前L0五项设计覆盖已完成，需PM阶段验收；完整L3新增真实安全边界仍需独立关卡和用户具体批准。P3-147仅Local Functional User Verified / No Independent Pass，不能扩张为148安全授权。未关闭风险、未冻结、未推进Stage、未push/merge。

## 会话与上下文

Reused Session：上一P3-147已结束并元数据收尾，固定提交只读；未继承旧真实权限。授权为PM投递当前任务卡及用户“那就补充，然后启动”的顶部限定合同。

Task Contract：[当前任务卡](/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-148_source_backed_ai_conversation.md)。当前顶部合同优先于文末旧Draft字样。最初“同目录PM closeout”路径不明确，已向PM请求准确路径并暂停该依赖，期间只做独立允许读取；PM提供[pm-delivery-closeout.md](/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-147/pm-delivery-closeout.md)并更新卡后补齐。

读取最小启动包、TASK_BRIEF_TEMPLATE/SESSION_REPORT_TEMPLATE，定向补读ACCEPTANCE_GOVERNANCE、CI_CD_GOVERNANCE、PM_OPERATING_MODEL授权/验收/恢复章节及架构V1.0；固定源码、6份147设计、最终报告、非内容状态和PM closeout已核对。复用本会话稳定AGENTS全文读取结果。工具曾在大段UI/历史检索汇总截断；用于结论的IPC、存储、凭据、Transport及Source关键段已有完整单独输出；UI目录行9完整，未依赖缺失行。没有减少动态证据要求来节省读取。

当前CURRENT_STATUS仍2026-09-03、指向P3-144，与147交付/148新合同不同步。此为状态指针漂移，须PM工程启动前对齐；专项不修改PM账本或启动旧144。

## 需 PM 决策与下一门禁

需要PM决策：Yes。请核对五项方案并把26IPC/11个v3分支、JSON存储语义、新provider库2表/新OS引用、已有147根委托与无扫描访问写入完整合同；先对齐状态账本。05最后一节已准备整包真实批准内容，涵盖精确本地路径、锁及SQLite副文件、Key持久化、固定DeepSeek目标、逐次确认、非内容亲验和独立评审边界。

当前不要求用户逐项选择技术细节；由PM集中展示确定方案。PM/用户未批准新增关键API/存储及真实边界前，不进入依赖实现/真实阶段。批准合成工程后同一P3-148继续，不拆治理微任务；不自行启动其他任务。无额外后继任务建议。

自评：High，适合固定代码和可实施合同设计；运行有效性需要后续真实工程证据，不能由本设计替代。篇幅Slightly Over：五项关键合同需完整字段/矩阵，主报告只提供索引。当前设计无未完成交付；整体任务等待门禁不是Rework，也不是Paused环境事件。
