# SP-05 dependency registry

本登记是合成 Spike 的候选分类，不是正式 Schema。显式登记缺失、扫描不完整或边界未知时，运行时必须默认阻断，不能以“稍后清理”替代。

| Dependency type | Discovery | Block / cleanup rule | Class |
|---|---|---|---|
| `user_original` | explicit | block; delete only for delete_content | controllable |
| `external_original_copy_or_pointer` | explicit | disconnect pointer; external original is out of control | boundary |
| `artifact_version` | explicit | block/invalid; delete targeted versions | controllable |
| `content_chunk` | explicit | block then delete | rebuildable |
| `fts_posting` | scan+explicit owner | query filter then rebuild/delete | rebuildable |
| `vector_mock` | scan+explicit owner | query filter then delete | rebuildable |
| `summary` | explicit inputs | invalid/rebuild lawful subset | rebuildable |
| `recovery_fragment` | explicit inputs | exclude then rebuild | rebuildable |
| `ai_candidate_action` | explicit inputs | invalid; L1 default | rebuildable |
| `ai_candidate_decision` | explicit inputs | invalid; L1 default | rebuildable |
| `important_link` | explicit evidence | invalid/review | rebuildable |
| `confirmed_object` | explicit evidence | retain history; review_required | user-history |
| `feedback_history` | append-only reference | retain; retract current effect | user-history |
| `cache` | namespace scan | evict | rebuildable |
| `prompt_copy` | explicit manifest | delete or irreversibly redact | avoid-retaining |
| `queue_payload` | explicit manifest | claim filter then delete/redact | rebuildable |
| `object_file_or_pointer` | explicit owner | delete controllable file/pointer | boundary |
| `backup_copy` | backup manifest scan | tombstone-first restore; expire/rewrite later | windowed |
| `offline_copy_or_outbox` | device/outbox manifest | reject replay; clean when reachable | windowed |
| `third_party_mock_copy` | send manifest | delete request or vendor_limited | vendor-boundary |
| `audit_entry` | command reference | retain minimal non-reconstructable fields | minimal-history |
| `cleanup_proof` | cleanup job reference | retain minimal non-reconstructable result | minimal-history |
