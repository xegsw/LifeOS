# LIFEOS-P3-112 独立测试设计（冻结版）

## 冻结记录

- 创建时间：2026-08-24T16:44:46+0800
- 创建会话：全新 Codex 独立评审会话；本会话未参与 P3-104 至 P3-111 的工程、评审或 PM 验收。
- 投递授权：用户于本会话投递 `/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review.md`。
- 任务卡 SHA-256：`d57c9c36a8e9a7cc3431ffd290a53d203d28a9c406bba6266c18d790bdfd8bc3`
- Frozen ABF：`ABF-P3-112-v1`；SHA-256 `780ffb07c8f1bd4948ae568771f7b5c334d7fd7bcc2de925a38edcf95e9f78bf`（已复算）。
- 依据：任务卡、Frozen ABF 与 L1-1 至 L1-10；本设计不修改 ABF 或被评审候选。

## 读序声明

在本文件创建前，评审方**未读取、导入、复制、执行或语义分析**下列 P3-111 工程资产：

- `lifeos/engineering/LIFEOS-P3-111/tools/semantic_verifier.py`
- `lifeos/engineering/LIFEOS-P3-111/tools/run_disposable_mutations.py`
- 初次／Rework `semantic-verifier-result.json`
- 初次／Rework `mutation-results.json`

此前仅已阅读任务治理文件、当前状态、P3-112 任务卡、P3-112 Frozen ABF、L1 与评审模板；尚未创建临时副本，未运行 test/build，未查询、metadata、打开、读取、hash、复制或清理 Pilot-2，未启动真实 app。

## 不可越界约束

- 不访问 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2` 或其 `capture.sqlite`（包括路径查找、metadata、open、read、hash、copy、cleanup）。
- 不启动 P3-111 Tauri app／binary，不联网；不读写 P3-111、PM 账本、ABF 或历史 Evidence。
- 唯一临时写入根为 `/private/tmp/lifeos-p3-112-review-v1`；启动前必须不存在，结束时只精确清理此根并验证不存在。
- 评审 runner 由本评审独立编写，不能导入、复制或调用 P3-111 runner／verifier 作为通过主证据。

## 独立验证设计

1. 先复算 ABF 列明的 12 项固定输入和 72-file candidate tree；任一不符即 Blocked，停止 copy/build。
2. 对 P3-111 候选采用正向 allowlist 复制到唯一临时根；记录复制清单，确认 Evidence、tools 和既有 target 未被复制。
3. 仅在副本运行 `cargo test --locked --offline` 与 `cargo build --locked --offline`；收集命令、退出码、8 个固定非敏感 tests 与网络关闭事实。
4. 独立静态扫描候选三 IPC、capability、依赖、禁止路径／能力与内容来源边界。
5. 从 raw 初次／Rework Evidence 和 Manifest 独立复算动态闭环 12 行、脱敏／身份／来源条件及相关 SHA-256；不将汇总 PASS 当作动作证据。
6. 编写自有 verifier，检查 payload Manifest 的路径、hash、bytes、missing、extra 与语义字段；分别期望初次 37/37、Rework 38/38。
7. 将未经篡改的完整副本置于祖先含 `/disposable/noop` 的目录，验证 control 以 exit 0 且零 finding 通过。
8. 在六个互相独立的 disposable 副本分别进行缺文件、hash、cleanup、negative、lifecycle、geometry mutation；每项必须 exit 1，且仅出现该 mutation 的冻结预期原因。
9. 仅在自有主证据完成后，只读重放提交 verifier 作结果交叉比较；复核 `PM-CE-001`、历史/candidate 不变、风险/冻结/Stage 4 状态。
10. 生成逐行 M-001 至 M-015 closure matrix、非自指 Manifest 和精确 cleanup Evidence；所有零计数条件成立才建议 Pass。

## 判定规则

- 固定输入、candidate identity、会话独立性、模型／工具、真实数据零访问或临时根空基线不成立：Blocked。
- 候选或固定输入漂移、P0/P1，或需要 ABF／边界改变：交 PM，不能在本任务修复候选。
- 仅本任务 runner／Evidence 缺陷且 ABF 不变：Rework（当前正式预算 0/2）。
- 仅 I-01–I-11、M-001–M-015 及全部子动作通过，且 P0/P1/P2/Unknown/Not Implemented 全为 0，才建议 Pass；这不关闭风险、不冻结、不恢复基线或进入 Stage 4。
