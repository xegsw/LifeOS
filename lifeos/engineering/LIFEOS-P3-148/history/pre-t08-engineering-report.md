# LIFEOS-P3-148 来源支撑的AI对话：工程进展与可恢复交付

2026-09-08；Codex专项工程；L3；状态 **工程包已交付，待PM及独立安全评审**。需要PM安排新增真实边界独立评审；当前不宣称25行全覆盖的完整L3 Pass、独立Pass、PM验收、真实亲验或Stage切换结论。原设计阶段报告完整保存在 `lifeos/engineering/LIFEOS-P3-148/history/design-stage-report.md`。

## 已实现与已验证事实

在 `codex/l3-p3-148-source-ai` 分支，基于固定 `5c26431ca43d68b77ab3d91a715dd59444a62e2e` 的147 candidate只读复制到148。147和PM账本未修改。五份合同封存保留，E01草稿恢复单独增量封存。

26项IPC注册、11项v3分支；本地草稿/问题幂等保存、Top3相关检索、精确披露body、逐次确认、ModelPort派发和不重发状态、来源引用、反馈纠正与跨重启恢复已接线。旧业务库打开路径不DDL、不seed、不扫描；provider两表独立，仅明确保存后创建。启动无数据库/worker/OS凭据/网络动作。反馈不会自动提升为长期确认事实。

API Key使用AES-256-GCM密文与148独立引用。显式recover/save/delete才处理已知遗留凭据操作；被动读取只显示待恢复。真实DeepSeek Adapter只允许固定models/chat路径、无proxy/redirect/retry/fallback，输入和响应有界，日志不带正文。真实构建接线只验证既有147 marker、打开已有库；不创建真实根、不枚举旧资产、不扫描原目录。本轮仅engineering构建，未编译/运行真实profile。

最新合成CI **16项Rust测试通过**，跨进程集成 **6+6组通过**，新增v2正向功能smoke通过，契约静态检查通过。覆盖保存故障保留草稿、跨会话隔离、4匹配稳定Top3、2400scalar及JSON开销预算、预览失效零调用、超时/落库失败不重发、伪引用、反馈范围、凭据恢复、50/51分页和148实例锁。详见 `evidence/ci-final-02.json`、`evidence/restart-final.json`、`AC_MATRIX.md`，不把测试数冒充25行完整L3通过。

实际合成App已操作提问→披露→确认→答案→引用→纠正→重启。当前候选桌面PID **66415**、二进制SHA-256 **0962fbff03159678afb707f0e9ee9590566bdbb1c29e7d7e2a75506062aa4808**；PID→精确标题AXWindow→WebArea→CG窗口→截图geometry保存在 `app-revieweddesktop*` 和 `launch-revieweddesktop.json`。8云/4本地目录保持，表单间距与预览遮挡问题已包内修正。之前700×760窄屏已验证预览和确认可滚动到达；当前候选最终窄屏曾因Mac锁屏暂停；用户解锁后以新PID **68278** 恢复，已完成会话恢复、披露、确认发送、答案和Settings检查，证据为 `app-resumednarrow02*`，二进制摘要与桌面相同。

## 尚未关闭的边界与限制

工程观察矩阵明确保留T08原始Tauri消息重复键层的覆盖限制；T22已新增普通v2正向功能smoke，不能外推全部输入组合。没有运行旧27项Rust测试，也没有改写或绕过此前平台拒绝的安全测试。已覆盖的DTO、源码及普通回归不等于这些未验证范围的独立安全证明。

SyntheticKeyPort只用于跨进程演练，使用明确不安全的模拟材料；MemoryCredentialPort单独验证AES和失败路径。这不是实际OS Keychain安全证明，不得在合成App输入真实Key。真实构建、真实库结构、真实OS凭据和真实DeepSeek调用均Not Run/Not Inspected。真实用户操作必须先经过PM安排的新安全Gate，再由用户在App激活并逐次确认；147 waiver不继承。

148锁只保护多个148实例。真实使用前由用户关闭147，使用148期间不重开；不能承诺跨版本互斥。没有真实资料/DB/Key/正文hash/截图/AX进入Evidence，没有网络下载，没有push/merge、冻结或风险关闭。

## 检查点与复跑

检查点：`lifeos/engineering/LIFEOS-P3-148/evidence/checkpoint.json`；`resume_from=PM_review`。锁屏中断记录完整保存在history，恢复时校验合同/候选不变，没有重跑无关阶段。所有本任务App已停止，唯一合成根 `/private/tmp/lifeos-p3-148-source-ai-v1` 保留构建与纯虚构夹具供复核。

`FINAL_MANIFEST.json` 为本次工程交付的文件清单和hash，不是Frozen资产或安全通过回执。`MANIFEST.in-progress.json` 保留中断时快照，不覆盖其历史。恢复初期操作工具未取到AXWindows时保存的 `app-resumednarrowrestart/preview/confirm` 三组实际仍是启动页，均明确排除正Evidence；修正的是任务操作helper的同PID AXMainWindow读取，产品candidate未改动。随后成功证据均重新取得同PID准确窗口、WebArea、CG几何与截图绑定。

任务内CI入口：`tools/verify_source_conversation.py --phase all` 或指定contracts/build/storage/credentials_mock/transport_mock/restart；要求 `LIFEOS_P3_148_BUILD_PROFILE=engineering`。GUI不进无人值守CI。旧147复制runner不属于148复跑入口。精确清理工具有marker/PID/WAL门禁；本次未清理其他根。

## 角色与PM交接

主责为Codex专项工程；协审和PM裁决尚未发生。本会话按新P3-148合同执行，不继承147范围。原最小启动包、任务模板、验收/CI治理、PM授权章节及架构定向输入已读；CURRENT_STATUS仍旧144索引的差异已按PM卡披露，专项不改账本。E01歧义已由PM同包批准，无新用户授权问题。

待PM：审阅本包覆盖限制并安排新增存储/凭据/网络边界的独立安全评审及真实亲验步骤；不把当前工程观察矩阵冻结为ABF。本轮工程交付完成；后续同包评审修正仍遵守本合同，未启动后继任务。
