# T01–T25 有限合同断言与当前证据

状态：**四项独立P1已作工程Closure，待PM与独立复评**。当前修复/回归/GUI索引以IR_CLOSURE.md为准；下表保留既有有限覆盖背景，不代表旧独立Not Pass已转Pass。E03前最终二进制GUI已由PID73617（700×760）和73741（1280×949）补齐，见evidence/final-gui-verification.json。不是独立安全Pass、PM Pass或真实亲验。原缺项清单原样保存在history/pre-closure-CONTRACT_ASSERTION_MAP.md；旧Covered矩阵在history/pre-t08-AC_MATRIX.md。

引用索引：Rust `evidence/closure-rust-final-02.log`（35通过、27旧测试过滤）；I=`candidate/tools/test_source_conversation.py`；X=`test_conversation_extended.py`；L=`test_legacy_functional.mjs`；运行日志由`evidence/closure-restart-final.json`指向（6+7组及v2 smoke）。Rust缩写为函数名尾部，均可在candidate/src中精确rg定位。GUI均有各自launch/PID/标题/WebArea/截图/geometry，不能跨构建替代。

| ID | 具体断言与Evidence | 限定结果/剩余 |
|---|---|---|
| T01 | I保存幂等、X事务失败；app-closuresavefailure编辑器保留且新问题计数不增 | 已观察；保存错误分支未被后续文案修正改变 |
| T02 | closure_draft_revision_and_cross_session_writes；I保存后跨进程同request重放、E01隔离 | 有限负例已补齐 |
| T03 | I四匹配稳定Top3；source_filters窗口；closure_preview_operations_and_no_match零词/无关文本/token省略/零调用 | 有限搜索分支已补齐 |
| T04 | source_filters原8变体；closure_configuration_private_key_and_restricted_filters | 配置过滤漏项已修复；不承诺识别所有秘密 |
| T05 | closure_exact_serialized_budget_and_multiple_corrections；closure_source_query_returns_eight_at_most；X预算 | 0/空白、800/801、24576精确/超1、多纠正总额及SQL最多8结果→3片段已补齐；合法2000scalar无法独立超过8192 UTF-8字节 |
| T06 | preview_bytes_citations_and_duplicate_dispatch逐字比较；app-e02preview及app-closurepreviewrecovered；历史F1展示 | 组合工程证据；E03前正常调用见app-finalnarrowpreview/answer |
| T07 | closure_preview_operations_and_no_match真实cancel/remove/rebuild/replace/select及问题版本；原expiry/session/epoch等变体 | 旧token零调用；不把直接stale mutation冒充移除operation |
| T08 | ipc_boundary三个测试、strict_json边界测试；E02_IMPLEMENTATION.md；19个operation/反馈分支表 | 共享Raw入口拒绝前业务回调0；原缺陷已修复；live负面注入Not Run；E03前正常GUI绑定已完成 |
| T09 | lifecycle_models_only_on_explicit_test_and_no_creation_on_reads逐阶段GET计数；RecordingModelPort confirm调用数/body；固定Transport源码 | 保存0、test仅models一次、select/enable不增、confirm一次；OS和ModelPort为分层组合证据，不宣称实际网络监听 |
| T10 | model_selection_and_no_network_build；raw_operation_contract_table other-provider；runtime_env_cannot_enable_transport；disabled变体 | 有限拒绝项已补齐；环境字符串不能改变编译能力 |
| T11 | closure_real_coordinator_duplicate_and_revocation_barriers；dispatch_commit_failure | 真实共享协调器+Barrier+阻塞ModelPort，两request一次；事务失败零调用。名称real_coordinator指真实代码协调器，不是实数据信息 |
| T12 | closure_process_exit_after_dispatch_commit_and_explicit_retry；timeout/result failure；X恢复 | 子进程进入ModelPort后exit77，重启unknown、读取/旧回放零发送；新预览后才新尝试；curl异常退出映射unknown代码已修复 |
| T13 | response_errors/HTTP纯解析；app-closureerrorsone/errorstwo；app-closureanswerrecovered | 四固定失败码及unknown可见，成功可见；GUI为显式虚构状态夹具，状态生成由Rust用例支持 |
| T14 | preview_bytes引用集合；app-closureliteral | HTML/图片语法字面显示、1个无效引用可见；不以显示检查冒充网络抓包 |
| T15 | closure_structure_and_citation_version_rejection；app-e02citation；late_revocation | 同版本正例、新版/撤权拒绝；confirmed=false；详情负例为本地SourceStore接口 |
| T16 | closure_feedback_decisions_and_transaction_rollback；correction_scope | helpful/reject不改记录；反馈中途故障整体回滚；对应依赖变化、无关依赖保留 |
| T17 | I纠正后重启再预览含对应文字；closure_feedback旧revision与其他答案C2拒绝 | 跨进程和有限作用域负例已补齐；不外推无限依赖图 |
| T18 | 既有8云4本地/导航/来源GUI；E02窄屏；新桌面故障GUI | 目录/布局保持；E03前二进制窄屏Settings与桌面恢复/Settings均已绑定，各截图注明自身PID/构建 |
| T19 | lifecycle_independent_key_persistence_and_replace_windows；P tamper；MemoryPort crypto failures；I跨进程 | 独立随机OS模拟材料不等于reference派生值，跨SQLite重开；nonce/tag/AAD/缺失锁定由命名用例组合支持；真实OS Not Run |
| T20 | lifecycle替换5边界、删除3边界；prepared/delete_cleanup既有用例；no_secret检查 | prepared前后/创建后/提交前后/OS删除失败；显式recover回放0；provider行/回执/settings无完整虚构Secret；不声称逐条机器指令崩溃 |
| T21 | existing_store_open；closure_structure；lifecycle无库读取/操作不创建；X schema_version | 缺库/缺表/缺索引/未知schema、无DDL/seed、明确replace才创建provider已补齐；未检查真实库 |
| T22 | contracts26清单；I/X/L；X five_source_ipc_allowed_and_disabled_branches | 旧20命令命名分支与来源5项允许/禁用分支；v3隔离/50+1/cursor；未运行旧27或平台拒绝runner |
| T23 | closure_revocation_barrier_before_permission_consumption；closure_real_coordinator_duplicate_and_revocation_barriers；X 148锁 | 消费前Barrier排序零调用；消费后受锁撤权结果stale；不证明147互斥、不承诺召回 |
| T24 | 历史保存、逐行矩阵、E02与当前检查点/Manifest | synthetic/GUI/user/security分开；当前GUI已补齐，不是最终任务Pass |
| T25 | lifecycle pending状态激活→read_conversation→read_settings OS/models trace不增；main启动调用链；app-closurepreparefixed→recovered | 问题保存/准备失败/busy释放/再次预览成功；启动零动作由静态入口与合成激活计数组合，不作真实OS遥测；最终GUI绑定已完成 |

无要求穷举所有语言、输入字符串、线程调度或指令崩溃组合。live WebView负面注入未执行；工程Raw入口单元测试与actual-Tauri正常调用须分开陈述。真实构建/DB/OS/网络、独立新安全Gate和用户真实亲验继续Pending/Not Run。

E03配置增量：两个合成编译profile均通过3项定向测试/8项环境覆盖拒绝；业务/UI不改，旧GUI按自身构建保留。新增构建未运行GUI（PM明确不重跑无关GUI）。参见E03_IMPLEMENTATION.md及evidence/E03-lineage.json。

四P1增量映射：T06/T07→IR001当前packet回放；T16/T17/T25→IR002真实反馈恢复；T03/T15/T23→IR003统一SourceValidity；T11/T12/T23→IR004显式Transport receipt与返回时复核。最终5项专项/25项相关回归/2项Transport/13组集成及当前GUI见IR_CLOSURE.md。
