# LIFEOS-P3-127｜P3-126 清洁启动候选独立复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-127`
- 被评审能力包：P3-126 已获 PM Pass 的 final candidate；受控能力包：Yes。
- 独立评审角色：路径安全、Rust/Tauri Runtime、Evidence QA；协审视角：数据主权、授权不漂移、生命周期、历史保全。
- 独立性：全新 Codex 会话、P3-127 自写 `runner.py`／`history_verify.py`、全新 review 根和唯一 disposable 根；未 import、复制或调用 P3-126 historical runner。
- 评审关卡：Gate 2、Gate 4；Gate 1/3 仅作零产品／接口漂移核对；Gate 5 不适用。
- 评审结论：**Pass**。
- 风险等级：L3 / Gate（Frozen `ABF-P3-127-v1`）。
- 评审触发事实：P3-126 PM Pass 与用户采纳后，冻结合同要求全新隔离的 actual-Tauri 独立复评。

## 冻结启动与范围

- P3-127 task／ABF／source allowlist 的 SHA-256 分别为 `3504a3e2…e988`、`f44199a2…4966`、`5d45d866…ef72`；allowlist 为 75 个物理、机器可读、无语义坏行的 source rows。见 `evidence/preflight.json`。
- Frozen M001 的 model/effort 路由以用户作为平台操作方的明示确认完成绑定；本评审未把环境工具不可见误写为自证。见 `evidence/user_model_attestation.md`。
- P3-126 candidate、task、ABF、Evidence、delivery、Review 及上游历史全程只读。没有访问、stat、hash、创建或清理旧 P3-122 Runtime root；无网络、模型、云、真实数据、额外 IPC/capability 或账本变更。
- 运行根唯一权威为构建时 `LIFEOS_RUNTIME_ROOT`；所有 App/DB/mutation/Cargo 临时输出仅在已删除的精确 disposable 根中发生。

## 冻结矩阵逐行闭环

| ABF 行 | Frozen action | 测试 ID | 实际 Evidence | 结论 |
|---|---|---|---|---|
| M-001 | 冻结 inputs、75 行、授权、两根初始不存在、平台确认后才读 candidate/建根 | P127-M001 | `evidence/preflight.json`、`evidence/user_model_attestation.md` | Pass |
| M-002 | 自写 runner，不得复用 P3-126 historical runner | P127-M002 | `runner.py`、`history_verify.py`、`evidence/independence.json`、空匹配 `independence-executable-scan.txt` | Pass |
| M-003 | 独立重算 75-file source/candidate lineage | P127-M003 | `evidence/source-lineage.json`、`copy-lineage.json`、`source-lineage-post.json`：各为 75/75、0 failures | Pass |
| M-004 | isolated copy 的 locked offline serial test/build/bundle | P127-M004 | `evidence/build-results.json`、`run-a-cargo-test-serial.log` 4/4、`run-a-bundle.log`、`run-b-bundle.log` | Pass |
| M-005 | 两个新根分别构建运行 actual Tauri | P127-M005 | `evidence/roots-results.json`；A/B 各有首屏截图、SQLite 与 PID 命令行 | Pass |
| M-006 | status、first、repeat、refresh、close/reopen | P127-M006 | `evidence/runtime-results.json`；A 为 `0/0→1/1→1/2→reopen 1/2`，B 为独立 `0/0→1/1→1/2`；UI/IPC 回执、SQLite 与 PID 交叉一致 | Pass |
| M-007 | path/type/symlink/DB/atomic failure 先于状态变更关闭 | P127-M007 | `run-b-cargo-test-serial-nocapture.log` 与 `evidence/negatives.json`：7 个 blocked code、4/4 test pass | Pass |
| M-008 | 仅三 IPC、禁止能力／旧根零触达 | P127-M008 | `static-ipc-scan.txt`、`static-boundary-scan.txt`、`evidence/boundary.json`；actual UI 为 Offline · 3 IPC | Pass |
| M-009 | 重算 P3-126 frozen assets | P127-M009 | `evidence/history.json`：P3-126 Final Manifest 的 123/123 entries byte/SHA 一致；`p3-126-protected-post-sha256.txt` | Pass |
| M-010 | pristine 后逐类 disposable mutation 必须 fail closed | P127-M010 | `evidence/mutation-results.json`；content、missing-file、symlink 三类均被 P3-127 runner 拒绝 | Pass |
| M-011 | App 关闭后精确清理唯一 temp root | P127-M011 | `app-process-after-close.txt`（无 App PID）与 `evidence/cleanup.json`：精确 root absent | Pass |
| M-012 | 逐行闭环、非自指 Manifest、Review 与交付摘要 | P127-M012 | 本 Review、`FINAL_MANIFEST.json`、专项交付摘要；Manifest 覆盖 inputs、runner、Evidence、Review 与 cleanup，且排除自身 | Pass |

## 实际 App 取证说明

- Run-A 的实际 Tauri WebView 初始 AX attestation 为 `restricted_offline,0,0`；首次 capture 产生 `p3-122-000001a03c99570e-p3-122-synthetic-one`，repeat 明示未创建重复记录，SQLite 为 1 capture／2 audit，关闭重开仍为 1／2。截图：`run-a-ui-initial.jpeg`、`run-a-ui-capture-first.jpeg`、`run-a-ui-idempotent-repeat.jpeg`、`run-a-ui-restart-persisted.jpeg`。
- Run-B 在独立 build-time 根重复同一 lifecycle，首次 record 为 `p3-122-000001a03c9c0d12-p3-122-synthetic-one`，SQLite 仍为 1 capture／2 audit，PID 命令行指向本轮 bundle。截图：`run-b-ui-initial.jpeg`、`run-b-ui-capture-first.jpeg`、`run-b-ui-idempotent-repeat.jpeg`。
- GUI 子进程被 macOS 启动时没有向重定向 stderr 写出内容；该空通道没有被当作正证据。actual-App 结论由界面 IPC 回执、截图、SQLite/audit、PID/命令行及 AX attestation 共同绑定；`run-b-cargo-test-serial-nocapture.log`仅作为同一 runtime 的补充 IPC/失败关闭日志，不替代 actual-App 证据。

## 例外、计数与独立性裁决

- `cargo test --locked` 的默认并行调用曾因测试 fixture 共用编译时根而发生测试间清理竞争；它没有修改 candidate 或生成成功假象。P3-126 的冻结 Evidence 指定 serial Rust test，独立的 serial `--test-threads=1` 两次均为 4/4 pass。因此这是已保留的 test-invocation 诊断，不是候选 Runtime 的 P2 或本 ABF 行失败。
- P0：0；P1：0；P2：0；Unknown：0；Not Implemented：0；silent N/A：0。
- 未发现 Evidence 冲突、历史漂移、授权扩张、额外能力、candidate 改动或独立性不足。无需回到 P3-126 Closure Cycle。

## 关卡、风险与 PM 回流

- Gate 1：Pass（仅核对零产品／接口漂移；无产品冻结结论）。
- Gate 2：Pass（全程 synthetic、最小 IPC、SQLite/audit、失败关闭与历史保全已复核）。
- Gate 3：Pass（AI、网络、vault、export、sync、renderer direct capability 均关闭；无新增信任边界）。
- Gate 4：Pass（离线 bundle、双根 actual Tauri lifecycle、负向与精确 cleanup 均可复核）。
- Gate 5：N/A（无 Pilot、真实用户或价值验证）。
- 风险：不关闭或更新任何风险条目；Stage 4、风险关闭、产品／架构／Schema/API 冻结均不在本结论内。
- 需要 PM 决策：无新的产品或风险决策；PM 仅应按既有流程记录本独立复评的 Pass，不得将其误写为 Freeze、Stage 4、risk closure、PM Pass 或用户采用。

## 最终建议

建议将本 P3-127 独立复评作为 P3-126 清洁启动候选的独立 Evidence 输入。结论范围只覆盖 Frozen offline synthetic actual-Tauri contract；不构成真实能力启用、用户价值验证、产品冻结或下一阶段准入。
