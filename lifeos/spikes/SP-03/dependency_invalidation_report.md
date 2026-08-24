# SP-03 依赖失效报告

## 结论

- 显式 `Derivation.inputs` 依赖边进行传递闭包查询。
- 六类触发共预期命中 15 个 Derivation；漏报 **0**，误报 **0**，无法解释的全库失效 **0**。
- `version_modified` 进入 `stale`；删除、断源、撤权进入 `invalid/inactive`；来源不可达进入 `stale + evidence_unavailable`；Feedback 撤回按直接依赖重算。
- 用户已确认 Decision 的唯一证据失效后，`recognition=confirmed` 历史保留，同时 `evidence_unavailable=true`、`review_required=true`、`automatic_basis_active=false`。

## 逐项结果

| 触发 | 目标 | 预期 | 实际 | 漏报 | 误报 | 结果 |
|---|---|---|---|---:|---:|---|
| version_modified | version-obs-v1 | deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | 0 | 0 | PASS |
| source_unreachable | artifact-web-material | deriv-decision-v1, deriv-multi-v1 | deriv-decision-v1, deriv-multi-v1 | 0 | 0 | PASS |
| disconnect_source | artifact-obs-note | deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | 0 | 0 | PASS |
| delete_content | artifact-web-material | deriv-decision-v1, deriv-multi-v1 | deriv-decision-v1, deriv-multi-v1 | 0 | 0 | PASS |
| revoke_processing | auth-local-a | deriv-feedback-v1, deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | deriv-feedback-v1, deriv-multi-v1, deriv-next-v1, deriv-recovery-v1 | 0 | 0 | PASS |
| retract_feedback | feedback-action-edit | deriv-feedback-v1 | deriv-feedback-v1 | 0 | 0 | PASS |
