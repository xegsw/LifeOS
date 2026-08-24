# LIFEOS-P3-105｜三张冻结 Stitch 页面高保真 Tauri UI 整合能力包

## 任务信息

- 任务 ID：`LIFEOS-P3-105`
- 执行 Agent：Codex，新建隔离工程会话
- 任务类型：P0 受控高保真 UI／真实 Tauri 整合能力包
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-105_three_frozen_stitch_pages_high_fidelity_tauri_ui_integration_acceptance_basis_freeze.md`
- ABF ID／SHA-256：`ABF-P3-105-v1` / `3db798ab392c663ca4099491ed10ef8f70429542ef7b43809c97fb0774be6a4c`
- 当前状态：`Blocked / Not Submitted as Pass`
- 正式 Rework：`0/2`；本次为执行前置条件冲突，不计 PM 正式 Rework。
- 授权证据：用户于 2026-08-23 将任务卡绝对路径投递至本新建 Codex 工程会话；该投递仅授权 Frozen ABF 范围。

## 执行摘要

1. **[事实]** 启动前已完整核对 ABF、三张 1280×1024 权威参考图和九项 P3-104 固定输入；全部路径与 SHA-256 匹配。
2. **[事实]** 已复制 P3-104 到新建 `lifeos/engineering/LIFEOS-P3-105/`，只修改授权的三张 HTML、`app.js`、`styles.css` 及 `tauri.conf.json` 的窗口标题／初始／最小尺寸字段，并新增 task-local 测试与阻断前 Evidence。
3. **[事实]** 首轮实现包含全高白色左侧导航轨、蓝灰主画布、默认恢复双栏卡、无建议空态与三列痕迹、离线／权限双警示、受限恢复卡、今日安排、固定底部 composer、skip link、可见焦点、窄屏和 reduced-motion。附件／语音为 disabled；Project、AI、来源及其他未实现动作会明确披露“未启用”。参考截图未作为图片、背景、蒙层或主体资产；没有远程资源。
4. **[事实]** 阻断前自检为静态 35/35 PASS、源级视觉合同 34/34 PASS、Rust unit 7/7 PASS，task-local 工程内离线 locked debug `.app` bundle 成功。`Cargo.lock`、`src/runtime.rs`、`src/main.rs`、`capabilities/main.json` 和直接依赖保持冻结输入不变。
5. **[事实]** 在启动实际 app replay 前发现 Frozen 边界矛盾：不可变 `runtime.rs` 只接受直接位于 `/private/tmp/lifeos-p3-104-*` 的数据库父目录；本任务 ABF 只授权新建／清理 `/private/tmp/lifeos-p3-105-*`。前者会越出本任务写入授权，后者会被 runtime 在启动前拒绝。
6. **[判断]** 该矛盾无法在当前 ABF 内安全绕过。修改 runtime、使用目录链接或创建 P3-104 前缀夹具分别违反 ABF-I-06、ABF-I-09、L1-1/L1-9 与明确允许写入目录。按停止条件，本会话未启动实际 app、未创建越权夹具、未生成虚假动态 PASS。

## 修改范围

- UI：`ui/default-recovery.html`、`ui/no-reliable-suggestion.html`、`ui/restricted-offline.html`、`ui/app.js`、`ui/styles.css`
- 窗口字段：`tauri.conf.json` 的 `title`、`width`、`height`、`minWidth`、`minHeight`
- 测试／Evidence：`tests/visual_contract.json`、`tests/static_checks.py`、`tests/verify_visual_contract.py`、`evidence/`
- 未修改：P3-104 全目录及历史资产；P3-105 的 `Cargo.lock`、`Cargo.toml`、Rust runtime/main、capability 与直接依赖。

## 自检与 Evidence

- 复跑命令：`python3 tests/static_checks.py`；`python3 tests/verify_visual_contract.py`；`CARGO_NET_OFFLINE=true ... cargo test --locked`
- 静态检查：35 PASS / 0 FAIL
- 源级视觉合同：34 PASS / 0 FAIL
- Rust unit：7 PASS / 0 FAIL
- 离线 locked bundle：PASS（task-local engineering target）；实际 app clean replay 未启动
- 结构化矩阵：`lifeos/engineering/LIFEOS-P3-105/evidence/structured_results.json`
- 阻断说明：`lifeos/engineering/LIFEOS-P3-105/evidence/blocker_report.json`
- 当前计数：P0=0、P1=0、P2=0、Unknown=0、Not Implemented=15
- `/private/tmp/lifeos-p3-105-*` 残留：0；未创建任何 P3-105 动态夹具。

## 角色与关卡

- 主责产品体验／前端 UI 工程：阻断前代码实现和源级视觉合同完成；实际 app 视觉验证未完成。
- 技术架构：冻结 runtime／依赖／capability 未漂移；发现路径合同与本任务授权冲突。
- 数据／领域与 AI 信任：固定演示、用户原文、系统状态、AI／来源关闭态已在代码中区分；未通过实际 app 证明。
- 可访问性：代码具备 skip link、焦点、Tab/Enter 原生控件、窄屏和 reduced-motion；动态 Evidence 未完成。
- Gate 1：源级预检通过，最终待 PM；Gate 2/3/4：Blocked，不能据静态结果宣告通过；Gate 5：仅固定非敏感内部理解检查，未执行。

## PM 待确认

**[建议｜需 PM 确认]** 当前 ABF 的路径授权与不可变 runtime 合同存在不可满足的冻结冲突。执行会话不能修改 ABF。请 PM 按两层验收治理判断关闭／Supersede 当前任务并创建新任务／新 ABF，或以其他合规方式重建一致的 runtime 与夹具路径边界；在新授权前不得继续实际 app Evidence。

## 非范围保持

未访问 retained pilot、真实个人数据、真实用户 DB／路径、网络、云、第三方、Vault、导出、同步、多设备、L3 或外部用户；未修改账本、风险或冻结状态；未创建最终独立复评，未进入 Stage 4。
