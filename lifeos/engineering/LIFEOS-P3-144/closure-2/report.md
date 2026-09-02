# LIFEOS-P3-144 Closure 2｜Profile 对齐与测试生命周期隔离

## 结论

本轮只关闭 `independent-re-review-1` 的 P1：完整串行回归在冻结 `independent-review` profile 下存在测试顺序依赖。候选产品功能、20 IPC、DeepSeek authority、Work／Health 语义、UI、Schema、Provider、真实 Gate 和 ABF 均未修改。

整改后：

- `engineering` profile 完整离线串行 Rust：21/21 Pass。
- `independent-review` profile 完整离线串行 Rust：21/21 Pass。
- 离线合同：21/21 Pass，恰好 20 IPC，synthetic mode。
- `cargo fmt --check` 与 LifeOS governance guard：Pass。
- 两个固定合成根在测试后均不存在。
- P0=0，P1=0，P2=0，Unknown=0，Not Implemented=0（本 Closure 范围）。

## 修改

1. 为 Phase-A 上下文测试增加 profile-aware 生命周期守卫。
2. 守卫在退出时验证编译期精确根、0600 普通 marker、marker 内容和 0700 普通 runtime 目录，再逐项删除文件／空目录；不使用宽泛递归删除。
3. CI 清单同时固定执行 `engineering` 与 `independent-review` 两套完整串行 Rust suite，禁止再以单测或错误 profile 替代评审前置回归。

## 边界

- Pilot-7、真实 DB、真实文本、真实凭据、DeepSeek 网络及其他 Provider：零接触。
- `independent-re-review-1`、P3-143 和更早历史：只读保全。
- 本报告仅为同任务工程 Closure Evidence，不是独立评审、PM Pass、Phase C、风险关闭、冻结或 Stage 4 准入。

## 下一关

以本轮新候选 identity 进行最后一次全新隔离 Phase B 独立复评。复评必须在候选接触前封存自有 controls，并在固定 `/private/tmp/lifeos-p3-144-independent-review-v1` 下执行冻结 profile 完整回归和剩余 review-owned mutation；窄视口问题只按 Evidence Gap 补取，不得把环境／截图问题误判为产品 Rework。
