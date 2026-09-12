# P3-148 IPC 与严格 DTO 提案

状态：2026-09-08，只读设计完成，待 PM 纳入 Task Contract；不是已实现 API。固定输入提交 `5c26431ca43d68b77ab3d91a715dd59444a62e2e`。下文源码位置均相对该提交的 `lifeos/engineering/LIFEOS-P3-147/candidate/`，不是运行态检查。

## 1. 现有 25 项逐项核对

注册权威：`src/main.rs:22–54,150–176`；路由权威：`src/repository.rs:662–695` 与 `src/source_api.rs:185–240`。前20项外层为 `{version:2,operation,payload}`，后5项为 `{version:1,payload}`；注册不等于能力可用。

| # | IPC | 5c26431 可达 operation / payload 分支 | 建议最小差异 |
|---|---|---|---|
| 1 | capture_record | save / ingest / draft | 保留 v2；新增 v3 draft_question、save_question |
| 2 | get_today | snapshot | 原签名保留；通用投影不得泄露新内部包/凭据 |
| 3 | runtime_status | snapshot | 保留；真实148不能继续硬报所有网络计数为0 |
| 4 | confirm_capture_context | unavailable | 不借用作网络发送 |
| 5 | get_context_recovery | unavailable | v3 open_conversation / read_conversation，打开已有本地会话，不启动扫描 |
| 6 | get_context_next_action | unavailable | 不变 |
| 7 | decide_context_next_action | unavailable | 不变 |
| 8 | record_action_result | unavailable | 不变 |
| 9 | assemble_global_ai_context | local_prepare / surface_question | 保留 v2；v3 prepare_source_preview / cancel_source_preview |
| 10 | get_evidence_backed_understanding | snapshot | 保留 v2；v3 read_answer，含受校验引用 |
| 11 | decide_understanding_feedback | question_decision / feedback | 保留 v2；v3 answer_feedback |
| 12 | get_ai_provider_settings | snapshot | 保留 v2；v3 read_settings，只返回脱敏专用 DTO |
| 13 | save_ai_provider_settings | offline_settings | 保留 v2；v3 select_model |
| 14 | save_ai_provider_credential | offline_capability_denied，打开DB前拒绝 | v3 replace_credential / delete_credential / recover_credentials，新引用专用接线 |
| 15 | test_ai_provider_connection | 同上 | v3 test_connection，用户点击单独确认的 GET /models |
| 16 | set_ai_provider_enabled | 同上 | v3 set_enabled；保存、测试、选择、启用、发送分离 |
| 17 | upsert_durable_memory | correct | 不用来自动确认模型回答；不变 |
| 18 | update_current_state | correct | 不借用来覆盖来源正文；不变 |
| 19 | resolve_request_context | offline_generate | 保留离线语义，真实模式拒绝该生成路径 |
| 20 | get_context_disclosure_receipt | snapshot / source_revoke | 保留 v2；v3 read_preview |
| 21 | connect_source_directory | requestId | v1 DTO不变；148真实会话模式禁用重新扫描入口 |
| 22 | control_source_job | requestId,connectorId,expectedGeneration,action | v1 DTO不变；148真实模式仅允许停止/断开类动作，refresh/resume拒绝 |
| 23 | get_source_status | connectorId? | 不变，已有库激活后读取 |
| 24 | authorize_source_target | requestId,connectorId,expectedGeneration,linkId,decision | 不变；真实模式继续 external_targets_disabled |
| 25 | get_source_evidence | search / detail 判别联合 | 不变；引用详情复用，旧版/撤权不能悄悄切换版本 |

建议新增第26项 **send_source_ai_request**，只有 `version:1, operation:"confirm_send"`。它是明确外部副作用，不能为凑25项伪装成 resolve/offline_generate、capture 或读取操作。公共增量是 **25→26 + 现有11个命令的v3分支**（1、5、9、10、11、12、13、14、15、16、20），须 PM/用户按关键 API 合同确认。v2旧分支不接生产网络；新真实会话模式的扫描与快照投影收紧也须一并列入批准，不静默修改旧147应用。

## 2. 统一严格规则

- 下列字段列表穷尽允许字段，`?`才可省略；其余均必填。对象每层拒绝未知字段、null、数字字符串、重复JSON键、非有限数值及混合分支字段；解析器必须显式拒绝重复键，不能依赖通用 Value 最后值覆盖。
- ID：1–120 ASCII字符 `[A-Za-z0-9_:-]`。版本/代数：整数1..9007199254740991；revision基数可为0。客户端不传路径、URL、SQL、service、Keychain reference、模型输出、任意prompt或授权布尔值。
- Text：问题/纠正1–2000 Unicode scalar，UTF-8≤8192字节，非全空白；草稿允许空串。不做静默trim/改写，超限保留草稿并明确拒绝。
- v3外层严格 `{version:3,operation:<该命令枚举>,payload:<对应对象>}`；第26项外层版本1，其余相同。先解析/模式/权限检查，再访问存储或 OS。合成版本仅注入 MemoryCredentialPort / RecordingModelPort，真实网络实现不可由运行时环境变量打开。
- RequestID为一次操作ID，不是授权；同ID、同规范化DTO回放，同ID异DTO `idempotency_conflict`。客户端重试必须沿用ID；跨IPC幂等键绑定 command+version+operation。关键代数由后端检查。
- 所有错误仅 `{code:<下述固定枚举>}`，不用动态错误串/正文/路径。成功结果均以下述类型精确序列化，不返回数据库原始body。

## 3. 操作与输入

| command / operation | payload（穷尽） | 返回类型 |
|---|---|---|
| capture_record / draft_question | requestId, draftId, conversationId, turnId, revision:u53(≥1), text:DraftText | DraftResult |
| capture_record / save_question | requestId, draftId, conversationId, turnId, expectedDraftRevision:u53 | TurnResult；正文只从绑定草稿读取 |
| get_context_recovery / open_conversation | requestId, conversationId | ConversationPage；用户点击“打开已有本地会话”，不表示网络授权 |
| get_context_recovery / read_conversation | conversationId, cursor?:ID | ConversationPage，已激活后分页，50条/页 |
| assemble_global_ai_context / prepare_source_preview | requestId, conversationId, turnId, expectedQuestionVersion:u53, excludedSegmentIds:ID[] | Preview；首次空数组，移除片段后重建新预览，数组≤8且无重复 |
| assemble_global_ai_context / cancel_source_preview | requestId, previewId, expectedPreviewRevision:u53 | PreviewState |
| get_context_disclosure_receipt / read_preview | previewId | Preview（先重新检查有效性） |
| send_source_ai_request / confirm_send | requestId, previewId, expectedPreviewRevision:u53, confirmationToken:ID | DispatchResult；不接正文、模型或URL覆盖 |
| get_evidence_backed_understanding / read_answer | dispatchId | AnswerResult |
| decide_understanding_feedback / answer_feedback | requestId, answerId, expectedAnswerRevision:u53, decision:"helpful"或"reject"或"correct"，correct分支独有 correctionText:Text, affectedCitationIds:ID[] | FeedbackResult；correct数组可空表示整条回答，非空必须属于此回答 |
| get_ai_provider_settings / read_settings | {} | SettingsResult |
| save_ai_provider_credential / replace_credential | requestId, profileId:"deepseek-default", expectedCredentialRevision:u53(≥0), apiKey:Secret | CredentialResult |
| save_ai_provider_credential / delete_credential | requestId, profileId:"deepseek-default", expectedCredentialRevision:u53, confirmation:"delete_this_credential" | CredentialResult |
| save_ai_provider_credential / recover_credentials | requestId, profileId:"deepseek-default", expectedCredentialRevision:u53(≥0), confirmation:"recover_owned_credential_operations" | CredentialResult；仅用户点击“恢复凭据操作”，无Secret/reference/service输入，零网络 |
| test_ai_provider_connection / test_connection | requestId, profileId:"deepseek-default", expectedCredentialRevision:u53, confirmation:"test_deepseek_models_once" | TestResult；只GET固定/models，不含问题或来源 |
| save_ai_provider_settings / select_model | requestId, profileId:"deepseek-default", expectedProfileRevision:u53, testReceiptId:ID, modelId:ModelID | SettingsResult |
| set_ai_provider_enabled / set_enabled | requestId, profileId:"deepseek-default", expectedProfileRevision:u53, enabled:boolean | SettingsResult |

ModelID为1–128字符 `[A-Za-z0-9_.:-]`，且必须属于本凭据版本刚成功测试的列表；不根据旧历史硬编码真实可用模型。Secret沿用8–512 ASCII graphic，排除引号和反斜线（`secure_credentials.rs:201–210`），不返回、不进入通用request receipt或Debug。合成fixture model只能在合成构建选择。

PM一致性补正：显式新增上述`recover_credentials`拟operation，仍归第14项v3，不增加IPC数量或受影响命令数；须随合同批准，不是既有授权。启动、打开会话、read_settings以及网络test/send均不能隐式触发OS恢复/清理；仅用户明确恢复/保存/删除动作可处理获准148引用。没有待恢复项时返回当前stored/deleted且OS调用为0；有待恢复项则按03执行，未完成返回cleanup_pending。

## 4. 返回 DTO 字典

下述对象同样字段封闭，时间均服务端 UTC epoch毫秒；可缺字段用`?`。ID均随机/稳定不透明ID，不能由真实内容生成hash。详细内部存储见02；流程见04。

```text
DraftResult {draftId, revision, state:"saved"}
TurnResult {conversationId, turnId, questionId, questionVersion, state:"stored"}
PreviewState {previewId, revision, state:"cancelled"|"stale"|"consumed"}
SourceRef {segmentId, recordId, connectorId, sourceRef, version,
           authorizationGeneration, scanEpoch, locator, startScalar, endScalar}
DisclosureItem {citationId, kind:"source"|"user_correction", text,
                source?:SourceRef, correctionId?:ID}
  source分支必须source且禁correctionId；correction分支相反。
Preview {previewId, revision, questionId, questionVersion, question,
         provider:"DeepSeek", authority:"https://api.deepseek.com",
         modelId, profileRevision, credentialRevision, instructions,
         items:DisclosureItem[], bodyJson, budget:Budget,
         state:"ready"|"no_match"|"stale"|"cancelled"|"consumed",
         expiresAt, confirmationToken?:ID}
  只有ready返回token；bodyJson为将发送的规范JSON全文，UI可展开显示；
  instructions和所有实际文本必须可见，不允许隐藏历史消息。
Budget {maxQuestionScalars:2000, maxSourceScalars:2400, maxSegments:3,
        maxCorrectionScalars:2000, maxInputBytes:24576, maxOutputTokens:1024,
        usedSourceScalars, usedInputBytes, tokenEstimate, estimateOnly:true}
DispatchResult {dispatchId, previewId,
                state:"dispatching"|"succeeded"|"failed"|"outcome_unknown",
                answerId?:ID, errorCode?:ErrorCode}
Citation {citationId, source:SourceRef, availability:"available"|"stale"|"revoked"}
AnswerResult {dispatchId, state:DispatchState, answerId?:ID, revision?:u53,
              text?:TextAnswer, citations?:Citation[], invalidCitationCount?:u53zero,
              validity?:"candidate"|"stale", confirmed:false,
              provider?:"DeepSeek", modelId?:ModelID, startedAt?:Time,
              finishedAt?:Time, usage?:{inputTokens?:u53zero,outputTokens?:u53zero},
              errorCode?:ErrorCode}
  succeeded必须answerId/revision/text/citations/invalidCitationCount/validity/
  provider/modelId/startedAt/finishedAt；非成功禁正文与上述成功专属字段。
  usage可缺，不能伪造零；text上限16000 scalar、65536 UTF-8字节。
FeedbackResult {feedbackId, answerId, answerRevision,
                state:"recorded", correctionId?:ID}
CredentialResult {profileId, credentialRevision,
                  state:"stored"|"deleted"|"cleanup_pending", maskedTail?:string}
TestResult {testReceiptId, profileId, credentialRevision,
            state:"succeeded"|"failed"|"outcome_unknown",
            models:ModelID[], errorCode?:ErrorCode}
SettingsResult {profileId, profileRevision, credentialRevision,
                credentialState:"absent"|"stored"|"unavailable"|"cleanup_pending",
                maskedTail?:string, modelId?:ModelID, enabled:boolean,
                testReceiptId?:ID, models:ModelID[]}
ConversationPage {conversationId, revision, turns:ConversationTurn[], nextCursor?:ID}
ConversationTurn {turnId, questionId, questionVersion, text, createdAt,
                  previewState?:PreviewState, dispatch?:DispatchResult,
                  answer?:AnswerResult, feedbackIds:ID[]}
```

字典内所有revision/version/generation/epoch均u53正整数；计数、usage、startScalar及预算已用量为u53zero（0..9007199254740991），endScalar>startScalar且不越过原段长度，expiresAt/createdAt等时间为u53zero；tokenEstimate为u53zero估算。state/status字符串严格采用列出的枚举。TextAnswer即上述16000 scalar/65536字节答案；DispatchState即DispatchResult所列4态。Citation.source须与本地包内source逐字段一致。Preview.items最多6项（3来源+3纠正）；各字符串总量仍受预算约束。

Conversation分页游标为后端不透明ID，绑定会话/排序位置/快照revision；旧revision返回 `cursor_stale` 后客户端刷新第一页并按turnId去重，不重新发送。凭据及发送内部body永不通过通用snapshot返回。引用SourceRef只用于本地点击，实际网络payload仅citationId与片段，不包含路径/文件标题/connectorID或本地hash。

## 5. 错误码及恢复分类

| 固定码 | 动作 |
|---|---|
| dto_rejected / unknown_field / duplicate_field / identity_rejected / integer_rejected / operation_rejected / version_rejected | 请求未执行，修正DTO；零网络 |
| local_activation_required / source_database_missing / store_contract_mismatch / database_unavailable / database_path_rejected | 保留草稿，停止该次操作，不创建或迁移旧库 |
| draft_stale / draft_conflict / draft_missing / text_rejected / turn_conflict / idempotency_conflict | 同内容同ID可查回执，冲突需重新编辑，不覆盖 |
| source_missing / authorization_rejected / context_stale / context_budget_rejected / sensitive_content_rejected / query_rejected / cursor_stale | 零发送；刷新本地预览。无匹配是no_match成功状态，不伪造答案 |
| preview_missing / preview_expired / preview_stale / preview_consumed / confirmation_rejected | 零新发送；consumed可查询既有dispatch |
| provider_not_enabled / provider_revision_conflict / model_not_tested / real_capability_denied / external_targets_disabled / source_scan_disabled | 零发送；明确功能/授权状态 |
| credential_invalid / credential_reference_rejected / credential_revision_conflict / credential_unavailable / credential_missing / credential_authentication_failed / credential_cleanup_pending | 不降级明文/会话保存，不找旧service |
| dispatch_persistence_failed | 网络前持久化失败，零发送 |
| provider_authentication / provider_model / provider_protocol / provider_unavailable / response_too_large | 已调度即不可自动重试；错误正文丢弃 |
| dispatch_outcome_unknown | 超时、断网、崩溃或发送后结果落库失败，显示可能已发送；无自动重试 |
| answer_missing / answer_revision_conflict / feedback_scope_rejected | 不改其他回答；刷新对应回答 |

Transport内部错误映射固定枚举，不能把curl stderr或服务商响应体拼入code。ErrorCode即上表所有码的封闭联合；保留的v1/v2老分支仍使用其原错误码。

## 6. 实现落点（均拟在148 candidate，当前不创建）

- `src/main.rs`：新增26号注册、按版本分派严格DTO；禁止从旧offline dispatch直通网络。
- `src/conversation_api.rs`、`src/conversation_store.rs`（拟新增）：严格解析、事务、投影；API不暴露SQL/通用Value权威。
- `application/core.ts`及拟 `application/source_conversation.ts`：Application/Orchestrator、用户状态流与ModelPort DTO；不把整个领域逻辑迁到Rust。
- `src/source_store.rs`：有界检索与本地有效性复验；`application/ui.ts`：草稿→预览→单次确认→回答/纠正，保持现有导航和视觉资源。
- `src/provider_api.rs`、`src/provider_store.rs`、`src/secure_credentials.rs`、`src/deepseek.rs`：专用凭据/Provider Adapter；生产边界由Rust重复强制执行，见03。
