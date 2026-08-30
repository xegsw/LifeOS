# attempt-6 actual-Tauri 身份与三档窗口矩阵

所有条目均来自本轮独立构建的 bundle，且每一档都由其自身 direct-launch PID 启动；没有复用历史 PID、窗口、receipt 或截图。截图只含固定合成界面，不含真实正文、Health 值、凭据或 Provider 通信内容。

| 档位 | direct PID | receipt 稳定样本 | receipt observed outer logical | 同 PID exact-title AXWindow | 新截图 | 结论 |
|---|---:|---|---|---|---|---|
| desktop | 30637 | `post_set_size_stable_samples`，220ms 后 3×、间隔80ms | 1280×949 | 1280×949 | `screenshots/desktop_bundle_direct.jpg` | 尺寸/PID/title 一致；Web role 未证明 |
| compact | 30792 | 同上 | 700×760 | 700×760 | `screenshots/compact_bundle_direct.jpg` | 尺寸/PID/title 一致；Web role 未证明 |
| narrow | 30875 | 同上 | 560×640 | 560×640 | `screenshots/narrow_bundle_direct.jpg` | 尺寸/PID/title 一致；Web role 未证明 |

## 绑定链与反证

- Bundle：`LifeOS P3-141 Controlled Pilot Candidate.app`；bundle id `local.lifeos.p3-141`；release executable SHA-256 `fafbdd0649d44825538621ba2b4462a65a33a8c9c4bb5d7a9af49060f6d8426b`。
- 每项 receipt 是本 PID 的 `p3-141-actual-viewport-<pid>.json` 副本：`raw/desktop_bundle_receipt.json`、`raw/compact_bundle_receipt.json`、`raw/narrow_bundle_receipt.json`。三者均记录 `network_dispatch_count: 0`、`content_recorded: false`、`synthetic_fixture: true`。
- 每项原生 AX probe 以 PID 创建 application element，再在其 `AXWindows` 中筛选 exact title；没有枚举其他 app 来建立身份。原始结果在 `raw/*_bundle_ax_pid.json`。
- 三项 probe 都得到唯一 exact-title AXWindow；但递归到 `AXChildren`、`AXContents`、`AXVisibleChildren`、`AXFocusedUIElement` 后，仍只得到 `AXWindow`／`AXGroup`／`AXButton`／`AXStaticText`，并没有 `AXWebView` 或 `AXWebArea`。属性级复核保留在 `raw/ax_attribute_probe_final.json`。
- Computer Use 的本轮 bundle accessibility surface 确实显示 `HTML content`，URL 为 `tauri://localhost`，且界面可交互；但这是 app-level semantic surface，不是同一 direct PID 的原生 `AXWebView/AXWebArea` 结果，不能替代 ABF-M-016 的明确要求。

## 视觉检查

- desktop：Today、五字段结构化 Health 控件、固定合成候选、离线无 Provider 标识均可见；没有真实内容。
- compact：主要 Today/Health 控件可见，窄高滚动布局没有截断关键控件。
- narrow：侧栏、场景／失败关闭控件和五字段 Health 控件在 560×640 下可见；下方候选通过页面滚动承载。

因此，三档的稳定 receipt、direct PID、exact-title AXWindow、尺寸对照和视觉检查均成立；但 `AXWebView/AXWebArea` 是 P0 必需节点，未被本轮原生 PID AX 链证明。ABF-M-016 为 `P0_BLOCKED`，不以截图或 app-level `HTML content` 补足。
