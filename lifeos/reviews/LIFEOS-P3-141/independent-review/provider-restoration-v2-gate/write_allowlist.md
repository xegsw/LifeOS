# 本轮写入白名单

## 唯一允许写入

- `/Users/xxe/.codex/worktrees/0d00/No.2/lifeos/reviews/LIFEOS-P3-141/independent-review/provider-restoration-v2-gate/`
- `/private/tmp/lifeos-p3-141-provider-restoration-v2-independent-review-v1`（仅在预接触有效且动态评审获准启动时）

## 本轮实际写入

仅第一个路径中的 fail-closed 评审记录；本审查未创建、探测或清理临时根。

## 明确禁止

- 候选、工程目录、PM 账本、P3-140、旧 P3-141、历史 Review/Evidence/Manifest 的任何写入。
- `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-6` 及其 `capture.sqlite` 的任何 access、exists、stat、inventory、hash、read、write、copy、create 或 cleanup。
- 其他 Pilot、真实数据、真实 Provider、凭据、网络、云、第三方、产品模型和新 IPC。
