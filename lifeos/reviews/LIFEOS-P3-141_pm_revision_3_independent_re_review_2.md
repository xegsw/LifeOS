# LIFEOS-P3-141 Revision 3 Independent Re-review 2 — PM Intake

## 结论

- PM结论：Rework / P0 confirmed。
- 候选commit `60a93746`的Engineering Gate Pass当前效力撤回；工程历史与Evidence只读保留。
- 本轮独立性和输入门有效。评审复算fixed inputs 4/4、工程Manifest 124/124、candidate 80/80及两场失败历史后，以全新评审根执行构建并确认P0。

## P0事实

- `candidate/build.rs`把`/private/tmp/lifeos-p3-141-model-settings-revision-3-v1`硬编码为唯一synthetic父根。
- 全新评审根`/private/tmp/lifeos-p3-141-revision-3-independent-review-v3`在build.rs阶段以exit 101被拒绝，错误为`runtime root must be a direct child of the authorized Revision-3 synthetic root`。
- 这迫使评审复用工程期root，违反ABF3-M-011／012的全新隔离与不复用运行事实要求。
- 构建在runtime前停止；候选前后80-file tree不变，无DB、secret、loopback、PID、网络或禁止目标接触。

## 五类计数

- P0：1
- P1：0
- P2：0
- Unknown：0
- Not Implemented：11

## Closure

- 同一P3-141修正root authority：允许每次显式、task-scoped、marker验证的全新P3-141 synthetic root，而不是固定工程root，也不得变成任意路径授权。
- 必须覆盖absolute/normalized、`/private/tmp`直系、任务名前缀、real directory、非symlink、0600 marker、marker内exact authorized_root、runtime direct child，以及错误root／marker／symlink／traversal写前失败关闭。
- 不改变Cloud五项、Local三项、API Key SQLite密文、20 IPC、UI、Pilot或风险边界。
- 修复后工程侧完整复跑并重建Manifest；随后由不同全新worktree重新独立复评。
- 原一次授权继续覆盖，无需用户确认或新产品任务。

## 状态

- Phase C保持暂停；Pilot-6、真实Provider／凭据继续零触达。
- R-0056保持Open；ABF-v3不修改；产品未冻结；Stage 4禁止。
