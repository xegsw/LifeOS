# LIFEOS-P3-079｜本地 MVP 整合受控能力包交付物

## 1. 任务与授权

- 任务卡：`lifeos/tasks/LIFEOS-P3-079_local_mvp_integrated_controlled_capability_package.md`
- 执行授权证据：用户于 2026-08-21 17:15 CST 在新隔离 Codex 工程会话投递上述任务卡路径。
- 实际配置：Codex；本会话未降级模型（任务卡推荐 `gpt-5.6-terra` + `high`）。
- 写入范围：仅新建 `lifeos/engineering/LIFEOS-P3-079/`、本交付物及本地预检输出。

## 2. 交付事实

已建立单一、可操作的合成闭环：`scripts/operator_cli.py` 接受操作者提供的非敏感测试文本、幂等键和明确确认，向调用方指定的 task-local SQLite 保存；随后可查看来源与状态、预览精确权限、设置 grant/deny/撤回、预览并确认恢复，并持续记录审计。

核心实现为 `src/integrated_runtime.py`。唯一允许结果是 `allowed_local_synthetic`；实现明确静态关闭网络、云、AI 消费、文件导出、Tauri/IPC、Vault、真实路径、同步、多设备、L3 与外部用户通道，且不触发外部动作。

P3-063、P3-067、P3-075、P3-077 仅作为只读语义和反例输入，未被改写，亦未调用其 runner 充当本包主证据。其当前 hash 见 `evidence/historical_input_hashes.json`。

## 3. 包内自检结论

**通过。** 在脚本创建的干净系统临时副本中完成以下可复跑验证：

- 16/16 单元与端到端测试 PASS，退出码 0。
- CLI 完成首次 `CONFIRM` 保存 → grant → 恢复预览 → 确认恢复，全部 PASS。
- 重复保存、重复恢复、权限撤回、阻断审计、重启后审计与撤回状态均有测试覆盖。
- 原子失败注入不留下 record；未确认、错误确认、默认拒绝、deny 优先、过期 grant、绑定不匹配及撤回内容均 fail-closed。
- 结构化结果、日志、CLI 链、快照、源 hash 和 Manifest 已保留；验收矩阵见 `evidence/acceptance_matrix.md`。
- 静态检查未发现网络/云相关导入或 URL、Tauri invoke 调用；边界状态另见 `evidence/self_check_results.json`。

复跑命令：

```bash
python3 lifeos/engineering/LIFEOS-P3-079/scripts/run_self_check.py
python3 lifeos/engineering/LIFEOS-P3-079/scripts/make_manifest.py
```

额外不落盘语法编译通过。一次 `py_compile` 尝试因 macOS Python 缓存目录无写权限失败；它未写入本项目，且已由 `python3 -B` 的不落盘语法编译替代，不影响上述测试结果。

本地预检已按项目规则调用，但局域网模型在当前受限环境不可访问；预检报告为 `lifeos/local_prechecks/LIFEOS-P3-079_LIFEOS-P3-079_local_mvp_integrated_controlled_capability_package_local_precheck.md`，状态 `Skipped / Local Model Unavailable`，未作为任何验收结论。

## 4. 验收矩阵与 Evidence

主 Evidence：`lifeos/engineering/LIFEOS-P3-079/evidence/MANIFEST.md`。

| 任务卡标准 | 覆盖状态 | 主 Evidence |
|---|---|---|
| 明确确认保存、失败不得称已保存 | PASS | `self_check_results.json`、`self_check.log` |
| 来源/状态/权限预览与仅本地允许结果 | PASS | `operator_cli_chain.json`、`operator_snapshot.json` |
| 默认拒绝、精确 grant、deny 优先与 fail-closed | PASS | `self_check_results.json` |
| 审计、撤回与重启可追溯 | PASS | `self_check_results.json`、`operator_snapshot.json` |
| 原子失败、恢复确认、撤回阻断、幂等冲突 | PASS | `self_check_results.json` |
| 临时副本、runner、结果/日志/快照/hash/Manifest | PASS | `run_self_check.py`、`MANIFEST.md` |
| 历史只读与禁止能力静态关闭 | PASS | `historical_input_hashes.json`、`self_check_results.json` |

## 5. 风险与边界

事实：本任务未接触真实个人数据、真实用户 DB/路径/文件、Vault、Tauri/IPC、网络、云/第三方、AI 消费、导出、同步、多设备、L3 或外部用户；未关闭/重开风险，未恢复工程基线，未冻结 Schema/API 或任何资产，也未进入 Stage 4。

推断：在本任务限定的合成、单进程、task-local SQLite 边界内，闭环的授权、撤回、恢复和失败披露行为由当前 Evidence 支持。

建议：交由 PM 进行一次验收，再交由**全新隔离会话**进行独立安全/体验复评。即使通过，资产仍为 Not Frozen，且不自动启用任何真实能力或进入 Stage 4。

## 6. 问题计数与未覆盖项

- P0：0
- P1：0
- P2：0
- Unknown：0
- Not Implemented：0（在任务卡所定义的合成受控范围内）
- 未覆盖项：真实能力演练；这是任务卡明确禁止的范围，并由静态关闭态替代验证。

## 7. 角色与关卡

- 主责角色：Codex 工程执行。
- 协审角色：后续独立安全／体验复评 Agent。
- 已通过关卡：任务卡授权核对、范围/历史只读核对、包内端到端自检、静态关闭态核对、Evidence 完整性核对。
- 尚未通过的关卡：PM 验收、全新隔离独立安全／体验复评、用户采纳。以上均需 PM/用户流程，不能由本执行会话替代。

## 8. 需 PM 确认

无产品、范围、架构、数据模型或 AI 权限边界变更建议。本包仅请求按既定流程进行 PM 验收与后续独立复评路由。

---

## 9. D-0328 窄 Rework（2026-08-21）

### 整改事实

PM 发现的 P1 是：撤回幂等键只按键匹配，可能在指向不同 permission ID 时仍误报成功。现已将撤回回执绑定为完整请求语义：`permission_id`、`REVOKE` 确认值、操作类型 `permission_revoke` 与幂等键。相同键仅在全部语义一致时返回 `idempotent_repeat`；同键、不同 permission ID 返回可见 `idempotency_conflict`，不撤回目标权限，且不报告成功。

CLI 新增 `revoke-permission --permission-id … --key … --confirmation REVOKE`，用于操作者可复查演练。

### Rework 自检与 Evidence

**通过。** 新 runner 在干净系统临时副本运行完整 20 项测试：原 16 项保持 PASS，新增 4 项覆盖同键同权限重复、同键异权限冲突、重启后重放和审计回执语义一致性。CLI 演练确认两条不同权限先后 grant；第一条撤回成功、同请求重放返回 `idempotent_repeat`、第二条复用相同键返回 `idempotency_conflict` 与 `ok: false`。

新 Evidence **仅**写入 `lifeos/engineering/LIFEOS-P3-079/evidence/rework/`；父目录 `evidence/` 保持只读历史。新结果、日志、快照、旧 Evidence hash、当前源 hash 与 Manifest 分别见：

- `evidence/rework/self_check_results.json`
- `evidence/rework/self_check.log`
- `evidence/rework/revoke_cli_chain.json`
- `evidence/rework/revoke_snapshot.json`
- `evidence/rework/historical_base_evidence_hashes.json`
- `evidence/rework/MANIFEST.md`

复跑命令：

```bash
python3 lifeos/engineering/LIFEOS-P3-079/scripts/run_rework_self_check.py
python3 lifeos/engineering/LIFEOS-P3-079/scripts/make_rework_manifest.py
```

### Rework 问题计数与关卡

- P0：0
- P1：0（D-0327 撤回幂等键 P1 已由 4 项针对性测试覆盖）
- P2：0（父 `evidence/` 未被 Rework runner 或 Manifest 重写）
- Unknown：0；Not Implemented：0（任务卡所定义的受控范围内）

事实：未扩大真实能力或任何禁止边界；静态关闭态再次检查 PASS。不变：仍需 PM 重新验收与全新隔离独立安全／体验复评，资产继续 Not Frozen。
