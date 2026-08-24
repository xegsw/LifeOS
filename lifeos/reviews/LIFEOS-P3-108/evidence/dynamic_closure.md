# P3-108 实际 Tauri 动态闭环

## 运行边界

- 被测 app：固定 P3-106 候选的本地 Tauri debug app；所有正常交互使用 `/private/tmp/lifeos-p3-104-p3-108-review-nominal-p3108a1/capture.sqlite`，仅含固定非敏感文本。
- 可复跑入口：`LIFEOS_P3_104_DB_PATH=<fixture>/capture.sqlite <clean-work>/target/debug/lifeos-p3-104`；GUI 观察使用同一候选的已构建 macOS app 和同一环境变量。
- 不能把本表的旧静态材料或提交 Evidence 当作动态证据。每一行均只记录本会话实际操作。
- `tauri://localhost/` 是 Tauri 内建本地协议，不是 HTTP 网络请求；静态 CSP/代码扫描已在 `static-results.json` 记录为无 remote endpoint。

## 已成立的实际动作

| ID | 前置与操作 | 可观察结果 | 结构化结果 | Evidence（SHA-256） | 状态 |
|---|---|---|---|---|---|
| P3108-D01 | nominal app 首启 default | 原文/系统/AI/来源身份清晰；关闭态可见 | `P3108-M007-visual` | `dynamic/P3108-D01-default.jpeg` (`f770e31d3890fdaae33246a6e597c06e6c261fb6cbe3c1e10ed1bf1fbee7b487`) | PASS（基线实际渲染；非 1280×1024） |
| P3108-D02 | 点击“暂无可靠建议” | 页面显示“暂无可靠建议”，不伪造 Project 或 AI 结论 | `P3108-M007-visual` | `dynamic/P3108-D02-no-suggestion.jpeg` (`de3272279b8d67158391e86d95ee62bf6be1bd4e0b461a1572795e3ae5f32faf`) | PASS（基线实际渲染；非 1280×1024） |
| P3108-D03 | 点击“权限受限与离线” | 网络/外部来源/AI 均关闭，本地 backend 可查 | `P3108-M007-visual` | `dynamic/P3108-D03-restricted.jpeg` (`b6d5c85ef75d5d061fada7191f664cd072813725670a3e3704b5fb0d50813dc1`) | PASS（基线实际渲染；非 1280×1024） |
| P3108-D04 | nominal 空 SQLite 点击固定捕获 | UI 显示 SQLite 原子发布完成；随后 DB 为 1 capture/1 audit | `P3108-M009-first-capture` | `dynamic/P3108-D04-first-capture.jpeg` (`f2e111fb9746ed70fe11c316f38dce92b3e44f90cfe61b2431914efffe7a0765`)；见下方 DB transcript | PASS |
| P3108-D05 | 再次点击相同 capture | UI 显示幂等重复；DB 仍 1 capture，audit 为 saved+repeat 共 2 | `P3108-M010-repeat` | `dynamic/P3108-D05-repeat.jpeg` (`469edf94849506b1bcb6f452aa8fdf2be56c8c865cb6c4a93cf82fb5786a3744`)；见下方 DB transcript | PASS |
| P3108-D06 | 点击 conflict capture | UI 明示 `idempotency_conflict`；DB/audit 数量未增加 | `P3108-M010-conflict` | `dynamic/P3108-D06-conflict.jpeg` (`fc190abb2df62b32e6c9d068963fc462562bb10a0e2fe99f7125f6edda4da323`) | PASS |
| P3108-D07 | 点击 injected atomic failure | UI 明示 `injected_atomic_failure`；DB/audit 数量未增加 | `P3108-M010-failure` | `dynamic/P3108-D07-failure.jpeg` (`b1a8afa367cf3d85b8352160488c47bc2848cdcffa4567321e0da479a787ef46`) | PASS |
| P3108-D08 | 在 restricted 页面按 `super+r` | 刷新后仍显示“已由本地 backend 耐久恢复”及 1 条本地记录 | `P3108-M011-refresh` | `dynamic/P3108-D08-refresh.jpeg` (`fd703de87127410ae604d0d9691a5e1164aaa3c09c98737230e3d23992191191`) | PASS |
| P3108-D09 | 依次实际导航 default → no-suggestion → restricted | 三次 AX URL 分别为 `tauri://localhost/default-recovery.html`、`tauri://localhost/no-reliable-suggestion.html`、`tauri://localhost/restricted-offline.html`；回到 restricted 仍耐久恢复 | `P3108-M011-nav` | AX transcript：本文件；三态实际截图 D01–D03 | PASS |
| P3108-D10 | 关闭 app，再以同一 nominal DB 重开 | 重开 default 显示“已由本地 backend 耐久恢复”及“本地记录 1 条” | `P3108-M011-reopen` | `dynamic/P3108-D10-reopen.jpeg` (`172549bffda6a6f9084f3efc6f3862664d34ca45b47c498d830f41b2f92404b1`) | PASS |
| P3108-D11 | 点击 disabled “附件未启用” | 控件仍 disabled、语音也 disabled，backend 仍耐久恢复；无 IPC/写入迹象 | `P3108-M012-unimplemented` | AX transcript：本文件 | PASS |
| P3108-D12 | 打开本地验证后点击 unknown IPC | UI 明示 unknown invoke handler 拒绝且零副作用 | `P3108-M012-unknown` | `dynamic/P3108-D12-unknown-ipc.jpeg` (`5e5003769bbbeee6f10824a48e6cb25f760adcf00f78d6202a68ae0f204190f4`) | PASS |
| P3108-D13 | 本地验证触发 extra path/SQL/shell fields | UI 明示全部拒绝，记录与审计不变 | `P3108-M012-extra-fields` | `dynamic/P3108-D13-extra-fields.jpeg` (`7055260a47f0426a1ba9c6367abcc6a246fab0f4fa61d4c4eda91280124933f9`) | PASS |
| P3108-D16 | 实际拖动 app 窗口至窄窗口后复查 default | 捕获动作仍在 AX tree 中可达，截图实际尺寸为 768×832 | `P3108-M008-narrow` | `dynamic/P3108-D16-700x760.jpeg` (`a08fccd597949c90e24b17ba84ab66b87cce3d862363b3f1f6fa38b8f247a348`) | PARTIAL：不能证明冻结的精确 700×760 |
| P3108-D17 | 在 restricted 页面按 Tab | 真实键盘动作后获取窗口截图和 AX tree；skip link 存在 | `P3108-M015-tab` | `dynamic/P3108-D17-tab-focus.jpeg` (`da3e731a417cf25ac7d474897e590fb0eac11df8bf8cda10a3ed68fdb98b4423`) | PARTIAL：AX 不报告焦点环的顺序 |
| P3108-D18 | 紧接按 Return 激活 | 焦点进入 HTML content，页面主内容仍可操作 | `P3108-M015-enter` | `dynamic/P3108-D18-enter-skip.jpeg` (`7dac58f69a37ad5390342063b21aa2f79966a818536df82ddd0fc4ca97ad041e`) | PARTIAL：无法以 AX 证明焦点落点就是 main |
| P3108-D20-content | 以内容篡改 SQLite 夹具启动实际 GUI | UI 明示“backend 拒绝读取；未展示缓存或部分记录”“启动读取失败”；记录数 0 | `P3108-M014-content-tamper` | `dynamic/P3108-D20-content-tamper.jpeg` (`1265528e6eae4060178f92d9fce17c6d561ee0f3a946323313ab32cd1344dc1b`) | PASS |
| P3108-D20-schema | 在同一非敏感 fixture 删除 `audit` 表后重开实际 GUI | 与内容篡改同样明示拒绝且无缓存成功态 | `P3108-M014-schema-tamper` | AX transcript：本文件 | PASS |

## 启动前 fail-closed 实际进程矩阵

干净副本生成的 Tauri debug binary 在以下夹具上均退出 101，且在启动边界输出相应 `controlled DB boundary rejected`，没有打开正常 UI 或写入夹具：

| fixture | 动作 | 观察到的 code | 结果 |
|---|---|---|---|
| path | `capture.sqlite` 是目录 | `database_type_rejected` | PASS |
| link | `capture.sqlite` 是 dangling symlink | `database_type_rejected` | PASS |
| hardlink | `capture.sqlite` nlink=2 | `database_type_rejected` | PASS |
| dangling-final | 最终 DB 为 dangling symlink | `database_type_rejected` | PASS |
| dangling-journal | 有 dangling `-journal` | `database_sidecar_rejected` | PASS |
| dangling-wal | 有 dangling `-wal` | `database_sidecar_rejected` | PASS |
| dangling-shm | 有 dangling `-shm` | `database_sidecar_rejected` | PASS |

这些退出结果来自本会话运行 `<clean-work>/target/debug/lifeos-p3-104` 的 stdout/stderr；绝不以提交 unit test 代替。

## nominal DB / audit 只读 transcript

在 D04–D07 后，readonly SQLite 查询得到：`capture_count=1`，`audit_count=2`。唯一 record 的 `content` 是任务固定非敏感文本、`source=local_capture`、`idem_key=p3-104-ui-primary`；audit 依次为 `capture_saved/local_capture` 与 `capture_repeat/same_idempotency_key`。nominal app log 还依次记录 `saved record_count=1`、`idempotent_repeat record_count=1`、blocked `idempotency_conflict`、blocked `injected_atomic_failure`。

## 未完成动作及其阻断理由

| ID | 状态 | 事实与影响 |
|---|---|---|
| P3108-D14 | NOT IMPLEMENTED | 当前可用实际窗口截图为 1036×779 基线；任务禁止改系统显示，无法取得冻结要求的 1280×1024 三态逐页比较。 |
| P3108-D15 | PARTIAL | 基线实际三态已取得（D01–D03），但无法证明题卡要求的“原工作区”精确视口和滚动闭环。 |
| P3108-D16 | NOT IMPLEMENTED | 已实际缩窄窗口，但所得截图为 768×832，不能诚实声称等于冻结的 700×760。 |
| P3108-D19 | NOT IMPLEMENTED | 当前运行时报告“系统未请求 reduced motion”；任务禁止修改系统显示/偏好，未取得用户对该系统设置变更的明确授权。 |
| P3108-D20 其余类型 | PARTIAL | 已完成 path/link/hardlink 与四个 dangling 类型及 content/schema tamper；未单独建立并运行“外部路径”夹具，因为固定路径 schema 在启动前已拒绝，但缺少独立 actual-app Evidence 行。 |

因此本闭环不能支撑 Pass；未完成/部分项必须被最终 verifier 真实报为非通过，而不是被静态检查抵销。
