# P3-111 本地 UI 动态 Evidence 闭环表

范围：仅本任务 unsigned native Tauri app 的实际操作。所有保存的结构化结果、AX 日志和截图均不包含用户原文、客户端 key 或 DB 内容。`m005` 的保存后默认页不截屏，是为避免将用户输入收录到 Evidence；其余截图均来自不会展示原文的状态页。

| 验收项 ID | 具体动作与前置状态 | 预期可观察结果 | 结构化结果 ID | 视觉／日志 Evidence 路径 | SHA-256 | 状态（PASS / N/A / NOT IMPLEMENTED） | N/A 理由 |
|---|---|---|---|---|---|---|---|
| D-001 | Native app 首次启动；真实专用目录及 DB 尚不存在；默认恢复页为空态。 | 默认页显示本地 runtime 闭合状态、来源提示及可输入记录区。 | `DYN-M001` | `screenshots/m001-default-empty.png`; `raw/m001-default-empty.ax.txt` | `a3d33590bb54fbe5c8be37bc8e5b3c2249b493f50f98c96aa9ff3c9aa5f54a03`; `bfedb8ac2437f74bcfe2d9a05c312b292855377db983e2a8244ecc33a8e3c062` | PASS | — |
| D-002 | 从默认页实际导航至“暂无可靠建议”。 | 建议关闭态、记录入口和本地状态可见；无外部建议被伪造为可用。 | `DYN-M002` | `screenshots/m002-no-suggestion-empty.png`; `raw/m002-no-suggestion-empty.ax.txt` | `e03bd760c72e1d5f549d5ccf0da97115b679155c478abd176cb831ce543a5173`; `41c4c07a352b001ea8c29cdbbcfe29a1af5d87313cbd13098718d4570036e7ab` | PASS | — |
| D-003 | 从导航实际进入“受限／离线”页。 | 离线、权限与外部能力均明确为关闭态，记录入口仍可见。 | `DYN-M003` | `screenshots/m003-restricted-empty.png`; `raw/m003-restricted-empty.ax.txt` | `d4db78937f00ac6a9a62d06867559650f5080965c26e9186e39cacf57e974544`; `ef8546590e58b56b1756b1e89956ccaad706062f2ea594f02b3e077689fb4d2e` | PASS | — |
| D-004 | 空态 native 窗口中实际按 Tab；尚未输入真实文本。 | 焦点能够进入界面可访问控件；此行为不被用作 Enter 提交的替代证明。 | `DYN-M004` | `raw/m004-keyboard-tab.ax.txt` | `ef8546590e58b56b1756b1e89956ccaad706062f2ea594f02b3e077689fb4d2e` | PASS | — |
| D-005 | 用户在 native app 内主动手工提交低敏感短文本；最多三条授权上限内。 | 保存提示和本地 backend 状态成立；后续无原文页面显示的状态页观察到 2 条记录／2 条审计。 | `DYN-M005` | `raw/m005-user-save-redacted.json`; `raw/actual-pilot-metadata.json` | `145cd424b70ef2fbcd4a44bead43396cb503a77879c47d1b9ed9d349481df110`; `2d302442189f56b5dcd8e8d52daba514aa1c99afbc96e67e527881e09547e387` | PASS | — |
| D-006 | 默认页执行实际刷新 `Super+R`，已发生用户保存。 | 刷新后由 backend 恢复权威 Today 状态；不以残留 toast 作为证明。 | `DYN-M006` | `raw/m006-refresh-redacted.json` | `60f58703bdc2870e31b75d0b779db9544fca731ffbaef0204b4672e2c4c1b205` | PASS | — |
| D-007 | 刷新后实际导航至“暂无可靠建议”。 | 安全状态页仍显示 2 条记录、关闭态和可用记录入口；不展示原文。 | `DYN-M007` | `screenshots/m007-no-suggestion-after-user-save.png`; `raw/m007-no-suggestion-after-user-save.ax.txt`; `raw/m007-refresh-navigation-redacted.json` | `fc293a702e215e54ba5cfbb6010d2c80ee6697724a256ccb67f405334cf4c0bb`; `31c3459bc6e0c07d2ee6f2c7b3a5c9d47d02105a103599b9bc96626dc4a1dc87`; `3931c3d12e7ae7965bc889184feaac8eabd0bf0da9e5889f9c20ee4e684b6870` | PASS | — |
| D-008 | app 实际 `Super+Q` 关闭，随后以同一 unsigned app 全新启动。 | 关闭与重开为独立动作；重开后默认页从 backend 恢复，不以刷新代替。 | `DYN-M008` | `raw/m008-close-reopen-redacted.json` | `95cf92da5b4108cdede9892ce9bd886c49e6fe4a95ae28d0214442c184002909` | PASS | — |
| D-009 | 重开后实际导航至“暂无可靠建议”。 | 安全状态页继续显示 2 条记录，无原文 Evidence。 | `DYN-M009` | `screenshots/m009-no-suggestion-after-reopen.png`; `raw/m009-no-suggestion-after-reopen.ax.txt` | `c21f4ae3e1545aa632319cad0ccd8d6d8aa81edb92eccabf39fe3f898e407c89`; `1c5f7af5db3f6a11fc96716a3ded9c6b9e762498da93a722a87fcbab32549852` | PASS | — |
| D-010 | 重开后实际进入“受限／离线”页。 | 受限来源、离线和未启用设置保持可辨，记录数量仍为 2。 | `DYN-M010` | `screenshots/m010-restricted-after-reopen.png`; `raw/m010-restricted-after-reopen.ax.txt` | `0b40206a37641eb3b67fdc17dd9eea6f0f2a34d1dc497597320ba5bc2013ab9d`; `43615767783d236d5f82d088986c39bcbda54ccec81bd4ec50f90bc54b5c2935` | PASS | — |
| D-011 | 重开 native app 后实际 Tab，再实际 Enter 触发“设置未启用”控件。 | 真实键盘路径触发明确的未实现关闭提示，记录数仍为 2；未将“可聚焦”误写为提交证明。 | `DYN-M011` | `raw/m011-keyboard-tab-enter-redacted.json`; `raw/m011-keyboard-tab-enter.ax.txt` | `27bd23798c09db5517d267f8595a9125504730c3442ca7230f295f570bfd70ad`; `eb628798531f6dba367669422e97ccdd6ab725e8ed987aae18945862d39edf44` | PASS | — |
| D-012 | 固定非敏感 runner 独立执行首次、重复／幂等、冲突、原子失败、路径／类型／sidecar／tamper 拒绝与临时清理。 | 8 个 Rust 测试通过；未知 IPC／额外参数拒绝；夹具和 shadow 残留为 0。 | `DYN-M012` | `raw/fixed-lifecycle.json`; `raw/negative-results.json`; `raw/cleanup.json` | `f1e0d288dec1d57b7b2e79a1d4d6278c9bf03eacdfdee232df4294924c46d2cc`; `7c685ba1e528ff265ef2474ac3c8f42fad1c24505b4f99d5cd5dd98945a1a73e`; `d7e6ed130161e352aa623ad22fcac0a3a422c2c4db682a5f84c7c2f679a105fc` | PASS | — |

## 逐项闭环判定

- 全部必填动态行均为 `PASS`，无 N/A、无 `NOT IMPLEMENTED`。
- 刷新（D-006）与关闭重开（D-008）独立执行；初始 Tab（D-004）与实际 Tab/Enter（D-011）独立记录。
- D-005 的实际内容仅由用户在 app 内输入并由 retained DB 保存；Evidence 仅保留无原文的状态／计数／metadata，未读取 DB 内容。
- 本表由 `tools/semantic_verifier.py` 解析：必须出现 D-001 至 D-012 且全部为 PASS，才能通过语义校验。
