# P3-141 Phase A 合成工程测试设计（预接触）

## 边界与方法

本设计仅适用于 `LIFEOS-P3-141` 的 Phase A 合成工程。唯一写入根为本目录；唯一临时根为 `/private/tmp/lifeos-p3-141-controlled-pilot-v1`。所有运行时资料均为明显虚构的 Work、Health/Fitness 状态及 loopback Provider 响应。测试、日志、截图、hash、Manifest、路径清理和代码中均不得出现、访问、探测或推导任何真实 Pilot、真实 DB、真实路径、真实正文、Health 值、凭据、真实 Provider 或网络。

Phase C 的真实根不属于本设计的输入、输出、预检、环境变量、扫描范围或清理范围。真实模式在 Phase B 独立 Pass receipt 缺失时必须以 `phase_b_independent_pass_required` 失败关闭。

## 冻结前置与谱系

1. 对 12 项固定输入逐项复算 bytes/SHA-256。
2. 复算 P3-140 只读候选的 79 文件 length-framed tree hash，要求等于固定清单值。
3. 仅在本文件、`write_allowlist.md` 与 `precontact_seal.json` 都已创建并哈希后，复制只读 P3-140 closure-1 候选。
4. 候选复制后，对本候选完整树、P3-140 候选以及所有固定输入产生只读谱系记录。
5. 所有最终 Evidence 通过独立 verifier 从 raw 文件重新计算；FINAL_MANIFEST 不列入自己的 entries。

## Phase A 合成场景

| 场景 | 合成输入 | 断言 |
|---|---|---|
| 单 Provider 激活 | 虚构 OpenAI profile + loopback endpoint | 保存、测试、启用、显式发送分离；只有启用 profile 可发送。 |
| Provider 锁定 | 首次 loopback 发送成功 | 后续切换、fallback、第二 Provider、Custom 和后台发送均拒绝。 |
| 最小披露 | Work 选择、已确认 Memory、当前 Health state | ModelPort 仅接收 request-scoped refs/计数，不接收完整 DB；disclosure receipt 不含正文。 |
| 跨域 Today | Work 压力 + 疲劳/可用时间 + 已确认约束 | Person-first 结果随长期 Memory 和当天 State 共同变化；不按 Domain 配额发卡。 |
| 反馈适应 | 合成纠正 | 旧 Understanding/Suggestion stale；重算结果不同且不复用旧 request_id。 |
| Health request-local 移除 | 第二次合成请求移除 Health | 本请求披露/结果无 Health；数据库本体未改；下一请求不继承移除。 |
| Health 安全停止 | 结构化高风险 signal | 返回非诊断的保守停止状态；无训练负荷建议。 |
| 失败关闭 | 授权、stale、预算、DB、Provider、模式 gate | 在 request/receipt/result/feedback/audit/Memory/State 写入及 dispatch 前失败；sentinel/计数不变。 |
| 重启 | 同一合成 DB 重开 | 不重发、不重复派生、不复活 stale、不复用 request_id。 |
| 真实模式 gate | `real_self_use` 请求 | 无 Phase B receipt 时拒绝且绝不接受真实路径参数。 |

## 动态和视觉计划

1. 仅从本候选构建并直接启动一次 Tauri bundle；记录每个运行的 bundle、binary hash、PID、唯一标题、AXWindow、AXWebView 与截图 hash。
2. 覆盖 desktop 1280x1024、compact 700x760、narrow 560x640。只显示合成界面，不显示任何真实内容。
3. desktop 覆盖单 Provider 激活、发送、锁定、Today、反馈 stale/recompute、Health safety stop；compact 覆盖 request-local Health removal；narrow 覆盖布局和安全状态。
4. 任何 PID、标题、AX 或 WebView 绑定不能证明时停止该动态证据链，不以静态扫描或 fixture HTML 替代。

## Mutation 与清理计划

1. 对 disposable candidate 副本变异：IPC 数量、Provider fallback、content-exclusion scanner、final manifest hash、候选树 hash、phase gate 及 Provider 锁定；每一种必须使 verifier 失败。
2. 测试用 SQLite 只放在唯一临时根；退出前由固定字面路径 cleanup 工具删除该根并验证 absent。
3. 不删除或清理任何真实资产；未实现 Phase C 行使用 `PENDING_PHASE_C`，不得表达为 PASS。

## ABF 映射

`ABF-M-001` 至 `ABF-M-007`、`M-010` 至 `M-016`、`M-019` 与 `M-020` 在 Phase A 以合成可观察事实验证。`ABF-M-003` 验证 Phase B receipt gate；`M-008`、`M-009`、`M-017` 与 `M-018` 是 Phase C/B 专属，工程矩阵明确标 `PENDING_PHASE_C` 或 `PENDING_PHASE_B`，不作为 Phase A PASS。
