# P3-148 工程观察矩阵（非 Frozen ABF / 非独立 Pass）

合同：contract-inputs 五份封存设计 + E01-task-card。2026-09-08。状态：工程Evidence已整理提交；锁屏后从检查点恢复，当前构建窄屏检查完成。下表是证据索引，不能把“Covered”解释为全部L3攻击空间或真实运行通过。

最终自动阶段索引：`evidence/ci-final-02.json`（16项Rust）与 `evidence/restart-final.json`（6+6组集成）；最后GUI展示构建：`evidence/gui-final-build.json`。完整日志由索引精确定位。本文不覆盖旧27项测试或此前平台拒绝的安全测试。

| ID | 已观察结果 | Evidence / 实现检查 | 工程状态 |
|---|---|---|---|
| T01 | 原子提问；触发器故障保留pending草稿，同request恢复；E01六字段恢复 | restart两个脚本；capture事务；桌面提问历史 | Covered |
| T02 | request/turn回放、异文冲突、跨会话拒绝、重启不重复，已提交草稿不返回 | test_source_conversation | Covered |
| T03 | 中文4匹配稳定Top3；英文匹配；无匹配no_match；窗口800scalar精确定位 | Rust source_filters；集成四匹配和重复预览 | Covered |
| T04 | 未解析、missing、secret、旧version/grant/epoch、外链root、撤权不入包 | Rust source_filters 8种变体；source_store::search/check | Covered |
| T05 | 2000/2001多字节边界；3×800=2400；序列化控制字符开销超24KiB拒绝；纠正溢出拒绝 | Rust scalar/feedback；extended budget | Covered |
| T06 | ModelPort收到逐字bodyJson；系统说明、问题、C1–C3和F1可查看 | Rust preview_bytes；app-revieweddesktoppreview | Covered |
| T07 | 过期、取消状态、重启session、source版本/epoch、失效标记、disable零调用 | Rust preview_invalidation；窄屏取消历史 | Covered |
| T08 | 严格字段/版本和token；stdio递归重复JSON键拒绝；Tauri命令对象使用封闭DTO | Rust strict_dto；integration token/unknown | Partial：未声称验证Tauri框架原始消息重复键解析 |
| T09 | 保存、test、select、enable、confirm分离；models与chat固定authority及路径 | provider模型测试/纯HTTP解析；固定Transport源码；合成UI | Covered in mock/static；真实网络Not Run |
| T10 | 未test启用、未知模型、旧凭据版本拒绝；合成调用真实Adapter在spawn前拒绝 | p148_model_selection_and_no_network_build | Covered |
| T11 | 同/不同request同preview仅一次ModelPort调用；dispatch DB故障零调用；重复request登记 | preview_bytes/response_errors/dispatch_commit_failure | Covered；并发全组合不外推 |
| T12 | timeout、结果落库故障、跨进程dispatching→outcome_unknown；重复读取不重发 | Rust timeout；extended跨进程恢复 | Covered |
| T13 | 固定HTTP错误、模型错误、空响应、超限，failed/outcome_unknown持久；UI显示固定错误 | transport解析/response_errors；source_ui错误投影 | Covered in mock/static；未逐种GUI注入HTTP故障 |
| T14 | C1映射提交集合，C99计数且不成证据；HTML/图片语法作为转义文本 | Rust preview_bytes；UI esc；引用GUI历史 | Covered |
| T15 | citation按本地sourceRef/version打开；晚撤权答案stale；confirmed=false | handoff_late_revocation；app-desktop02citation | Covered |
| T16 | correct原文+feedback同事务；未知citation拒绝无部分写；无关依赖保留 | Rust correction_scope；桌面实际纠正 | Covered |
| T17 | 纠正重启保持、旧答案stale、下一预览带F1；revision由反馈合同验证 | Rust correction_scope；restart；desktop02correction/preview | Covered |
| T18 | 8云4本地目录、导航、来源检索；桌面高保真布局；先前窄屏预览/确认已取证 | contracts；app-revieweddesktop*；app-narrow02* | Covered：app-resumednarrow02*，700×760，同二进制 |
| T19 | AES-GCM持久cipher；nonce/tag/AAD错误；MemoryPort锁定/缺失；旧引用拒绝前零key调用 | provider persistent；p148_memory_os_port_crypto_failures | Covered in mocks；真实OS Keychain Not Run |
| T20 | replace DB故障保留旧Key及prepared；delete清除可用凭据后cleanup_pending；被动读取不恢复；显式恢复回放无额外调用 | provider prepared/delete_cleanup测试 | Covered for named fault windows；未声称穷尽所有崩溃时序 |
| T21 | App只开已有表/列/索引，缺库不CREATE；打开/来源读取schema_version不变；provider被动读取不建文件 | existing_store_open；extended passive；CLI造数入口隔离 | Covered for synthetic structure；真实库 Not Inspected |
| T22 | 26注册清单；旧snapshot/unavailable/offline拒绝分支；v3不泄露至v2；50/51游标及旧cursor拒绝 | contracts；extended legacy/paging；legacy-functional-03.json | Covered：新增v2正向功能smoke；不外推全部组合 |
| T23 | 消费前撤权零调用；消费后撤权结果stale；两个148进程锁冲突拒绝 | Rust dispatch/handoff；extended cooperating lock | Covered；不证明147互斥或请求召回 |
| T24 | 合成/GUI/真实/安全分开；包内均合成文本；历史失败保留；无真实目标探测 | 本矩阵、checkpoint、包Manifest | Covered：FINAL_MANIFEST.json，工程包摘要，不是Frozen或安全Pass |
| T25 | 启动不打开DB/worker/OS；被动settings不恢复prepared；E01草稿跨进程恢复；busy finally结束 | main startup；provider计数；extended passive；source_ui | Covered in synthetic/static；真实启动 Not Run |

真实新边界独立评审、PM最终验收、用户真实亲验均Pending/Not Run。148锁只约束遵守该锁的148实例，不能证明147关闭。真实构建接线可供审阅但本轮没有编译或运行；App内用户关闭147提示不能替代PM安全Gate。

SyntheticKeyPort是跨进程演练用、明确不安全的确定性OS模拟；MemoryCredentialPort提供独立密码学失败模拟。网络零调用由合成分支和真实Adapter入口拒绝支持，不是外部网络监听证明。真实明文、Key、DB、内容hash/AX/截图没有进入本包。
