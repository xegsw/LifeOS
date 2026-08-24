# LIFEOS-P3-051 Evidence Manifest

## 1. 任务、授权与方法

- 任务：R-0049 风险关闭建议与 R-0048 边界复核。
- 执行任务：全新 Codex 任务 `01a021d6-6ef6-7d22-baa6-7cd695befcd0`。
- 实际配置：`gpt-5.6-sol` + `xhigh`；未降级、无后备模型。
- 数据/能力边界：只读核验本地候选 SQL、测试、Review、Evidence 和主账本；未连接真实 DB/Vault/Tauri/IPC/用户数据/网络/云/第三方模型，未执行真实 migration。
- 修改边界：仅创建 P3-051 决策包、独立 Review 与本 Evidence Manifest；未修改工程、历史 Evidence 或 PM 账本。
- 核验方法：逐文件读取、`rg`/`sed` 定向定位、`jq` 结构化计数、`shasum -a 256` hash 核对、规范化 JSON 语义对比。P3-051 未重新执行工程测试；复跑结论只引用 P3-050 独立 Evidence 与 PM Evidence。

## 2. 关键输入

- `lifeos/RISK_LOG.md`：R-0048、R-0049。
- `lifeos/DECISION_LOG.md`：D-0226 至 D-0237。
- `lifeos/FREEZE_STATUS.md` 与最新 `lifeos/CURRENT_STATUS.md`。
- P3-045 合同。
- P3-046/P3-047/P3-048 交付物及 PM Review。
- P3-047 PM-CE-06 Manifest、脚本、结构化失败结果。
- P3-050 任务卡、派发证明、独立 Review、PM Review、独立 Evidence、PM Evidence。
- 当前 P3-031 候选 SQL、合同测试与 P3-047 等价回归结构化结果（均只读）。

## 3. P3-050 独立性核验

| 项目 | 核验结果 |
|---|---|
| 全新会话 | PM 派发证明记录 `create_thread` 创建 `01a02001-a5f2-7681-a2b8-e42f44a08efd`，首轮仅隔离握手 |
| 计划先封存 | plan → plan hash → script → first results → seal 的文件时间顺序成立 |
| 延迟读取 | seal 声明 P3-049 详细攻击资产当时未读；任务卡允许此前只读 P3-049 PM Review |
| 程序独立 | 脚本仅 Python 标准库；无 P3-048/P3-049 runner/helper import/call |
| 首轮结果 | 832 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown |
| PM 复跑 | 同为 832/0/0/0/0；`.results` 逐项规范化 hash 与原结果完全一致 |
| 历史保护 | 40/40 expected hash 匹配；P3-047 原 0 PASS / 8 BYPASS 证据未覆盖 |

## 4. Hash 核对

| 文件 / 语义集合 | 当前 SHA-256 | Manifest / 计划期望 | 结果 |
|---|---|---|---|
| P3-050 independent attack plan | `3ac78f53bc50eea102d9ae40021b9beffa4c26ba5aa863ce5daae084fc1680dc` | 同值 | Match |
| plan hash file | `f0a47318ae321d062cf25c92d52ab8756807f452c5e0e0c0656fa8b9d94f4a70` | 同值 | Match |
| P3-050 independent script | `dbdb8855077aedfcc28d6e406f864a008948b16546653f8ef61115081fd9a42f` | 同值 | Match |
| P3-050 first result JSON | `38d10b07ddd1a4b3a9981352d4871edd172a06851a72273a7527c76937297405` | 同值 | Match |
| P3-050 environment | `115ccfb9a649db7b3e47273b100a9e5534f30a0457f49adf5950da8272510cca` | 同值 | Match |
| P3-050 first-run seal | `d5d3f1ce8772057da94d54c6944db3ffa728acea3d7ceadcc69ea19e0d21f31d` | 同值 | Match |
| P3-048 copied result | `fc698f8e46230038f5d9110db3b49e1e5971ca11750bea9fde1ca018a5787fb1` | 同值 | Match |
| P3-047 equivalent result | `85518c2b3a5fa8929b675910ba32756af96388ce08070c2cbce3700d21b29d1f` | 同值 | Match |
| original PM-CE-06 on candidate | `449b73c5000701fe1d770d460be86cad073f2d98a9f77bdffdd670303a5a6f2b` | 同值 | Match |
| PM rerun result JSON | `16372161d0992cc1aca6b09b73307e187f51bfd68b2b006cefeefaad4cfbc6ce` | 同值 | Match |
| PM P3-048 rerun log | `01729149ba61be7293aae67e6f2b898d78314898f2e47a5febae7222ef48c92e` | 同值 | Match |
| current candidate SQL | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` | P3-050 plan 同值 | Match |
| current P3-031 contract tests | `6729d48eeb9e523b5875165c053701602d6e10d5171fd27f235e680dcb34b3b5` | P3-050 plan 同值 | Match |
| current P3-031 validation shell | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` | P3-050 plan 同值 | Match |
| P3-047 original PM-CE-06 script | `54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50` | P3-047 Manifest 同值 | Match |
| P3-047 original 8 BYPASS result | `f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5` | P3-047 Manifest 同值 | Match |
| P3-050 original/PM `.results` 规范化集合 | `b22cee38a953ad4a15e370acc49b6d0bb5817f79437516c38f48717bf39f7f0e` | 两侧同值 | Semantic Match |
| P3-050 original/PM config checks 规范化集合 | `7aad636a1545df93fc023830df128f3d2a7f21fd91534f5348e76fe318a2ae21` | 两侧同值 | Semantic Match |

原/PM 结果完整 JSON hash 不同，差异来自 `schema` 绝对/相对路径及临时文件数据库路径；`schema_sha256`、832 条结果、状态统计和完整性检查一致，故不构成 Evidence 冲突。

## 5. 结构化统计核验

### P3-050 独立矩阵

| Family | PASS |
|---|---:|
| direction | 24 |
| field | 336 |
| null | 288 |
| status_time_combo | 48 |
| conflict | 40 |
| atomicity | 8 |
| transaction_boundary | 8 |
| legal | 32 |
| legal_noop | 48 |
| **Total** | **832** |

八配置各 104 条；824 条 P2、8 条 P3 transaction observation；所有 status 均为 PASS。四个 file 配置的 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

### 回归与条目映射

- P3-048：552 PASS；direction 24、field 336、status/time 48、replace 40、multirow 8、legal 72、time 16、原 PM-CE-06 8。
- P3-047 等价：297 PASS；其中 AC-12/13/17/18 各 8/8 PASS；PM-CE-01 8、PM-CE-02 8、PM-CE-03 16、PM-CE-04 8、PM-CE-05 33，均无 non-pass。
- P3-031：70 PASS（P0 18、P1 27、P2 25），退出码 0。
- 原 PM-CE-06 对当前候选：8 PASS / 0 BYPASS，退出码 0。
- P3-048 总复跑日志末尾：P3-048 552、P3-047 等价 297、`P3_031_EXIT 0`、`READ_ONLY_PRESERVED True`。

## 6. Evidence 结论与边界

- 未发现 hash、统计、任务结论、风险范围或独立性上的阻断冲突；未触发升级到 `max` 或 Blocked 条件。
- Evidence 支持在候选 SQL + 合成 SQLite + 当前 Evidence + 有限 Stage 3 边界内“建议关闭 R-0049”。
- Evidence 不支持关闭 R-0048、冻结任何资产、恢复工程基线、启用真实能力或进入下一阶段。
- 本 Manifest 不更新任何风险或项目状态；最终风险状态只能由 PM 在用户明确授权后更新。

## 7. Local Precheck

- 决策包预检：`lifeos/local_prechecks/LIFEOS-P3-051_LIFEOS-P3-051_r0049_risk_closure_decision_and_r0048_boundary_review_local_precheck.md`。
- 独立 Review 预检：`lifeos/local_prechecks/LIFEOS-P3-051_independent_review_local_precheck.md`。
- 两次预检状态均为 `Skipped / Local Model Unavailable`；错误为 `<urlopen error [Errno 1] Operation not permitted>`。脚本均按规则退出 0，允许跳过并继续人工评审。
- 本地模型输出仅作模板/措辞预检，不作为风险关闭、独立评审、冻结或阶段结论。
