# LIFEOS-P3-141 Attempt-8 Closure engineering report

## 工程门结论

**Phase A Ready for Independent Review；Phase C build/launch 明确 Pending。** attempt-7 的唯一 P0 已在编译期关闭：`phase_c_real` 现在只接受一份未来、独立评审工作树中已提交且只读的结构化 Pass receipt。旧的 `LIFEOS_P3_141_PHASE_B_RECEIPT` 字符串无论内容为何都直接拒绝；receipt 缺失时在读取或解析 runtime root 之前失败关闭。

本结论只覆盖唯一临时根内的离线合成回放和负例。工程会话没有、也不能生成一份可被 gate 接受的 receipt；Phase B 独立评审和 Phase C/D/E 仍未开始。

## 本次修复与验证

- 新增显式编译模式：`synthetic_review + synthetic` 不读取 Phase-B receipt，可完整运行通常合成评测；`phase_c_real + real_self_use` 在 runtime-root 解析之前要求 `LIFEOS_P3_141_PHASE_B_RECEIPT_PATH`。
- verifier 只接受 review-owned `lifeos/reviews/LIFEOS-P3-141/independent-review/<attempt>/phase_b_pass_receipt.json`：绝对规范路径、所有祖先非链接、单一只读 regular file、受限大小、同一 Git common directory 中声明的 peer worktree、同一文件 owner、clean HEAD 内容一致、精确 schema/无重复字段/无额外字段、task/ABF hash、Pass verdict、review Manifest hash/identity、candidate commit/tree 均须匹配。receipt、Manifest、目录、链接、祖先链接、伪造/陈旧候选、错误 ABF、Rework、Blocked、损坏/重复/额外字段、错误 Manifest hash、无关 Git root 和 dirty history 都在构建前拒绝。
- 离线 gate 回归为 **1 个 synthetic-review 正编译 + 17 个负例**；测试夹具故意绑定错误 candidate，或以精确 candidate binding 证明无关 Git root 仍拒绝；未生成或接受任何 Pass receipt。
- 完整 Phase-A synthetic replay 为 **48/48**；固定输入 12/12、P3-140 baseline 79/79、current candidate 79 files/恰好 20 IPC 均由 replay verifier 复核。Provider 四选一/loopback、Resolver、Work、Memory、五字段 Health、Today/feedback、root 与失败关闭回归未下降。
- 以最终 current `synthetic_review` bundle 新鲜启动 desktop PID 56928、compact PID 56982、narrow PID 57047；每一行均为 direct PID→exact-title 唯一 AXWindow→原生 `AXWebArea`，并有三张无敏感截图和 post-`set_size` receipt。它们只证明 Phase-A UI/AX；旧“receipt-enabled real mode”及本轮 peer-ownership 前资产已移入历史，不能为新的 Phase-C receipt gate 背书。

## Evidence 与复跑

- receipt schema/binding/public verifier contract：[phase_b_receipt_contract.md](evidence/phase_b_receipt_contract.md)。
- 离线反例结果：[phase_b_receipt_gate_regression.json](evidence/phase_b_receipt_gate_regression.json)；完整 48/48 日志：[attempt-8-replay.log](evidence/attempt-8-replay.log)。
- 逐行状态：[ABF_PHASE_A_MATRIX.md](evidence/ABF_PHASE_A_MATRIX.md)；current source lineage、Manifest、Mutation、失败历史与 exact cleanup receipt 位于 `evidence/`。
- 可移植入口：[replay_phase_a.sh](tools/replay_phase_a.sh)。调用时传 `--input-root /absolute/worktree`；该入口显式采用 `synthetic_review` 并且只清理唯一临时根。

## 五类计数与 PM 下一步

- P0：0（attempt-7 的字符串 bypass 已由离线 17 负例覆盖。）
- P1：0。
- P2：1（本机 Rust toolchain 未安装 rustfmt；`cargo fmt --check` 不能执行，见 `evidence/attempt-8-rustfmt.log`。）
- Unknown：0（仅工程可验证的合成范围）。
- Not Implemented：1（独立 review-owned Pass receipt 尚不存在，因此 Phase-C real build/launch 有意不可用；Phase B/C/D/E 全部 Pending）。

需要新的隔离独立评审生成其自身 receipt 后，才可尝试 Phase-C gate；本工程会话不得自行启动任何真实 Pilot。
