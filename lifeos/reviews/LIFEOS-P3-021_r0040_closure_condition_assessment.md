# LIFEOS-P3-021｜R-0040 关闭条件评估

## 评审信息

- 对应任务 ID：LIFEOS-P3-021
- 评审类型：独立风险评估 / 决策输入
- 主责角色：Security Reviewer / Risk Owner
- 协审角色：Technical Architect / Data Trust Reviewer / QA Reviewer
- 评审关卡：Gate 2、Gate 3、Gate 4
- 评审路径：`lifeos/reviews/LIFEOS-P3-021_r0040_closure_condition_assessment.md`
- 评估结论：**B. 建议保持 Open / Conditional**
- 更新时间：2026-08-11

## 评估摘要

1. **[事实]** R-0040 的原始风险是实际 Tauri capability、IPC、路径 scope 或 Renderer 调用链绕过领域授权门，造成越权读写、Vault 写回、路径泄漏或导出越界。
2. **[事实]** P2-015 以等价 harness 42/42 PASS、P0=0 证明后端安全合同，但未验证真实 Tauri capability/plugin、invoke 注册、WebView/CSP、debug/release 包或平台路径行为。
3. **[事实]** P3-009～P3-020 证明了合成、单进程、受控测试包内的领域门禁与证据链；P3-020 为 34 PASS / 0 FAIL、63 条反例 63 PASS / 0 FAIL。该工程包没有 Renderer、真实 IPC、真实文件导出或真实 Vault。
4. **[判断]** 现有证据支持继续有限 Stage 3 受控工程，但没有覆盖 R-0040 的决定性攻击面，不能支持关闭。
5. **[建议]** 当前不拆分。受控后端结论已由 R-0042、P3-020 表达；拆分可能弱化剩余 P0 风险。

## 事实依据

- `RISK_LOG.md` 将 R-0040 记为 P0、`Open / Conditional`；关闭条件是目标 Tauri debug/release、目标平台和 P2-015 矩阵复测。
- P2-016 只冻结后端合同；P2-018 / 019 只准入合成数据、外部能力默认关闭的有限 Stage 3。真实 Tauri、Vault和导出扩权仍受能力门阻断。
- P3-020 已获 PM 接受和用户采纳为 `Pass with Conditions`，且明确不关闭 R-0040、不启用真实能力。

## 证据边界拆分

| 证据组 | 已覆盖 | 未覆盖 / 不可外推 |
|---|---|---|
| P2-015 | 后端授权/路径 gate、Vault 零写、受控导出；42/42 PASS | 真实 capability/plugin/invoke、Renderer/CSP、打包和 OS 路径 |
| P2-016 / 018 / 019 | 后端合同、H1-H9、T-IPC、能力门 | 不冻结或准入真实 Tauri、Vault、文件 scope、导出格式、SLA |
| P3-009～020 | 单进程消费门、证据链、不复活、P1 迁移、默认关闭 | 无 Renderer、真实 IPC/文件出口、Vault、发布包或跨平台集成 |

## 当前 Stage 3 安全边界核对

**[事实]** 当前仍未启用真实 Tauri / IPC，未连接真实 Vault，未处理真实数据，未执行真实文件导出或路径扩权，云 / 第三方模型、同步、多设备、L3 与外部用户均关闭。

**[失效条件]** 引入实际壳/Renderer，修改 capability/plugin/IPC/scope，访问真实路径/Vault，或改变平台/打包配置时，受影响能力须关闭直至复测放行。

## R-0040 原始风险覆盖判断

**[判断] 部分覆盖，但未覆盖原始风险。** 证据证明调用进入后端门时可 fail closed，却没有证明真实 Renderer 只能走这些入口，也未排除 capability/plugin/IPC/scope、CSP、打包或平台路径提供旁路。

P3-020 可证明受控范围内 P1 迁移完成，却不能作为关闭依据；该风险仍涉及数据主权、Vault 只读与导出边界，P0 优先级应保持。

## 关闭 / 保持 / 拆分选项评估

| 选项 | 评估 | 对后续 P3 的含义 |
|---|---|---|
| A. 建议关闭 | **不支持**；缺少真实集成证据 | 易误读为真实文件能力可启用 |
| B. 保持 Open / Conditional | **推荐**；与原始风险和证据一致 | 受控工程可继续，真实能力继续关闭 |
| C. 拆分 | 当前不建议；受控后端结论已由 R-0042/P3-020 表达 | 增加重复账本与“半项关闭”误读 |

若 PM 因审计粒度选择 C，备选为：`受控后端/领域门禁旁路风险`（受控包内已有覆盖）与 `真实 Tauri/IPC 集成旁路风险`（继承 R-0040 的 P0、Open / Conditional 和触发器）。拆分不得改变能力关闭状态。

## 推荐结论

**B. 保持 R-0040 为 Open / Conditional；当前不关闭、不拆分。** 允许继续 PM 任务卡授权的 P3 合成、单进程、受控测试包工程；不得将 P3-020 解释为真实 Tauri / IPC、Vault、文件导出、真实数据或生产能力许可。

## 适用范围与失效条件

本结论仅适用于无 Renderer/真实 IPC、无真实路径写入、Vault 或外部处理者的有限 Stage 3。首次真实 Tauri 集成，capability/plugin/IPC/scope/CSP 变化，debug/release、路径库或平台变化，启用 Vault/文件导出/真实数据，或发现绕门路径，均触发能力门。相关能力默认关闭；P0 失败不得条件豁免。

## 后续验证建议

进入真实 Tauri / IPC、真实 Vault 或真实文件能力前，最低应单列验证任务并形成可复跑 evidence：

1. 在真实 Tauri 集成、但仅使用合成临时目录/模拟 Vault的环境迁移 P2-015 全矩阵；不得先接入真实用户文件。
2. 验证 capability/plugin/invoke 白名单、未知命令默认拒绝；Renderer 无原始文件、数据库、shell、进程、网络或通用路径能力。
3. 端到端证明所有读、搜、建议、导出、恢复入口进入统一领域门并重检授权、精确版本、generation、tombstone/restriction、证据与租约；不存在旁路。
4. 在真实 OS 路径实现上攻击 traversal、绝对/编码/NUL、分隔符、symlink 与 scope 外 token；Vault 写/删/改名为 0，导出仅到确认目标且不静默覆盖或执行。
5. 验证 WebView/CSP、调试接口、日志与插件默认权限；debug/release、计划支持平台均为 P0=0。Vault 另测身份/对账、断源、清理、不复活；导出另测预览、冲突、部分失败与不复活。
6. 任务须经 PM 验收，建议非实现 Agent 只读反例复核；关闭风险或启用能力仍须用户确认。

## 角色检查点与关卡结论

- **Security Reviewer / Risk Owner：Pass with Conditions。** 原始攻击面仅被部分覆盖，保持 P0 Open / Conditional。
- **Technical Architect：Gate 4 受控工程层通过，真实集成层未通过。** 未越过“不冻结真实 Tauri 配置”的合同边界。
- **Data Trust Reviewer：Gate 2 在当前关闭态通过。** 身份与证据链在受控包内成立；Vault、导出、真实数据仍关闭。
- **QA Reviewer：Gate 3 在受控门禁层通过，真实 Renderer/IPC 权限链待 E2E 反例。** P3-020 不得外推。

## 风险

- 真实壳层可能新增绕门路径；受控 PASS 可能被误写为真实 Tauri 安全；拆分可能隐藏剩余 P0。

## 需要 PM / 用户决策

1. **[需 PM 确认]** 是否接受 B 结论并保持 R-0040 为 `Open / Conditional`。
2. **[需 PM 确认]** 是否不拆分，继续以单条风险和证据里程碑管理；如需更细审计，可采用上述 C 备选但不改变剩余状态。
3. **[需 PM / 用户确认]** 未来真实 Tauri 验证任务、R-0040 关闭及真实 Tauri / IPC、Vault、文件导出或真实数据启用。

## 最终建议

保持 `R-0040 = Open / Conditional`，不关闭、不拆分；继续允许受控 P3 工程，真实能力继续关闭。待真实 Tauri debug/release、目标平台与 P2-015 端到端矩阵全部 P0=0，并完成 PM 验收、建议的独立反例复核及用户确认后，再评估关闭。

## 范围与变更声明

本任务仅创建本报告；未修改代码、测试、evidence、Stitch、项目账本或冻结状态，未关闭风险、恢复/冻结工程基线扩展或启用真实能力。
