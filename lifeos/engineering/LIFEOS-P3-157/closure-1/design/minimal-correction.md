# P3-157 Closure-1 最小修正方案与确认语义差异 v1

状态：设计待PM裁定，未修改/构建/切换候选。2026-09-10。仅同任务Closure，不启动后继；用户ABF08未通过。真实App/DB/正文/Key/AX/截图/网络均未触碰。

## 已复现事实

对原交付不可变JS调用真实actionCandidate和ControlledConversation，Repository为无IO合成double：

| 合成替代句（非用户正文） | 当前解析 | 实际Application路径 | action_event |
|---|---|---|---|
| 我明天先买合成材料。 | undefined | 普通prepare_disclosure | 0 |
| 先不买合成材料了。（已有唯一对应安排） | undefined | 普通prepare_disclosure | 0 |
| 我明天先整理合成材料。 | create | 本地commit_action_turn | 1 |

另有固定取消、否定新意图、引用、多目标4个对照，共7例。evidence/reproduction.json保存调用序列；这是缺陷复现，不是修复通过。未检查用户真实记录，不能据此声称已读取或判定其具体DB状态。

根因是两个规则加一个路由歧义：clearArrangement依赖动词白名单；forbidden把“不”按字符串位置一概拒绝；ActionApplication将“无候选”合并为普通聊天false，Controller因此准备AI披露。聊天回答即使肯定也不是本地事务回执。不能只补“买”一词或把任何“不”当取消。

## 最小修正

1. **先分类，再执行**：TypeScript纯分类返回chat / unsupported_action / ambiguous_action / supported_action，独立于ModelAdapter的可选候选。只有chat允许进入旧对话披露链。模型返回undefined不能推翻Application已经识别到的行动意图。
2. **未支持表达明确停留本地**：unsupported_action不写action_event，不准备云披露，保留同一原始草稿；固定反馈“这句还没有记入安排，请明确说出要记下或调整的内容。”不显示“已记下/已取消”。无需新增确认按钮，也不自动重新发送。表达不明确时，ambiguous_action复用既有v6 clarify/现有action_clarification，只问一个必要问题；该提交不是行动写入。
3. **以明确句式槽位承接内容，不依赖动作词表**：提议在原有安全句式之外，采用强第一人称意图框架，例如“我明天先{内容}”“我今天要{内容}”“我接下来先{内容}”“我打算{内容}”。{内容}按原文跨度原样保存，不用动词名单决定买/寄/修/准备等词能否成为本地记录。不推断具体工具、日历时间或外部动作。引用/假设/问句/可能性/多分句冲突优先排除；弱或未支持框架归unsupported_action，不能静默送AI作持久化确认。保留原来的明确受支持句式作为兼容分支。
4. **否定与撤销拆开**：否定新意图如“我不打算买合成材料”不创建、不取消；不能仅因“不”出现就判断撤销。“先不{事项}了”等有结束/撤销信号的有限框架，须从已有planned行动中，以已知句式去除第一人称/时间/先要修饰后取得事项原文，再对该事项做精确唯一匹配。唯一匹配才产生cancel及expectedVersion；没有匹配不更新并明确未取消任何已记下安排；多个匹配只澄清目标；完成/取消历史不能复活。词内“不”（如“不锈钢”）不是句子否定，不使用contains('不')作权限规则。
5. **保持Host二次复核**：Rust对同一有限句式/目标匹配做确定性边界复核；来源/版本/原始草稿/packet和事务幂等保留。不能只在UI修分类而放松Host校验。新增测试同时攻击Application与Host，防止两边口径分裂。
6. **本地结果身份明确**：已写入状态只能由commit_action_turn成功返回产生；unsupported/clarify/失败分别显示未写入、必要澄清或失败恢复。普通AI文本仍是AI回答，不能生成本地安排成功状态。恢复只读，不用旧肯定语气重建行动。

## 协议与授权影响：需PM确认的精确delta

不新增SQL表、Schema迁移、数据库、IPC命令、v7、云端解析或权限；保持现有v6三操作与Candidate字段。保留174完整基线及全部旧能力，新增实现放closure-1/candidate，根历史只读。

Application内部submit由布尔值改为区分结果的union（具体内部类型可常规实现），这是消除静默回落的包内修复。Domain/Host的**确认语义**则有明确扩展：由“固定动词名单+固定取消后缀”，变为上述强意图槽位及基于既有事项唯一匹配的撤销框架。虽然wire字段不变，也不把它伪装成无协议语义变化。请PM裁定上述有限确认语义能否作为本次已授权Closure，或将此明确delta展示后取得必要批准；批准前不实施这些扩展，不切换App。

可单独批准立即实施的安全下限是：四类路由、未支持表达的本地未写入提示与草稿保留。它不扩大哪些表达能写；即使扩展句式暂未批准，也应避免普通AI肯定语气被误解为安排已保存。但最终验收仍需覆盖用户要求的系统性修复，不能只完成该安全下限就宣布Closure通过。

## 文件影响与验收

- action_domain.ts及对应Rust actions.rs：分类/有限框架/事项标准化与唯一目标复核；不改事件Schema或生命周期。
- action_application.ts、controlled_conversation.ts：消除boolean歧义，只允许chat走普通对话；保留草稿与只读恢复。
- health_ui.ts/health_errors.ts：只改结果状态文案接线，不添任务按钮/导航，不重做Settings；新增可达性/窄窗合成测试按实际影响决定。
- tests：新词/词内“不”、不同框架、明确撤销/否定新意图、无目标/唯一/多目标/终态/版本迟到、引用/假设/问句/不确定、ModelAdapter空候选、云端肯定文本与本地回执分离、失败/重复/重启/恢复。
- mutation：unsupported被改回chat、恢复动词白名单静默回落、任意否定取消、绕过唯一目标、模型文本伪造本地成功、Host原文/版本校验绕过。

完成修正后按影响回归和合成Gate，再提交真实切换检查点；本条不是现在重新切换的授权。当前真实运行157保持不动。既有254检查/5mutation和历史报告只说明上一交付，不外推为本Closure通过。
