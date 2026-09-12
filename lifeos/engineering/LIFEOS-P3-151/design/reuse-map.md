# P3-151 复用与缺口

输入先按各工程FINAL_MANIFEST核对，见evidence/input-identity.json。148最终候选93项代码/设计、149 closure-3的110项、150 R1的114项代码/设计/报告通过；未读对应真实库或历史真实内容证据。

| 能力 | 实际已有 | 本轮复用 / 差异 |
|---|---|---|
| ModelPort/SourcePort | 148 application/core.ts 的ModelPort、FixtureSource、两个离线实现 | 保留Port边界与双Adapter身份；演练输出只标合成。现有模板只处理少量固定Work状态，本轮拓展意图和无答案处理，仍不宣称通用推理 |
| Context Resolver | core.ts validRows/currentStates/resolve/relevantFeedback | 复用分层、授权版本、有效期、refs、预算；修正记忆层默认跨域及任选前几条的问题，按问题/时间/领域选择有限候选，不给UI全量历史 |
| 澄清/纠正 | core.ts nextQuestion/decide/correct | 复用questions/states生命周期；新增健康可用时间和歧义领域澄清语义，暂缓/忽略/回答抑制；纠正保存独立原文并使旧状态/依赖失效 |
| 对话持久化 | 148 conversation_store.rs 的records/drafts/packets/derivations/feedback/requests，已有9类业务表 | 在同一新合成业务库复用这些表，不建第二记忆库、不接真实open_active。151专用typed Repository Adapter使用相同表结构和新明确JSON版本 |
| 草稿与UI生命周期 | 148最终conversation_flow.ts 的serial、恢复编辑优先、busy、queue、controlled turn、取消 | 按该状态机适配一键离线发送；没有外部发送确认/手工组装，失败保留原草稿，幂等提交，迟到与取消不覆盖新输入 |
| 健康来源 | 149 closure-3 dayIndex/metric/source名称组/offset/nullable value/estimated | 只创建合成投影，复用语义；无ZIP/import入口，无真实health_reader接线 |
| 视觉与来源 | 148 source_ui + design116/settings142/conversation.css；150 R1按需辅助 | 继承基础CSS/图标/Global AI输入栏和右侧对话；来源仅按需查看，无健康看板和技术参数墙 |

核心产品规则仍在TypeScript Application/Domain/Context与ModelPort；Rust仅固定合成根、严格DTO、限量读取及事务/权限再验证。Provider及加密配置源文件保留原样而不编译/接入本模式。
