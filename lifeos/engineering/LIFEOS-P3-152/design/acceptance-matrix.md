# P3-152 合成阶段 A01–A09 包内矩阵

本表为执行侧自检，不是独立评审或 PM Pass。依据 contract-inputs/synthetic-ABF-v1.md；真实阶段未启用。

| ID | 结论 | 可复核证据与边界 |
|---|---|---|
| A01 | Pass（合成） | gui-preview/answer/narrow-answer/failure/cancel-after-dispatch/restart-draft 的 JSON+PNG；integration-tests-final.json 8/8，失败保留草稿、新预览重试、取消迟到隔离。窄屏700×762，宽屏1280×949。 |
| A02 | Pass（合成） | host-tests-final.log：权限/跨域/ref/预算/失效、future_or_wrong_metric、old_projection_invalidated_even_after_large_unrelated_history；TS本地选择与Host预算双校验；gui-final-date-filter 明示今天无来源观察。自然语义采用有限规则，不宣称通用语义检索。 |
| A03 | Pass（合成） | exact_preview_body_is_only_body_sent_and_duplicate_consumes_once 的 Spy 比较完整 body、问题与 items；stale_model_draft_source_or_credential、readonly_health_source_bytes_unchanged_and_changes_invalidate_preview；客户端body/确认token伪造拒绝。 |
| A04 | Pass（合成） | concurrent_duplicate、second_preview、restart_inflight、cancel_after_handoff；集成取消/迟到/重试不重复；mutation confirmation/expiry 被检出。GUI明确不能保证撤回已发送内容。 |
| A05 | Pass（合成） | provider_store 三项加密/AAD/篡改/替换/删除测试；provider_transport 两项固定错误与合成禁网络测试；remote_key_echo 测试与对应mutation；虚构凭据重启保留。OS CredentialPort未调用，真实Keychain能力未验证。 |
| A06 | Pass（合成） | readonly_health_source_bytes_unchanged_and_changes_invalidate_preview、unknown_estimated_and_multi_source_are_preserved_without_source_writes、sidecar失败关闭；测试前后合成健康库字节相等。fixture构造/攻击由测试显式写入，SourcePort只读路径无业务写入。 |
| A07 | Pass（合成） | 未确认Spy调用0，重复确认1，过期/撤权/模型/凭据变化0；runtime_root::is_real固定false，真实transport前置拒绝，模型选择纯本地，无models/testconnection/fallback。 |
| A08 | Pass（合成） | API Key专用IPC不进入会话audit/requests，错误固定分类、远端原样Key回显拒绝；input-preservation-final.json复算151全部178项和报告1项。code-inputs.json为收口代码身份登记，不伪称预接触seal。全部动态内容为synthetic；无真实内容捕获。 |
| A09 | Pass（合成） | checkpoint.json、FINAL_MANIFEST.json、tools/verify_package.py、verify_inputs.py、rerun.sh、mutations.py；mutation日志已包内保存。GUI修正影响面见gui-reuse-impact.json；临时锁屏恢复后定向续跑。 |

36/36 Host、8/8 TS→Host、3/3 code mutation killed。P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0（仅本合成阶段）。整体任务另有 Not Implemented=1：真实存储/凭据目标未获授权，真实运行与用户确认发送闭环未启用；此项不冒充合成阶段已实现。
