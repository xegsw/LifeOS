# P3-109 启动前 ABF 路径冲突分析

- 记录时间：2026-08-24T03:50:34Z
- 结论：`Blocked — Frozen ABF ambiguity/contradiction before execution`
- 依据：`ABF-P3-109-v1`，未修改。

## 已核对的互斥要求

1. ABF M-005 / I-03 要求独立的离线 locked `test/build/bundle`；任务卡把这项写为本轮必要 Evidence。
2. ABF I-04 规定所有写入必须仅命中逐字枚举的临时路径。ABF 第 22 行仅允许一个 review work 副本和 13 个 `lifeos-p3-104-p3-109-review-...-v1` 路径，并明确不授权 broad prefix 或其他后缀。
3. 候选只读源码 `lifeos/engineering/LIFEOS-P3-106/src/runtime.rs:695-705` 包含 Rust unit-test 模块。其 `fixture()` 以 `/private/tmp/lifeos-p3-104-unit-{name}-{pid}` 创建目录；后续测试还会创建 `lifeos-p3-104-unit-link-target-*` 与 `lifeos-p3-104-unit-link-*`（见同文件 799-804 行）。

因此，执行 `cargo test --locked` 会写入 `lifeos-p3-104-unit-*`；这些路径不属于 ABF 第 22 行的逐字枚举目录。省略 `cargo test` 又会使 M-005/I-03 未执行。两条冻结要求不能同时满足。

## 已采取的安全动作

- 在任何 candidate 复制、build、test、bundle、fixture、app 启动、GUI 操作或 `/private/tmp` P3-109 目录创建前停止。
- 仅以 `lstat` 记录了禁止读取内容的历史临时文件元数据；没有读取其内容。
- 没有读取、复制、导入或执行 P3-107/P3-108 的 runner、工具或动态 Evidence。
- 已保留本轮独立测试设计和未执行的 task-local runner 源码，供 PM 判断后续新 ABF／新任务时只读审计；两者均不是当前 PASS Evidence。

## 需要 PM 的决定

Frozen ABF 不可在本任务内实质修改。请 PM 按 ABF 启动前质疑窗口和 D-0401 治理决定：关闭本任务并以新授权、新 ABF 明确允许候选 unit-test 临时路径，或以新任务重新定义 M-005 的可接受独立测试入口。未作该决定前，本专项不得继续。
