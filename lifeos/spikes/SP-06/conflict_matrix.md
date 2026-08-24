# Conflict matrix

| Concurrent inputs | Automatic result | User-visible state |
|---|---|---|
| Two original edits from one base | Keep both immutable versions; one current, one conflict branch | “有两个离线版本待合并” |
| Candidate accept vs reject | Preserve both attempts; do not LWW | “这个建议在其他设备上有不同处理” |
| Edited accept vs original accept | Preserve edited payload digest and both attempts | “确认内容不一致，请选择” |
| Action complete vs defer | Apply first valid base; append stale attempt as conflict | “完成与延期冲突，当前未自动改写” |
| Decision revision vs old restore | New revision remains authoritative; old restore is stale | “恢复内容已过期” |
| Link confirm vs correct | No field LWW; explicit relationship conflict | “关系需要复核” |
| Feedback retract vs dependent state change | Retraction is appended; dependent projection recomputes or requests review | “反馈已撤回，相关状态待复核” |
| Tombstone/revoke/disconnect vs old write/job | Monotonic fence rejects the old operation | “旧设备内容未恢复；可查看原因” |

No text merge, semantic merge, or field-level LWW is attempted in this spike.
