# Closure-2 dynamic synthetic/offline matrix

All values below are review-owned metadata. The only text inputs were the fixed synthetic fixtures sealed in `../test_design.md`. No key material, real content, or database body was copied into this artifact.

| Matrix point | Direct observed result | Network proof |
| --- | --- | --- |
| No credential before setup | The UI disabled testing before a credential was saved. | No adapter action was available. |
| Fixed canary save | The fixed non-secret canary was accepted, the visible input cleared, and only the masked `••••real` suffix remained. The SQLite credential row contained AES-256-GCM metadata only (ciphertext 38 bytes, nonce 12 bytes, tag 16 bytes). | Saving did not expose a test/send control result. |
| Synthetic model/read and activation | UI reported `合成模型目录测试完成；未执行网络请求`; the only returned model was `deepseek-synthetic-v1`; explicit enable was required. | `lsof -nP -a -p 64146 -i` was empty after model testing/first response; `lsof -nP -a -p 64216 -i` was empty before and after the second response. |
| First request and confirmation feedback | Exact three-item local disclosure preview (Health, durable memory, Work) preceded confirmation. UI returned a typed Understanding and then changed feedback controls to `已确认`. | No sockets after response or feedback. |
| Restart persistence | A new exact-app PID `64216` displayed the masked credential, enabled synthetic service, response, and `已确认` feedback state. | Restarted PID socket inspection was empty. |
| Missing-key failure | After deletion of the synthetic Keychain canary, UI test returned `密钥材料不存在；已在网络前拒绝。` | Socket count stayed zero; the credential row and pre-existing derivation/feedback counts did not change. |
| Restored canary and correction | A second locally previewed, once-confirmed request produced feedback controls. `纠正` changed the UI to `已纠正并失效` and Today to `相关 Today 投影为 invalidated` / `撤回或重算受影响理解`. | Socket count was zero immediately before and after this response and after correction. |

Runtime-owned, non-content network receipt ledger recorded exactly four adapter operations: two `test_models` and two `confirmed_minimal_context`. Each recorded `authority=https://api.deepseek.com`, `methodClass=NONE`, `requestBucket=0B`, `responseBucket=0B`, and `statusClass=synthetic_no_network`. It is consistent with the live-PID socket observations; it is not a real network ledger.

Non-content persistence snapshot also established: two `understanding` derivations, both `deepseek` / `deepseek-synthetic-v1`, with source-ref JSON length 66; their terminal statuses were one `confirmed` and one `invalidated`. Both disclosure records were `work`, `previewed=1`, `confirmation_used=1`, source-ref JSON length 66. The synthetic SQLite file mode was `0600`.

Final synthetic SQLite count/status snapshot before cleanup:

```text
credential|1
derivation_pending|0
derivation_confirmed|1
derivation_invalidated|1
feedback_confirm|1
feedback_correct|1
context_assembled|2
context_item_saved|3
disclosure_confirmed|2
disclosure_previewed|2
understanding_feedback|2
understanding_saved|2
```

The database schema deliberately did not persist `method_class`/`status_class` columns. The no-network receipt class is therefore evidenced by the independent static runner, the UI’s synthetic/no-network status, and the repeated live-PID socket inspections rather than invented database columns.
