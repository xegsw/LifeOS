# P3-157 自然对话安排真实接入

2026-09-10，Ready / Execution Authorized，D-0661。用户在明确展示沿用真实库、新增安排历史、保留UI/数据/凭据、不迁移清理、正常切换完整App、DeepSeek逐次确认及有限句式边界后回复“确认，启动”。本卡将已展示范围具体化，不再重复询问启动。风险L3，独立评审继续依用户指示暂停，不宣称Independent Pass。

## 唯一结果与基线

Closure-1授权（D-0662）：用户允许已展示的有限语义修正，精确提案`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-157/closure-1/design/minimal-correction.md`，SHA-256 `4aeb731e3305b8f15cc8832c24a2d2fd59ab69daabe6fc87cc54d2749d9f60f1`。以强意图槽位替代动作词白名单，撤销须匹配已有唯一planned事项；普通聊天/未支持安排/歧义/支持安排分流，未支持不得转普通AI冒充已保存。TS及Host复核不减，v6字段/14命令/物理Schema不变，不新增按钮或云端解析。原始交付只读保留，合成回归后按原精确切换合同接续；真实验收仍未通过，不因本授权改为Pass。

在当前真实使用版正常聊天，明确说定的安排及完成/调整/取消按156有限句式保存并跨重启保持；不增加任务卡/同义确认按钮，歧义才澄清，不执行外部行动。

基线为`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-156/candidate`完整173文件，构建入口Cargo.toml；FINAL_MANIFEST及PM Review分别核对。156只读保全；155真实版作为切换前完整功能/固定根依据。必须保留设置、Provider列表、模型读取选择、Key加密无TTL、来源/健康/对话/155恢复，不能交付精简App。

## 允许范围

工程根`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-157/`；唯一新构建/合成根`/private/tmp/lifeos-p3-157-real-actions-v1`，0700及0600独占marker，不接管未知根。

仅将D-0660已批准v6安排协议接入真实existing-only模式：同库records/action_event、feedback/action_feedback、questions/action_clarification及原事务请求记录；物理表/Schema/14命令/v4/v5不变。原始用户表达、事件版本、权限、来源及幂等原子校验不得简化。真实模型解析不在本次范围：沿156本地有限句式识别，普通DeepSeek对话保留既有逐次披露，不把模型输出当用户确认。

真实目标仅由App内部使用，Agent不读取正文/值/凭据/AX/截图/内容日志/hash：

- `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/conversation.sqlite`：复用已有库，事务追加上述用户明确安排和反馈历史；保留原记录，不迁移/清空/重建。
- 同父目录provider.sqlite、`.lifeos-p3-152-owner.json`、`.runtime`及必要SQLite事务副文件：按既有合同复用，不改名重置。
- 同父目录source-engine-v1/sources.sqlite及既有资料缓存：按155现有读取/授权边界准备相关上下文；本轮不由Agent触发刷新/导入，不新增数据源。
- `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite`：沿既有只读上下文能力，保留库。不在本轮重新导入ZIP或读取原目录。
- Credential Port仅既有service `com.lifeos.p3-152.aead-key.v1`、严格旧account `p3-152-key-[0-9a-f]{32}`，不枚举、不重录、不回退其他任务Key。

普通模型请求仅用户逐次披露确认后访问https://api.deepseek.com既有端点，预算/授权保持155；不自动重试、不后台发送。行动本地保存不需要为它调用云端。若发现真实根或现有Schema不满足existing-only要求，失败关闭并向PM报告，不补建迁移。

先完成合成安全检查，再按精确包/运行身份正常退出155真实App，保留旧包，启动最终完整157真实App；不强杀模糊PID、不删除锁。失败先核对启动claim与实际结果，不重复盲启；保持数据并按既有锁合同恢复。合成156实例若冲突只报告身份，不清理真实资产。

## Acceptance / 交付

任务级验收依据见同目录LIFEOS-P3-157_acceptance_basis.md。实现、测试、动态验证、同范围修复、安全切换和用户最少验收放在本任务，不拆微任务。代码/行为优先，UI未变部分按影响复用，不机械截图；锁屏等Paused—Resumable，checkpoint恢复受影响阶段。

输入：5ed8根AGENTS、CURRENT_STATUS、本卡及验收依据、SESSION_REPORT_TEMPLATE、156最终PM Review与获批最小协议、155最终PM Review/真实切换报告；定向读PM/角色/阶段/验收治理的真实数据权限和用户暂停例外、CI可恢复执行与完整产品条款。工程顺序复用原会话，PM唯一维护账本，不启动后继。

交付：b3f6树lifeos/deliverables/LIFEOS-P3-157_real_conversation_actions.md及完整candidate、影响矩阵、Manifest、checkpoint、非内容切换回执和离线复跑入口。真实结果由用户正常说定安排、更新并重启后回复通过或固定错误码，不索取正文截图。L3终局等待用户结果，不关闭风险/冻结/切Stage，不自动合并main或清理数据。
