# LIFEOS-P3-130 独立 actual‑Tauri 动态闭环矩阵

本矩阵只引用本目录内由本次全新隔离复评生成的原始 AX、截图、SQLite/audit 快照、原生几何和机器核验；没有调用、复制或导入 Engineering runner。

| AC | 独立动作 | 复评原始 Evidence | 结论 |
|---|---|---|---|
| AC-01 | 重算 corrected Task Contract、75 行物理 allowlist、V1.0、P3-128 handoff 和工程 Manifest；复算 P3-126 75/75 源行 | `static_verification.json` | PASS |
| AC-02 | 离线 bundle；invalid build-time root 在 build output 前拒绝；既有三 IPC 严格 DTO 由静态与候选回归补充核对 | `root-fail-closed.json`、`candidate-regression.json` | PASS |
| AC-03 | 空库 actual App → capture → 同 key 重试；核对不可变文本、Source、Artifact 和 audit | `actual-confirm-initial.ax.txt`、`actual-confirm-captured.ax.txt`、`actual-confirm-repeat.ax.txt`、`run-confirm-candidate-db.json` | PASS |
| AC-04 | actual capture 后 UI/DB 均为 `candidate`，未出现静默确认 | `actual-confirm-captured.ax.txt`、`run-confirm-candidate-db.json` | PASS |
| AC-05 | 独立 actual App confirm 与另一全新 root reject；候选回归补充 strict conflict／重复确认核对 | `actual-confirm-confirmed.ax.txt`、`run-confirm-confirmed-db.json`、`actual-reject-rejected.ax.txt`、`run-reject-db.json`、`candidate-regression.json` | PASS |
| AC-06 | 关闭实际 App 后重新启动同一 task-local DB；Today/Context 恢复 confirmed 原始记录、Link、Feedback 与 audit | `actual-confirm-reopened.ax.txt`、`run-confirm-confirmed-db.json` | PASS |
| AC-07 | actual Memory 页面显示 Source、Artifact、typed Link、Feedback、Audit 引用和 `memory copy: false` | `actual-confirm-memory.ax.txt` | PASS |
| AC-08 | Inspector 移除 Selection 后 UI 为 `selection_included:false` 且声明未调用写 IPC；DB 前后 SHA-256 同为 `51d185…249af` | `actual-confirm-selection-removed.ax.txt`、`run-confirm-candidate-db.json` | PASS |
| AC-09 | 三个全新 actual roots 分别使 source、tombstone、authorization 失效；confirm 显示证据缺口且 mutation 后 DB SHA-256 不再变化 | `actual-mutation-*-fail.ax.txt`、`mutation-source.json`、`mutation-tombstone.json`、`mutation-authorization.json` | PASS |
| AC-10 | 候选回归覆盖 unknown fields、非法 Context/capture、key conflict 和 atomic failure；invalid root 在 build 输出前失败 | `candidate-regression.json`、`root-fail-closed.json` | PASS（补充回归；未把工程自测当作 actual UI 正证据） |
| AC-11 | 直接源码／capability／runtime scan：actual command surface 恰为五项；无 renderer permission、网络、Model、Agent、generic Context/Memory 表 | `static_verification.json` | PASS |
| AC-12 | 逐行 actual UI → IPC → SQLite/audit → UI，另有三档 actual 原生逻辑内容边界 | `actual-confirm-*.ax.txt`、`run-confirm-*.json`、`native-geometry-*.jsonl`、`verification.json` | PASS |
| AC-13 | 清理前 inventory、保护输入 post-hash、exact root deletion 与 absent check；复评 Manifest 将非自指 | `pre-cleanup-inventory.json`、`cleanup.json`、`verification.json`、`FINAL_MANIFEST.json` | PASS |

三档几何的最终 raw 行分别为：1280×1024、1160×768、700×760 logical content bounds；物理截图仅作为可见状态，未被当作逻辑几何替代。
