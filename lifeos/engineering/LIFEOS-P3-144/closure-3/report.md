# LIFEOS-P3-144 Closure 3｜Pilot-7 真实运行 Profile 启用

## 结论

本轮在同一 P3-144 Task Contract 内补齐 Phase C 的编译期真实运行入口。候选现有三个不可混淆的 profile：

- `engineering` → 精确合成工程根 → `synthetic`
- `independent-review` → 精确冻结评审根 → `synthetic`
- `pilot-7` → 精确 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7` → `real_gate`

运行模式和根 profile 都由 `build.rs` 编译进二进制；运行时环境变量不能把 synthetic 二进制切换为真实 Provider。`verify_task_root` 在任何 DB 或网络动作前再次验证 profile／mode 对应关系、精确父目录、basename、root、owner、marker schema 和 run-id。

## 修改范围

- `candidate/build.rs`：新增唯一 `pilot-7` profile，绑定精确用户已授权根与 `real_gate`。
- `candidate/src/runtime.rs`：运行模式改为编译期绑定；新增 profile／mode 失败关闭和纯字符串 authority 反例测试。
- `candidate/tests/offline_contract.mjs`：增加 Pilot-7 精确 root、marker、mode 静态合同。
- `candidate/ci/checks.json`：增加 Pilot-7 离线 compile-only 检查。

UI、20 IPC、Provider、DeepSeek authority、Schema、数据额度、Health 非医疗边界、凭据方案和披露确认状态机均未修改。

## 工程验证

- engineering profile 完整串行 Rust：22/22 Pass。
- independent-review profile 完整串行 Rust：22/22 Pass。
- pilot-7 profile：`cargo check --locked --offline` Pass；没有启动 App 或执行 runtime。
- 离线合同：23/23 Pass，IPC=20，模式=`synthetic`＋`real_gate`。
- 非法 profile 与 pilot-7 携带 review run-id：build-time exit 101。
- `cargo fmt --check`、`git diff --check`、LifeOS governance guard：Pass。
- P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0（本 Closure 范围）。

## 边界

- 本轮没有对 Pilot-7 进行 access／exists／stat／create／read／write／cleanup。
- 没有真实 DB、真实文本、真实凭据、DeepSeek 网络或其他 Provider 接触。
- Phase B Pass 历史、P3-143 和更早资产只读保全。
- 这只是工程 Closure，不是增量独立复核、Phase C 启动、PM Accepted、风险关闭、冻结或 Stage 4。

## 下一关

对 Closure-3 delta 做全新隔离只读复核：只验证候选 lineage、profile／mode/root 静态与 compile-only 反例、两个 synthetic profile 22/22、20 IPC 无回退；禁止运行 pilot-7 profile。Delta Pass 后才能构建并打开真实 Pilot-7 App，由用户操作 Phase C。
