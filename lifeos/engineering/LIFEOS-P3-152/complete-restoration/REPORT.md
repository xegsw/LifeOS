# P3-152 完整累积恢复：工程交付

2026-09-09。状态：Partial / Synthetic closure ready for PM review。L3；不是 Complete、Independent Pass、真实完整启用或产品冻结。主责 Codex 工程，PM 验收和真实权限差异确认尚待进行。

本轮按 `closure-contract-proposal.md` 与 `design/approval.json`，在 health-view-restoration 完整候选上恢复来源管理、原文检索/详情/统一对话、健康文件导入。保留设置、自然对话、草稿与按需健康查看。同一 candidate、同一 Tauri App，无第二套聊天 Shell。候选159文件：新增26、修改16、删除0，逐文件差异见 evidence/difference-manifest.json。

| 能力 | 当前合成行为与证据 | 真实模式 |
|---|---|---|
| 模型设置、草稿、自然对话 | 原12项集成全通过，actual App 保存模型、跨页保留草稿、重启保留模型和回答 | 继承既有受控健康对话许可；本轮未运行真实 App |
| 来源管理 | 目录连接、暂停/恢复/取消/刷新/断开/重连，固定合成目标授权/撤权；7文件初始GUI与8文件最终测试（新增长文分页fixture） | 新6个来源/导入IPC在引擎访问前返回权限未获准 |
| 原文检索与详情 | markdown/txt/html/csv/docx解析，配置受限、未知格式不假装解析；分页完整重组，刷新拒绝旧cursor | 尚未获准读取新的真实来源/缓存 |
| 来源到统一对话 | 原文只读，最多3个来源片段，与现有确认记忆合并；预览→显式合成确认→C1–C4引用回答 | 非健康来源真实外发未获准 |
| 引用时效与发送竞争 | store/root/source/file/version/grant/epoch/hash/range九类篡改拒绝；发送保护期间变更阻塞；刷新/暂停/取消/断开使旧确认失效 | 原有真实健康路径保持，不绕过许可 |
| 健康导入与查看 | XML新增3观察；重复XML/ZIP不新增；坏XML失败保留旧观察；同fixture Reader显示4321步与Synthetic Import Watch | 真实重新导入和目标库写入未获准；原健康只读查看继承 |

## 关键接线与边界

8个原IPC加5个来源管理IPC和1个导入IPC，共14个。私有 source-engine 是包内 path dependency；Cargo.lock只增加本地包，不引入网络依赖升级。沿用147来源管理和149解析/事务逻辑；149中明确禁用连接/刷新/授权的入口已用147实际实现替回，未以空桩接回菜单。

新合成引擎根固定在 task-owned `complete-source-engine`，0700目录、0600标记与文件，按Host fixture分库；不引用旧运行根。UI不能提交路径、fixture或模式。导入只影响当前fixture健康输入，不迁移真实库。来源桥接保留typed身份、版本、授权代数、epoch、内容hash；内部source意图只用于有实际命中时的上下文分类，不产生新的Core领域模型冻结。来源投影有界并可失效，原文不被改写为记忆。

来源管理页进入时查询，离开停止轮询并丢弃迟到结果；没有自动网络来源传输。实际来源worker只处理明确授权的固定合成目录。真实模式在私有引擎初始化/文件操作前拒绝新命令，health SourcePort先走既有真实只读分支。新真实bundle仅构建，未启动；既有真实App没有被关闭、重启、取AX/截图或读取真实库。

## 验证

- Host：63/63，`evidence/host-tests-final.log`，含原62项和新增SourcePort篡改/发送互斥综合测试。
- 原集成：12/12，`evidence/integration-tests.json`，覆盖披露、取消/迟到、失败重试、配置与草稿等。
- 新组合集成：11/11，`evidence/combined-tests-final.json`，覆盖来源生命周期、原文分页/旧cursor、实际引用回答、旧确认拒绝、离线目标、导入幂等/失败保持和DTO拒绝。
- UI：健康12/12 + 来源5/5，`evidence/health-ui-tests.log`、`evidence/sources-ui-tests.log`。合计103项测试，不是整个历史仓库全量套件。
- 双模式 `--locked --offline` 构建成功；真实只构建，不运行真实测试驱动或App。
- actual Tauri：目录→检索→原文→同一全局草稿→4条实际披露→确认→离线引用回答；XML导入完成→我→4321步；模型、来源状态、导入结果和回答跨重启保留。每个有效截图有直接PID、二进制hash、精确窗口标题、AXWebArea和CG窗口几何链。

`source-detail/source-preview/source-answer/import-completed/imported-health-detail` 绑定初始组合PID36705。`restart-conversation` 绑定PID37390。之后加入的内容仅为cfg(test)测试模块，但最终重构建的debug二进制hash发生变化，因此额外启动最终PID37533，补取`final-settings-visible/final-source-import-persisted/final-health-persisted`。最终二进制绑定见`evidence/final-artifact-binding.json`；两份早期launch receipt只读保留。没有把旧PID窗口伪称最终PID。

取证中一次旧helper仍引用旧receipt，返回拒绝；已改为本包receipt并重编译。一份`final-settings.json`仅有AX，CG窗口处于缩略状态，未产生有效截图，明确排除其正向截图效力。已恢复精确合成窗口并以`final-settings-visible`补取；不把环境取证缺口算候选缺陷。首次新增测试中`inputRefs`/`completed`断言误配实际`refs`/`duplicate`，修正断言后全通过；该断言修正不改变产品行为，首次失败不计入最终Pass。

## 运行产物

- 合成预览：`/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Complete Preview.app`；当前PID37533，hash `dc34be5927a125c4640b733414d9256b7513e072e40e45e12a259addf8187917`。
- 真实统一候选：`/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Complete Restored.app`；hash `657e138794b64249a5493ff5e76b4521b17f9862d9aa129742557f9dfaacff06`，未启动。
- 本机开发bundle仍依赖当前工作区/受控运行根，不宣称可分发到任意机器的安装器。没有覆盖任何历史或当前真实bundle。
- `tools/rerun.sh`在当前专用根内复跑，先校验包及固定合成fixture，再将新日志写到root内唯一新目录；不会写回已交付Evidence，不会开启GUI/真实Provider。
- `tools/setup_engine.py`是首次创建入口，已有根拒绝覆盖。`design/fixture-identity.json`记录本次12个合成输入文件；不得拿setup覆盖既有根或伪称新生成ZIP字节等同历史fixture。

## 保全和未完成边界

`evidence/preservation.json`逐项复算旧synthetic189、real-stage332、ui-restoration172、inheritance-audit3、health-view-restoration167，共863条历史文件hash全部一致。旧包、报告、Manifest不被改写。当前改动未提交/推送；先前PM源代码同步快照不是本次完整交付快照。

当前合成合同未发现未关闭P0/P1/P2。以下真实差异保持Unknown/Not Enabled，不换算为合成Pass：唯一真实来源及缓存/派生库路径和读写范围、非健康片段逐次外发许可、健康XML/ZIP及目标健康库写入许可、用户退出当前真实App后的安全切换。不能从健康只读/发送许可推导这些许可；不能以历史路径猜测或探测补齐。

需PM决定：复核本统一合成候选并集中明确真实Task Contract差异；独立评审/真实启用关卡按原L3安排继续，当前不宣称通过。完整真实产品仍未完成，不关闭本结果任务、不进入Stage 4、不冻结资产。合同之外116原型中的完整Workspace/Quick Capture等不凭菜单名字认定已经生产实现。
