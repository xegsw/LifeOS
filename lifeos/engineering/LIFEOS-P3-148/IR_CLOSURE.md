# P3-148 四项P1工程Closure

状态：工程修复及受影响验证完成，待PM与独立复评。依据PM任务01a0290d-4255-7c52-8e62-6b888d2d678a的同任务Closure分派；只读独立报告及lifecycle/supplement结果，摘要见evidence/IR-closure-lineage.json。未修改评审包，未访问已清理评审根。修前363项完整包/报告/Manifest保存在history/pre-IR-closure-package.zip，旧Manifest摘要3a4ee14faf9521664d64c0eb01437300c2481a9752766fe0b16ab188bc300bb2。

| 问题 | 修复 | 当前验证 |
|---|---|---|
| IR-P1-148-001 | prepare相同request回放从原回执取得previewId，再经current_preview读取当前packet；与read_preview共享投影。取消/失效/消费不恢复ready或token；历史回执原值保留 | p148_ir001，cancelled/stale/consumed三分支、无token、packet计数不增、两读取入口一致 |
| IR-P1-148-002 | read_conversation按会话+turn筛选回答ID，再投影targetId匹配的真实feedbackIds，包含同turn历史回答关系 | p148_ir002，helpful/reject、第二turn和同turnID异会话隔离、重开连接；主集成另验证纠正feedbackId在进程重启后仍返回 |
| IR-P1-148-003 | source_store::validate_reference共享已有SourceValidity：当前授权与generation/epoch、segment-record-file-connector关系、parsed/seen_epoch/各version、原记录有效性/正文及来源关系、locator和scalar范围。预览生成/发送前/回答读取/响应落库调用同一校验 | p148_ir003十种绑定字段变体，响应途中epoch变化先持久stale；另一测试成功后epoch变化，read_answer的validity和citation均stale；无真实扫描 |
| IR-P1-148-004 | ModelPort增加内部generate_with_receipt。协调器进入适配器时仍持有；DeepSeek在有界校验完成且精确body/key已装入Zeroizing配置后发出receipt，再启动curl/等待响应。Synthetic/in-memory适配器在入口接收请求后receipt。回调只消费一次；提交失败不入Port，接收前失败释放锁。成功响应重新取得协调器，事务内复核全部packet来源（包括未被模型引用的来源），再保存answer/citation状态 | p148_ir004用有界内存Port在接收前try_lock证明锁仍持有、dispatching已提交且连接无事务；receipt后能取得锁并撤权；仅接收一次、返回时持久stale/revoked。已有并发屏障/重复发送/提交失败/响应失败/退出恢复回归通过 |

receipt是本进程Transport接受已授权不可变请求的线性化点，不是服务商收到字节或请求成功的证明。协调器不等待整个网络，SQLite事务不跨网络等待；接收后撤权不承诺召回，只使后续来源使用失效。真实Transport仅静态检查其接收点与工程模式拒绝，未运行网络。

## Evidence与失败历史

IR-closure-domain-03.log：25项会话回归通过（含4项初版专项；其中既有1项为子进程辅助入口）。之后只扩充测试：IR-closure-targeted-final.log最终5项专项通过；IR-closure-transport.log 2项通过；IR-closure-restart.log与extended.log为6+7集成组通过。不同运行不简单相加为独立用例总数；没有重跑无关凭据生命周期/旧27项或平台排除runner。IR-closure-build-01.log为当前离线构建。IR-closure-regression.json为定向入口及日志索引。

保留IR-closure-targeted-01.log（测试操作名写成cancel_preview，固定DTO拒绝；修正为合同cancel_source_preview）；IR-closure-domain-02.log保留三处旧测试夹具正文/片段不一致的失败。正向预算和Top8夹具改为两处文本一致，未放宽新校验。这些是工程测试修正，不改独立报告或历史结论。

当前actual Tauri：PID76602窄屏700×760预览→合成确认→回答保存；PID76660桌面1280×949重启恢复→有帮助反馈保存。四张截图逐张查看，精确PID/标题AXWindow/WebArea/geometry/hash绑定；重启前后回答对象与计数一致，反馈计数增加1；两个PID已停止。见evidence/IR-closure-GUI.json。本次没有GUI脚本注入、真实内容或真实Provider。

评审侧P2 checkpoint、U GUI夹具、NI四组仍由独立评审自行补证，不能拿本工程结果代替；它们不记为本轮产品缺陷。四P1目前只标工程修复验证通过，独立复评/PM验收未通过，真实Gate继续暂停。无新产品范围/Schema/IPC/真实权限变化，无push/merge。设计01–05和E01–E03保持只读。
