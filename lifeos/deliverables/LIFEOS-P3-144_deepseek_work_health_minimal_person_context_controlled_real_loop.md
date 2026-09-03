# LIFEOS-P3-144 · DeepSeek Work／Health 最小个人上下文受控真实闭环

## 任务信息

- 任务 ID：LIFEOS-P3-144
- 任务名称：DeepSeek Work／Health 最小个人上下文受控循环
- 执行 Agent：Codex
- 当前状态：Accepted / Complete / PM Pass / Independent Pass / User Adopted / Not Product Frozen
- 需要 PM 决策：No
- 任务类型：工程实现、L3/Gate Evidence Closure
- 风险等级：L3/Gate
- Task Contract：[LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md](../tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md)
- L3/Gate ABF：ABF-P3-144-v1，[acceptance basis](../tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop_acceptance_basis_freeze.md)
- 启动前合同歧义：No

## 终局收口摘要（2026-09-03）

- Phase A 合成／离线工程 Gate、Phase B 全新隔离独立评审、Phase C 用户操作真实 Gate、Closure-3 profile delta 和 Closure-4 独立增量复核均已完成。
- 用户在 actual Tauri App 内完成受控真实操作；一次确认后的最小上下文只发送至 DeepSeek 精确 authority。真实正文、凭据和正文 hash 未进入 Evidence、日志、截图或聊天。
- Closure-4 关闭真实使用暴露的超时误分类、回答／反馈状态不可见、数据库文件名偏离合同和反馈重复消费问题。
- 活动数据库已按用户明确授权无损收口为 Pilot-7 根内 `capture.sqlite`，普通文件 `0600`；原零字节占位文件改名保全。Pilot-7、DB 与加密凭据均保留。
- 最终 PM 计数：P0=0、P1=0、P2=3、Unknown=0、Not Implemented=0。三个 P2 均为已修复或已排除的可分离历史事实，不阻断唯一用户结果。
- PM 结论为 Pass，用户已于 D-0647 完成 L3 最终采纳并授权推送当前任务分支。R-0055／R-0056保持Open，产品Not Frozen，Stage 4 Not Ready。

## 执行摘要

### 事实

- 已在 `lifeos/engineering/LIFEOS-P3-144/candidate/` 实现受限 Work 与非医疗 Health/Fitness Current State：每域最多 3 条、每条最多 200 字符，Health 医疗语义写前拒绝。
- Context Resolver 只从当前 Domain 的相关、有效、授权条目组装披露；披露预览明确显示条目、DeepSeek 精确 authority、模型、处理位置和 `3 / 480 / 120` 预算。移除、重启、过期式失效、撤回、纠正与重复确认均失败关闭。
- Understandings 以独立类型保存来源引用、Provider 和 model；用户可确认、编辑、拒绝、忽略、纠正。纠正／撤回来源会使相关 Understanding 标记为 `invalidated`，不改写历史。
- Phase A `run_mode()` 硬固定为 `synthetic`；Renderer 没有直接网络 API，DeepSeek 真实 adapter 在本 Gate 不可达。Cloud 8／Local 4、恰好 20 个既有 IPC 名称及 P3-143 Settings shell 均保留。
- 锁定离线定向 Rust 测试、前端离线合同、静态合同、marker 反例矩阵和最终 Tauri bundle 均通过。最终 bundle 以直接启动且仍存活的 PID 完成 Desktop／Compact／Narrow 的 `PID → exact AXWindow → AXWebArea → target-only screenshot` Evidence。
- Phase A 仅使用固定非敏感合成夹具。未访问或探测 Pilot-7、其 DB、真实个人内容、真实 DeepSeek、真实凭据或其他 Provider。
- 工程临时根 `/private/tmp/lifeos-p3-144-engineering-v1` 已在 marker 复核后精确清除；本轮创建的合成 Keychain 项已删除。

### 推断

- 工程 Gate、独立评审、真实用户 Gate 与 PM 验收共同支持本任务 Pass；该结论不外推为风险关闭、产品冻结或 Stage 切换。

### 建议

- P3-144资产转历史只读；保留Pilot-7、DB和加密凭据，等待用户决定下一结果级任务。

## 角色与关卡

- 主责角色：工程实现 / Technical Owner
- 协审角色：独立评审、安全与数据治理
- 已覆盖：Phase A synthetic/offline engineering、结构化正负路径、动态 actual-Tauri、Manifest、Phase B/Closure-4独立评审、Phase C真实用户操作、PM验收与用户最终采纳。
- 已触发独立评审：Yes；原因是 L3/Gate真实数据、凭据和第三方网络边界。
- 未通过或未执行的关卡：无（本 Task Contract 内）。

## Evidence 与交付物

- 工程目录：[LIFEOS-P3-144](../engineering/LIFEOS-P3-144)
- Phase A 验证：[phase_a_offline_validation.json](../engineering/LIFEOS-P3-144/evidence/phase_a_offline_validation.json)
- AC 矩阵：[phase_a_ac_matrix.json](../engineering/LIFEOS-P3-144/evidence/phase_a_ac_matrix.json)
- 原生窗口 Evidence：[native_window_evidence.json](../engineering/LIFEOS-P3-144/evidence/native_window_evidence.json)
- Checkpoint：[checkpoint.json](../engineering/LIFEOS-P3-144/evidence/checkpoint.json)
- 清理收据：[cleanup_receipt.json](../engineering/LIFEOS-P3-144/evidence/cleanup_receipt.json)
- Final Manifest：[FINAL_MANIFEST.json](../engineering/LIFEOS-P3-144/FINAL_MANIFEST.json)
- Manifest 验证：[manifest_verification.json](../engineering/LIFEOS-P3-144/evidence/manifest_verification.json)（127 entries，0 errors，PASS）

## 终局治理状态

- Phase B 独立评审、Phase C 用户真实 Gate、Closure-4 独立增量复核、PM Pass与用户采纳均已完成。
- 当前任务转历史只读；本次授权仅覆盖任务分支推送，不包含 main 合并、风险关闭、产品冻结、Stage切换、资产清理或后继任务创建。

## 后续任务建议

- 不自动创建后继任务；等待用户基于当前路线选择下一结果级任务。

## 阻塞或异常

- 无工程阻塞。
- 历史保全：一次继承的完整测试集会创建不属于固定工程根的任务前缀 fixture root，已从正 Evidence 排除；后续只运行 P3-144 定向测试。一次显示名 bundle 启动及一次后台 PID 尝试均未满足“启动返回且仍存活 PID”的要求，已排除；最终 PID Evidence 均使用持久终端 `exec` 的 live PID。
