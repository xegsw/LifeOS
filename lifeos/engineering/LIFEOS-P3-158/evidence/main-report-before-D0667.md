# P3-158 主链修复：阶段记录

状态：A 离线工程检查通过；B 实现准备中，C 未执行。不是任务 Complete，也不是 Independent/PM Pass。

A 从完整 174 文件 C1 基线增量实现，当前 176 文件完整 App；生产聊天使用 v7 Host 候选/事务回执，旧 v4/5/6 测试仅证明兼容性。16 组回归步骤全通过；6 项有效 mutation 全检出。actual Tauri 完整 App 验证创建、上下文调整、正常退出重启；截图和 AX 记录在本任务 evidence。这里使用固定离线模型替身，不证明真实模型理解能力。

A 阶段身份与检查详见 `../engineering/LIFEOS-P3-158/evidence/A-stage-manifest.json`。初始失败及锁屏记录保留，不作为正向证据。当前 P3-157 真实 App 未操作，157 真实验收未通过事实不变。

ABF：01 A 已检查；02–08 A 接线及负例已检查，B/C 部分待执行；09 B 未执行；10 A 构建隔离守卫已检查，真实切换待 C；11 C 未执行。真实模型明确表达成功、必要/不必要澄清、误写、重复、越权、假成功均未测，不能记作零缺陷。

D-0666 已批准 B 两个固定非内容配置行的 Host 只读访问，仍须 A 门槛、逐次用户 App 云端确认与 24/16/40 预算。当前真实访问与云端请求计数均为 0。C 权限未提前使用。

角色：专项工程执行；PM 最终验收及独立关卡尚未通过。下一步为 B 只读适配的合成负例验证，再准备公开测试发送预览。

B 适配增量：只读连接、两个固定 SELECT、禁止测试目录/配置写入、配置指纹绑定已实现。3 个新增合成测试及全部回归、4 项构建隔离守卫通过。在线测试完整包已构建但未启动，等待用户确认既有 Settings 已选 DeepSeek 模型启用；目前没有真实读取、Key 访问或 POST。A 历史快照保留在工程目录 `stage-A/`，不以 B 后续变化改写 A 历史。

最新 B 状态：用户已确认既有设置，在线合成 App 已启动；Host 尝试按授权只读打开 provider.sqlite，但系统 open 尚未返回，配置绑定未完成。当前 Paused — Resumable，等待确认是否存在系统访问提示；原因未定，不归咎候选或锁屏。云端请求 0、Credential Port 调用 0，未访问真实正文。此前“未启动/无真实路径接触”仅为启动前检查点，不代表当前状态。最新证据 `../engineering/LIFEOS-P3-158/evidence/B-startup-paused.json`。

B 恢复增量：系统允许后出现设置兼容错误；适配器已恢复既有 Settings 目录行可缺省语义（不补建真实行），新增合成测试通过。现已在精确启动 PID 2088 的完整在线合成 App 中完成配置绑定并生成首条公开表达“明天下午去健身房”的预览；没有历史对话、目标或来源披露。等待用户逐次云端确认，持久预算开发0/24、未见0/16、总0/40，C未执行。当前证据 `../engineering/LIFEOS-P3-158/evidence/B-first-preview.json`。

B 开发01核验：实际在线构建、持久预算1、唯一create事件/feedback、相同双回执及confirm/commit幂等记录一致，唯一事项version1/planned；明确创建成功1/1。未做重发探测。开发02“健身房改到后天下午吧”预览T1绑定同一事项version1，等待用户逐次确认。B总1/40、开发1/24、未见0/16；其余语义与C未执行。

B-dev-03: same action version 3/cancelled; exactly three events (create, adjust, cancel), feedback and receipts/idempotency consistent. Refreshed preview committed; old preview never consumed. Budget 3/40. Fixed erroneous coupling of topic association to 5-minute send TTL; send TTL unchanged. Topic continuity now requires a planned target. 22 operation tests passed including elapsed-topic retention, expired preview zero model calls, and terminal-topic exclusion. Normal restart retained cancellation/history and budget. B-dev-04 public create preview ready with no prior target or message disclosure. Elliptical cancellation, explicit completion, remaining semantic negatives and unseen set still pending.

B-dev-04: first consumed request failed with provider_unavailable and businessChanged=false; a new user-confirmed request created the desk action exactly once at version1/planned. Persistent budget now 5/40, development5/24, unseen0/16; four business events total. No complete event exists. B-dev-05 completion preview binds the same desk action/version1, awaiting user confirmation. Failed request retained and counted.

B-dev-05 complete verified: same desk action version2/completed, one complete event, matching feedback/receipts/idempotency. Budget6/40. Normal restart retained cancelled and completed statuses; no resurrection or duplicate events. Candidate target retrieval also excluded terminal states after an unsent preview exposed lexical retrieval of a cancelled action; 23 operation tests passed, prior preview cancelled without consumption. B-dev-06 library create preview now has zero old targets/messages and awaits user confirmation, followed by elliptical cancellation coverage.

B-dev-06 diagnostics: two distinct consumed failures, both provider_unavailable, zero events/feedback/commit; pending draft retained, total business events5. Budget8/40 (development8/24, unseen0). Prior v7 aggregation concealed all non-network/non-timeout ModelPort errors, so historical cause remains Unknown. Fixed safe allowlist classification; truncated output, empty output and rate limiting now distinct, unknown text not persisted. Full 16-step offline regression passed. Updated exact binary PID5276, new unconsumed library preview ready; no diagnostic network/models/replay performed. Retry prepares a new disclosure and still requires user cloud confirmation.

B-dev-06 recovery create verified, version1 library action. B-dev-07 was user-confirmed during verification: elliptical cancellation succeeded on the same library action/version2, one event/feedback/receipt/idempotency result, eventsTotal7. Budget10/40, unseen0; prior failures remain Unknown. B-dev-08 ambiguous-reference preview has no eligible target and expects necessary clarification/no business change. Whole B remains incomplete.

B-dev-08 had two consumed operation_response_rejected failures, zero action events/feedback/commit and retained draft; budget12/40, unseen0. Safety rejection is not semantic Pass. Historical detailed cause Unknown. Offline verified valid clarify with empty targetRefs succeeds and appears in production v7 history; extra candidate fields/invented refs still rejected. Prompt now explicitly limits evidenceSpans to action candidates and includes a valid empty-target clarify example (prompt ambiguity is a hypothesis, not proven cause). Added fixed diagnostic codes for JSON, fields, schema, intent, refs, targets, evidence and content without raw response logging. Full 16-step regression passed. Updated App PID6660; original ambiguous question has new preview awaiting user confirmation.

B-dev-08 recovery succeeded as necessary clarification, no business event/feedback, consistent persistent receipt; budget13/40. User-visible question exactly matched the English POLICY example: likely example copying, not independently proven model internals. Chinese UX defect fixed by Chinese example and explicit user-visible language instruction; JSON keys/enums unchanged. Prompt test1 and production Flow tests7 passed, showing variable persisted replies preserved without phrase substitution or translation call. Updated App PID7017; no new preview or POST. Historical English reply preserved. Chinese live output to be checked with next required case; whole B remains incomplete and unseen0.

B paused for Keychain UX diagnosis. Latest conditional request succeeded with operation none and no business change, persistent budget14/40; no dispatching preview. Native CredentialPort performs a fresh Keychain lookup per new confirmation; no external security process. Current ad-hoc linker signing uses cdhash-bound identity and changes across retained builds. Actual ACL policy remains Unknown and was not read. No key/cache/ACL/signing implementation change or diagnostic network call performed. Precise proposals and waiting-after-credential validation gap are documented in ../engineering/LIFEOS-P3-158/B-keychain-UX-diagnosis.md; PM/security delta decision required before proceeding.
