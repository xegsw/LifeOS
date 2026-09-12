# P3-151 健康来源参与自然对话最小闭环

状态：工程完成，提交PM验收；L2 synthetic/offline。主责Codex，顺序复用150 R1已结束会话。独立评审按用户指示暂停，未宣称Independent Pass。Task Contract为工程包contract-inputs/task.md，最小IPC差异批准保存在design/pm-approval.md。未提交、推送、合并或修改PM账本。

## 交付结果

已完成实际Tauri中的“一次输入→本地有限相关上下文→可替换离线ModelPort→显式合成回答→按需来源”。延续116/142基础风格和全局对话栏，没有健康看板、手工组装或逐回答审批。两种测试Adapter共享来源/状态/记忆；所有输出明确为合成有限规则，不具备开放域推理或真实医学能力。

澄清答复可形成24小时短期状态，忽略/暂缓不写状态；“20分钟→纠正5分钟”保留原文，旧状态和依赖回答失效。普通回答始终为AI候选，未自动写入长期记忆或行动。草稿失败保留、重试一次写入、重复点击及迟到/取消不覆盖新问题。重启后对话、状态、来源、两条确认记忆与Adapter B选择保留。

最终App保持打开：PID **19407**，窗口 `LifeOS P3-151 - Synthetic Conversation`。
App：`/private/tmp/lifeos-p3-151-health-conversation-v1/LifeOS P3-151 Synthetic.app`。
最终binary SHA-256：`dba21a6df522c71d127981d21fbcbae2c7d6df5a2ad597595621a4cb75d36ad5`。
截图：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-151/evidence/gui-final-conversation.png`。
PID为本次交付时实测；后续重启以synthetic-launch.json为准。

## Acceptance Contract 自检

| ID | 结论 | 可复核事实与Evidence |
|---|---|---|
| A1 | 工程自检通过 | 自然健康问题→时间澄清→回答实际接通；gui-clarification、gui-keyboard-sources、gui-final-conversation；integration-tests自然闭环 |
| A2 | 工程自检通过 | Work引用无Health，歧义零引用，未知如实无答案；Host拒绝过期/未授权/伪造/重复/超预算，撤销任一历史依据隐藏回答；gui-work-sources、gui-ambiguous-unknown；Host负例 |
| A3 | 工程自检通过 | 答复20分钟后建议变化；忽略工作澄清后不重复，歧义澄清可暂缓；无反馈不写状态；Host及集成抑制测试、gui-final-state |
| A4 | 工程自检通过 | 纠正5分钟后旧20分钟依赖标识失效；原始表达保留、自述不覆盖测量、无自动长期化；gui-restart-correction、gui-final-state/memory，Host纠正测试 |
| A5 | 工程自检通过 | 最终binary PID19289→19407实际关闭重开，Adapter B/5分钟/对话与记忆保留；stop/launch receipts、gui-final-state/memory/conversation |
| A6 | 工程自检通过 | 实际失败留草稿/重试、B生成取消、键盘Enter/Space及700×762滚动来源可达；gui-failure-draft、gui-cancel、gui-narrow-answer/sources；集成重复/编辑竞态测试 |
| A7 | 工程自检通过 | design116.css/settings142.css/conversation.css字节不变；Global AI延续右面板，依据默认折叠，默认无指标墙；初始/最终与窄屏截图 |
| A8 | 工程自检通过 | 14组仅synthetic精确PID窗口证据；构建离线、固定新根，旧148/149closure3/150R1限定输入93/110/114项哈希未变；input-preservation、gui-index |

Host **16/16**；TypeScript Application→实际Rust Host集成 **10/10**。实际GUI覆盖正闭环、负路径、键盘、窄屏、双Adapter与重启；没有用静态扫描替代实际窗口。不是全历史测试套件，也不是独立评审。当前合同内未关闭项自评 **P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0**；由PM复核裁决。

## 包内修正与边界

补齐历史回答的输入授权/有效性展示复验，撤销依据后不继续展示旧回答正文；修正中文自然句分词漏掉“报告”，增加对应回归。完成在同一任务内，没有修改原候选或恢复历史基线。

GUI中途锁屏记为Paused—Resumable；恢复后只继续受影响GUI阶段。初次自动键入中文只产生标点，作为失败测试输入保留，完整中文使用paste验证；没有删除或冒充正Evidence。证据的不同binary/PID归属、修正前后适用范围见design/execution-notes.md和evidence/gui-index.json。

全部数据均为本轮合成。未访问/探测真实健康库、原ZIP、Pilot、个人目录、凭据、Provider、网络/本地模型，也未截图或AX抓取150真实窗口。有限离线规则、≤3来源+≤2状态/记忆、4096字节上下文与有限历史快照是本合同实现范围；不证明真实AI质量、医学正确性、真实健康披露或Stage变化。

## 交付物与复跑

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-151/`。
- 实现：candidate/application/health_context.ts、health_conversation.ts、health_ui.ts及candidate/src/health_conversation_host.rs。
- 设计与批准：design/reuse-map.md、ipc-delta-proposal.md、pm-approval.md、execution-notes.md。
- 完整性：FINAL_MANIFEST.json、DIFFERENCE_MANIFEST.json、checkpoint.json。
- Evidence：evidence/rust-tests.log、integration-tests.json、gui-index.json、各精确窗口JSON/PNG及launch receipts。
- 复跑：`bash /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-151/tools/rerun.sh`。仅固定本轮合成根，输出新rerun目录，历史Evidence只读。

需PM决策：对A1–A8及交付作L2验收。独立评审未执行；不请求扩大权限。下一真实阶段仍须明确数据/接收方/模型/最小披露与风险边界的单独合同，本轮不执行、不自行创建后继。
