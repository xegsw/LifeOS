# LIFEOS-P3-141 Revision 3｜CL-MODE-DELETE-01 工程 Closure 报告

## 任务信息

- 任务 ID：LIFEOS-P3-141 / CL-MODE-DELETE-01
- 任务名称：模式显示与删除凭据一致性窄 Closure Cycle
- 执行 Agent：Codex
- 当前状态：Completed（仅工程 Closure Cycle）
- 需要 PM 决策：Yes
- 任务类型：L3 工程修正、回归、actual-Tauri Evidence 与精确清理
- 风险等级：L3
- Task Contract 路径／章节：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_3.md`；PM Review 的 CL-MODE-DELETE-01
- L3/Gate ABF 路径／版本：`lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_acceptance_basis_freeze_revision_3.md` / ABF-P3-141-v3
- 是否在启动前发现合同歧义：No
- 当前状态：Closure Cycle 已完成工程侧工作；Phase C 仍 Paused
- 交付物篇幅是否在建议范围内：Yes

## 执行摘要

- 事实：设置页把未保存的 Cloud／Local 切换表示为 `draftProvider`，而活动 backend 继续只使用已持久化的 `runtime.provider`。
- 事实：显示模式与活动模式不一致时，凭据输入、保存、测试、模型选择、启用与删除均不可达；页面明确提示“当前显示为 Cloud，但活动模式仍是 Local”。保存当前配置后才恢复对应模式的凭据操作。
- 事实：新增 `mode_delete_ui_contract.mjs` 覆盖“已保存 Local → 视觉切 Cloud → 直接删除不发凭据 IPC → 保存 Cloud 后删除可用”，并通过。
- 事实：发现默认并行测试会让 test-only 的全局授权撤销标志被无关 fixture 消费；已限制为唯一 race request id。默认 `cargo test --locked --offline` 现为 51/51 通过。
- 事实：使用唯一合成根的占位凭据完成实际 App 正常删除；删除后 SQLite `encrypted_provider_credentials` 行数为 0，新的直接 PID 重启后仍无凭据。
- 事实：桌面、1160×768、700×760 三档均以新的直接 PID 取得精确标题 AXWindow 与 AXWebArea 证据；最终 marker-gated 清理确认唯一临时根不存在。
- 推断：P2-001 所描述的“可见删除但 backend 按旧模式拒绝”路径已在工程候选中关闭。
- 建议：由全新隔离会话从阶段 0 发起强制独立复评；本报告不替代该结论。

## 角色与关卡

- 主责角色：工程执行（Codex）
- 协审角色：无；本会话未执行独立评审
- Evidence 等级与已覆盖关卡：L3 工程侧源码、正负回归、错误 marker／0700 反例、实际直接 PID 原生 AX、合成凭据生命周期、非自指 Manifest、marker 精确清理
- 是否触发独立评审及理由：Yes；L3 且涉及凭据生命周期。依任务卡必须由另一个全新隔离会话执行，当前未触发实际评审。
- 仍需 PM/后续任务确认的关卡：独立复评、PM re-review；Phase C、真实 Provider／凭据、Pilot-6、风险关闭、产品冻结与 Stage 状态均未改变。

## 会话与上下文

- 本任务执行方式：New Session
- 执行授权证据：任务卡路径投递；PM 对唯一合成占位凭据删除与 marker 精确清理的明确确认。
- 若复用会话，上一任务是否已结束：N/A
- 是否发现旧任务授权或范围被错误继承：No
- 已重新读取的关键文件：根 `AGENTS.md`、`lifeos/CURRENT_STATUS.md`、Revision 3 任务卡、ABF v3、模型设置基线、PM Review、P2-001、会话回复模板。
- 复用既有读取结果的稳定文件：无。
- 是否发生工具输出截断或补读：Yes；启动阶段的状态文件输出截断后已按段补读；不影响本任务结论。

## Agent 自评提示

- 本任务是否适合当前 Agent：High
- 如果不适合，建议后续交给：WorkBuddy / Other
- 原因：工程实现、离线构建、actual-Tauri PID/AX Evidence 与合成根清理已完成；独立性要求使后续评审不应由本会话承担。

## 交付物

- 完整交付物路径：
  - `lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/MODE_DELETE_CLOSURE_FINAL_MANIFEST.json`
  - `lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/evidence/mode-delete-closure-v1/manifest-verification.json`
  - `lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate/`
  - 本报告
- 文件状态：Created / Updated

## 需要 PM 决策

1. 是否派发一个全新隔离会话，对固定候选及本 Closure Evidence 做从阶段 0 开始的强制独立复评。
2. 工程范围内的最终计数为 P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0；请勿将其外推为独立评审、Phase C 或风险关闭结论。

## 后续任务建议

- 仅在 PM 创建并派发后进行：全新隔离的 L3 独立复评与 PM re-review。

## 阻塞或异常

- 无工程阻塞。
- 已保留的历史性执行异常：共享运行时污染、非 0700 根、错误 marker 与并行 test-only fixture race；前 3 项均由守卫拒绝／隔离，最后一项已作 test-only 定向修正并由默认并行 51/51 复跑验证。
