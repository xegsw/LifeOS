# P3-149 S2 苹果健康文件导入闭环

2026-09-09。状态：合成离线工程 Completed，提交 PM 普通 L2 验收；不代作 PM Pass。主责 Codex 专项工程，复用既有会话；S1 与手机方案线已结束。本轮不启动独立评审、真实接入或后继任务，不提交推送合并。合同为 PM 树 `lifeos/tasks/LIFEOS-P3-149_S2_apple_health_file_import.md`；新增唯一 IPC 的后续用户批准记录在 `contract-inputs/ipc-authorization.json`。

## 结果与入口

实际 Tauri App 已提供“设置 → 数据与隐私 → 导入苹果健康文件”。点击后选择任务内合成 XML/ZIP 即开始，显示进度、新增观察、重复内容、不支持、失败、来源与最近导入时间。失败可重试，成功历史关闭重开后恢复。文件选择器严格限于 S2/inputs，不是任意真实文件选择器；界面明确“文件导入，非自动同步”。“我”显示来源观察，Memory 保留导入批次。

当前展示 App PID **2358**，启动记录 `evidence/launch-s2restart.json`，程序为 `/private/tmp/lifeos-p3-149-health-source-v1/S2/LifeOS P3-149.app/Contents/MacOS/lifeos-p3-149`。binary SHA256 `f996a53251d61f030265421cf6fbd9341d5e3d24d3e51b8592bcc473f9d01304`。原始动态验证 PID 2095 已确认身份后关闭。仅操作149合成展示进程，没有操作148或其他任务进程。

## 实现及边界

系统 Python 标准库提供流式 XML/ZIP Source Adapter，Rust Application 用一个 SQLite 事务经既有 records/sources/states JSON 保存来源观察、内容去重和批次引用。没有新增表列或核心实体，没有下载依赖。固定 Host 注册从26到27，仅增加 `import_apple_health_file` 的 list/start/status；raw UTF-8 请求4096字节，拒绝重复/未知字段及不合法动作结构。固定根 marker、openat/O_NOFOLLOW、hardlink拒绝、描述符及路径链前后身份校验限制读源，并发 start 返回 busy。解析和投影在后台工作线程，不阻塞 UI 线程；无后台自动采集。

原文件字节摘要用于整文件幂等，标准化内容指纹只识别相同观察，不冒充样本UUID或修订证明。跨文件重叠内容不重复计量，同批重复/步数运动重叠冲突保持不确定，不因新文件缺行推断删除。来源按名称组划分，不冒充唯一设备。观察时间与导入时间分离；跨日睡眠按日并集，步数/运动比例分配标估算，不同offset不混合。新旧v1/S1状态双向拒绝混入。默认快照排除逐条苹果观察及成员关系，苹果按日状态最多显示最新256条，库内历史仍保留。

ZIP 只读取唯一 export.xml，附件仅验证目录元数据并计未处理，不读内容/引用。拒绝穿越、绝对路径、特殊文件、加密、歧义条目、压缩炸弹、选中XML损坏与资源超限；先限EOCD/中央目录再分配条目。XML 兼容正常内联DTD，拒绝自定义实体和外部DTD/实体请求，不解析外部目标。尾部损坏、超限、超时、中断、文件替换和事务失败均回滚。

## 验证结果

| 合同 | 工程自检 | 可复核依据 |
|---|---|---|
| S2-01 | Pass | `s2-xml-success.png/json` 新增3/不支持1；`s2-zip-success.png/json` 新增0/重复3/不支持1/附件1；同一实际UI入口 |
| S2-02 | Pass | `s2-duplicate.png/json`、`s2-overlap.png/json`；Rust 文件重放/重叠/乱序/冲突测试；重复后仅2批次，重叠增加1条观察 |
| S2-03 | Pass | Python 26项解析正负；Rust资源/描述符替换/事务失败回滚；`s2-failure.png/json` |
| S2-04 | Pass | 单位/跨日/offset/睡眠类别/未知类型测试；支持表及Me截图；未知与冲突不造零 |
| S2-05 | Pass | 中断重试/重启 Rust 测试；真实App失败前后及重试健康命名空间完全一致，关闭重开亦一致 |
| S2-06 | Pass | PID2095及2358精确窗口/AXWebArea/CG几何绑定；进度、完成、失败、重试、重启与700×760窄窗口证据 |
| S2-07 | Pass | `preservation-final.json`；前后端实际resolver/source-preview/prepare健康排除回归；无真实目标/网络调用 |
| S2-08 | Pass | 本报告、支持表、设计、run_checks.py、candidate-diff.json、results.json、FINAL_MANIFEST.json |

- Python **26/26**：`evidence/parser-final.log`。
- Rust **60个不同测试通过**：health筛选59 + p149_apple_import筛选1，`evidence/rerun-20260909T005241908432Z.log`。该组合日志的Python段是扩展前23项，最终解析数量以26项独立日志为准。69个无影响历史Rust测试未重跑，不称全历史套件。
- 前端 **27/27**：`evidence/ui-tests-1.log`，含8项Apple接口/进度/重试/并发/去重/转义/模型排除及19项既有受影响回归。
- UI构建与 Rust 离线构建成功：`evidence/build-ui-host.log`、`evidence/build-final.log`。未运行CI，不声称CI绿。没有调用真实Provider或本地模型。
- 1000行/177247字节合成文件成功，超过旧128KiB/256样本限制；`s2-progress.png` 捕获未完成状态，`s2-large-complete.png` 显示新增1000。该例不代表最大技术上限的性能承诺。

实际 App 最终 **1004条观察、1008条批次成员关系、4个成功批次、2个来源、6条状态**。`db-before-bad.json`、`db-after-bad.json`、`db-after-retry.json` 全对象一致；`db-db-after-large.json` 与 `db-after-restart.json` 全对象一致，结构化断言见 `results.json`。只查询本轮新库的 apple-file-v1 健康命名空间，没有查询凭据或其他库。重启截图恢复07-large.xml及原成功时间，未自动重新导入。

截图逻辑窗口为1280×949与700×760；对应物理像素2560×1898与1400×1520。`s2-narrow.png`、`s2-narrow-sources.png` 显示换行及滚动可达；`s2-me.png`显示独立观察日期/接收时间，`s2-memory.png`显示健康历史区域。继承的全局输入栏固定在底部，内容通过滚动查看。重启第一轮AX发生在渲染未就绪时，未生成错误截图，待同PID渲染完成后补取；不重做无关测试。

## 保全、缺陷与限制

原交付 **161项**及报告、S1 **129项**及报告均重新校验未变。两份历史Manifest摘要分别为 `ec7ac1ce37fc740df97654bde6574e40a1762cb3950dc448a5caeef7b48658d7`、`63e2a206ac66893d2e7858af210e33506a7a06b9da4c4f0e82d5bd4bd4cd8953`。116/142基础CSS与4个Provider/凭据相关源码文件逐字保持。S2候选相比S1新增8文件、修改14、删除0，完整差异摘要见 `candidate-diff.json`。启动记录中的全部候选文件hash与最终候选一致。

合同内自检 **P0=0、P1=0、P2=1、Unknown=0、Not Implemented=0**。P2-01：错误正文附带 `health_document_corrupt` 等未本地化技术码；失败1、未导入、有效数据保留及重试已明确，可读性小缺口不影响操作或失败关闭。此分级交PM判断，未据此宣称风险关闭。

首版明确限制：仅三类指标；ZIP64/多磁盘/非store-deflate不支持；1970–2100、单记录正时长最多7天，同条起止offset不同（含跨DST）整包失败。默认文件256MiB、XML512MiB、4096ZIP项、200压缩比、200万Record、120秒工作预算；SQLite约1GiB、128来源组、10000按日投影，超限整批失败。构建限额见 `candidate/apple_health_limits.json`。附件内容未验证，不支持类型未投影；真实Apple导出兼容性未执行，属于合同外真实阶段未知。

已修正的包内失败保留原日志：Python offset兼容、ZIP夹具固定时间、serde空动作忽略多余字段、新旧协议守卫遗漏位置与测试synthetic会话初始化。最终通过日志明确列出，不混用早期失败为正证据。

## 复跑与PM收尾

包根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-149/S2`。复跑：`python3 -B <包根>/tools/run_checks.py`，使用已准备的任务合成输入，验证根marker、离线运行26解析/60Rust/27前端，新增时间戳日志；不自动启动GUI、不联网、不清理。新环境需按任务合同先准备独立合成根/夹具，不能指向真实输入。GUI捕获入口为 `tools/capture_app.py <launch标签> <新证据标签>`，要求对应启动记录的活PID及精确窗口已就绪。

`checkpoint.json`记录工程交付完成；App保留展示，没有运行导入作业。本报告及全部包文件由 `FINAL_MANIFEST.json`校验；该Manifest是L2交付完整性清单，不是Frozen ABF。设计 `design/import-contract.md`，支持类型和未来真实操作授权清单 `design/supported-types-and-real-entry.md`。

需PM：按S2-01至08及P2影响完成普通L2验收。没有新合同范围请求；不启动独立评审或手机/网络后继。真实文件、读取类型/范围、存储位置、正文/hash/日志披露及保留政策尚未授权，未要求用户导出或上传。未读取/探测真实健康文件、iCloud/个人目录、Pilot、旧DB或凭据，未修改PM账本、冻结、风险或Stage。
