# T01–T25 有限合同断言核对

依据：原封存05的T01–T25、01–04及E01。工程核对，非独立结论。已执行证据仍绑定原候选与日志；“缺”表示当前没有足以支持该明确断言的证据，不等于已证明实现失败。T08另有已重现的实现缺陷。

证据简称：R为candidate/src/conversation_store.rs的p148_*测试；P为provider_store.rs的p148_*；I为tools/test_source_conversation.py；X为test_conversation_extended.py；L为test_legacy_functional.mjs；GUI为evidence中的app-*及gui-closure.json。自动结果索引ci-final-02.json、restart-final.json、legacy-functional-03.json。不得用静态实现位置充当动态断言通过。

| ID | 合同内有限断言及已有依据 | 明确缺项/状态 | 不要求的外推 |
|---|---|---|---|
| T01 | I草稿/保存/回放；X事务失败保留pending并同request恢复；E01重启恢复 | Partial：缺保存失败时实际UI保留编辑器且不显示已存的故障状态观察 | 不要求所有磁盘故障组合 |
| T02 | I同request同payload、同turn不同request回放、同revision异文拒绝、跨会话读取隔离及已提交草稿不返回 | Partial：缺旧draft revision、跨会话写入拒绝、同request异DTO和保存后重启再重放的逐项断言；不能拿跨会话读拒绝替代写拒绝 | 不要求无限requestID/文本组合 |
| T03 | I四中文相关候选稳定Top3；R英文窗口800scalar定位；source_filters无匹配/token省略 | Partial：缺零词项及普通无关文本no_match的明确ModelPort零调用断言；被过滤来源no_match不是全部搜索分支 | 不要求所有语言/全文搜索算法 |
| T04 | R未解析、missing、secret、旧version/grant/epoch、external root、撤权共8变体 | Partial：缺配置文件/受限状态/私钥头命名分支；不能把api_key赋值一例替代全部已列保守规则 | 不承诺识别一切敏感语义 |
| T05 | R2000/2001多字节、800窗口、单纠正超限；X3×800及JSON开销超限；源码有界SQL | Partial：缺0/空白问题、800/801精确边界、24KiB等于边界、多条相关纠正合计溢出、查询读取量的具体依据 | UTF-8合法2000scalar至多8000字节，8192独立超限在此前提下不可达，不应制造不可能输入 |
| T06 | R逐字bodyJson等于ModelPort body；GUI可见系统/问题/片段/目标/预算；历史纠正预览 | Supported：当前命名正路径有字节/GUI依据；历史GUI按其构建单独保留 | 不要求逐个模型排列重测相同序列化 |
| T07 | R直接状态变体expiry/cancel/restart/version/epoch/removed/disabled零调用；GUI取消历史 | Partial：缺通过真实operation完成移除/取消/重建后旧token零调用；缺凭据替换和模型选择变更；“removed”仅直接标记stale，不是移除操作测试 | 不要求全部变化交叉乘积 |
| T08 | 已有一例unknown payload和伪造token拒绝、stdio重复键拒绝；新增框架Value边界重现 | Fail：Tauri JSON重复键已覆盖。另缺所有operation的字段闭合/混版本有限表及副作用计数。见T08_BOUNDARY_REVIEW.md；需E02封装决策 | 不要求外部攻击/平台已拒绝测试，不以stdio代Tauri |
| T09 | P保存/test/select/enable功能分离；Transport固定目标源码与纯解析 | Partial：缺同一注入Port上的save=0、test仅models一次、select/enable=0、confirm仅chat一次的完整调用轨迹 | 真实网络按后续Gate，不在本轮补真实请求 |
| T10 | P未test启用、未知model、旧凭据revision、NoNetwork真实Adapter入口拒绝 | Partial：缺明确other-provider及运行时env不改变路由的有限负例；未enable发送由disabled变体部分支持 | 不要求任意系统环境变量穷举 |
| T11 | R顺序重复同request/异request仅一次，dispatch事务失败0 | Partial：没有同步屏障/真实并发两个request试验。顺序回放不能替代合同点名的屏障和点击竞态 | 不要求所有线程调度排列 |
| T12 | R超时/结果落库失败unknown且回放不发；X跨进程预置dispatching恢复/轮询 | Partial：缺断网等价错误明确映射、实际持久化阶段崩溃点、新预览明确确认才允许新尝试的完整轨迹 | 不要求任意机器掉电时刻；X预置行不是杀进程崩溃证明 |
| T13 | R成功/错误/空/超限无正文，纯HTTP解析覆盖401/协议错误；GUI成功 | Partial：缺失败/unknown在UI可见、busy结束可继续的实际合成故障展示 | 不需每个HTTP状态×所有视口 |
| T14 | R C1映射/C99计数；带HTML的文本作为答案保留；源码转义 | Partial：缺当前实际渲染中HTML/远程图片纯文本和未知计数可见的直接断言；R不测试DOM或图片加载 | 不执行外部图片请求以证明不发送 |
| T15 | GUI点击原版本来源；R晚撤权答案stale及confirmed=false | Partial：缺citation详情接口对新版/撤权拒绝、不悄悄切版本的直接断言；答案stale不等于详情拒绝 | 不要求旧真实源或147并发 |
| T16 | R correct与feedback/依赖变化、无关答案保留、C99拒绝反馈数不增；GUI纠正 | Partial：缺helpful/reject不改用户事实；缺correct事务中途失败后原文/feedback/失效全部回滚；当前C99是提交前拒绝 | 不要求任意依赖图规模 |
| T17 | I纠正后重启答案stale；R后续预览含纠正、错误citation拒绝 | Partial：缺同一次跨重启后预览带对应纠正；旧answer revision拒绝无部分写；其他答案拥有的citation作用域负例 | 不把C99不存在等同于其他答案citation |
| T18 | contracts目录8云4本地；来源搜索/详情、桌面/窄屏GUI及扫描禁用标注 | Supported for synthetic：当前命名界面有证据；真实扫描禁用仅源码/合成标注，真实运行Not Run | 不要求所有屏幕尺寸；不重扫真实资料 |
| T19 | I跨进程密文保持；P tag/AAD/旧reference零调用；MemoryPort nonce/AAD/缺失锁定 | Partial：MemoryPort独立key密码学单测与生产provider生命周期未联成同一个持久化Port测试；SyntheticKeyPort由reference确定派生，不能冒充独立OS key | 不要求访问真实Keychain |
| T20 | P replace配置提交失败、delete删除失败、显式recover回放零调用、被动settings计数；I provider库不含canary明文 | Partial：03明确的prepared前/后、OS创建后DB提交前、提交后旧key清理、delete禁用提交与OS清理各窗口未逐项覆盖；缺receipt/log/snapshot联合泄露检查 | 只需持久化边界代表窗口，不要求每条指令崩溃 |
| T21 | R已有库schema_version/seed数不变、缺索引/缺库拒绝；X来源读无DDL、provider读取不建库 | Partial：缺缺表/未知schema各代表结构；缺只在保存动作建provider库的命令入口负面集合与扫描Port计数 | 不要求检查真实库结构或复制旧库 |
| T22 | 26注册静态；I/X/L旧20项多个正负operation；v3隔离50/51/cursor旧revision | Partial：旧来源5项未逐operation形成回归表（当前status/search/detail正路径、其余禁用部分为源码）；不能把注册等同可达行为 | 不要求被禁旧安全runner或所有旧组合 |
| T23 | R消费前grant变更0、handoff后撤权stale；X两个遵守锁的148进程冲突 | Partial：handoff回调固定时点支持消费后逻辑，但缺两个受协调器约束的线程同步屏障竞态；与T11共用最小调度夹具即可 | 明确不证明147互斥、不承诺召回 |
| T24 | 合成/GUI/真实/安全分别记录，历史失败保留，无真实内容材料；旧矩阵措辞已纠正 | Supported as metadata：本轮新增缺项/Fail应进入当前checkpoint和Manifest，不再写完整工程包可送Gate | 不要求以安全Pass换元数据完整性 |
| T25 | main启动无DB/worker；P pending状态read_settings零OS计数；I E01恢复；X激活/被动读 | Partial：缺prepared/cleanup_pending组合的启动→激活→恢复全链OS/网络/扫描计数及准备失败问题保留/busy释放GUI | 不要求无人CI运行真实GUI或OS服务 |

## 处理顺序

T08修复需要明确传输封装，已交PM最小E02；缺陷不转交独立评审兜底。其余Partial为同任务有限补齐清单，不能宣布已关闭：先合并DTO表、预览变化、反馈事务及并发调度的共享合成夹具，再补生命周期Port轨迹与受影响GUI。所有工作继续受原禁止测试/真实边界约束。

“Supported”仅指本行列出的合成断言具备现有依据，不是L3/PM/独立Pass。当前整体Closure Cycle，真实Gate暂停。原矩阵原样保存history/pre-t08-AC_MATRIX.md。
