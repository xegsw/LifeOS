# LIFEOS-P3-122｜P3-116 实际 UI 强制继承、主机无关原生视口与 Evidence 谱系后继

## 会话与授权

- 会话类型：全新 Codex 专项工程执行会话；不是 PM 主会话，也不是独立评审会话。
- 授权证据：用户投递绝对任务卡路径；投递时间 2026-08-25 22:59 CST。用户随后确认按任务卡升级配置继续执行。
- 实际模型配置：`gpt-5.6-terra + xhigh`。
- Frozen ABF：`ABF-P3-122-v1`，SHA-256 `2aacd353ad50e5d00c92f168e3f508f5e6488336ebcc8385aba56437e70b0a42`。
- 任务卡最终 SHA-256：`1666bcad2a11a4949f695c60a9dcd417ffbe8eef647ef6e8c5d77d4497f48d14`。
- 启动前复算：10/10 Frozen inputs、P3-116 visual 8/8、P3-121 Runtime/Tauri 65/65 全部匹配后才创建工程根。

## 事实

### 候选与继承

- 新候选：`lifeos/engineering/LIFEOS-P3-122/candidate/`。
- P3-116 `styles.css`、`app.js`、`fixtures.js` 和四个视觉／交互合同文件保持 byte-exact；`index.html` 只增加两个明确 adapter tag，移除这两行后与 P3-116 source byte-exact。
- P3-121 current `ui/` 未作为视觉输入；候选视觉层哈希与 P3-121 current UI 不相交。
- P3-121 Runtime/Tauri 白名单逐文件复制。只在 P3-122 候选内适配任务 identity、前端绑定、精确 task-local root、native geometry 和无装饰 task-local Tauri window；三项 IPC、SQLite schema/version、合成生命周期与禁能边界保持不变。
- 新增 `runtime-adapter.js` 只调用 `runtime_status`、`get_today`、`capture_record`，只更新现有 Runtime status、Today/Recent 与 receipt slot；未新增可见产品 chrome。
- P3-116 原 CSS 在窄屏新 Workspace 中存在一个继承冲突：早期通用 `.workspace-inspector { grid-column: 2 }` 使 700 宽 computed grid 成为 `0px 546px`。候选保留原 `styles.css` byte-exact，并用独立 `viewport-adapter.css` 的一条规则将 `.workspace-reference .workspace-inspector` 在 `max-width:1120px` 复位为第 1 列。修正后 700×760 computed grid 为单列 `568px`，document horizontal overflow 为 false；这是一条窄屏适配修正，不是页面重设计。

### 原生逻辑视口与实际截图

| 请求逻辑 content | Native content | WebView inner | DPR | 当前显示 | 实际可见截图 | 结论 |
|---|---|---|---:|---|---|---|
| 1280×1024 | 1280×1024 logical | 1280×1024 | 2 | 1512×982，available 1512×949 | JPEG 960×768；宿主可见裁剪／capture 缩放单列披露 | PASS |
| 1160×768 | 1160×768 logical | 1160×768 | 2 | 同上 | JPEG 1160×768 | PASS |
| 700×760 | 700×760 logical | 700×760 | 2 | 同上 | JPEG 700×760 | PASS |

- `decorations:false` 只用于 task-local Tauri Evidence shell，使 native outer/content 与 WebView content 的逻辑尺寸一致，避免把 32px 标题栏误计入 content；不改变 P3-116 DOM/CSS/Token，也不增加产品 capability。
- 1280×1024 的逻辑 content 真实成立；其物理高度超过当前 display available height 949。实际 App screenshot 仅证明当前主机可见状态，未被标成 exact logical screenshot，也未要求用户修改 macOS 显示缩放。
- Today、Me、Contexts、Memory、Global AI、AI Workspace 在三档各有 actual Tauri screenshot、AX/DOM attestation、computed-style key、native trace 与 hash，共 18/18 页面行。三档 document horizontal overflow 均为 false；导航、主操作、Global AI 与 Workspace 展开入口均由实际点击到达。

### Runtime 与失败关闭

- 实际 renderer→IPC→DB→UI：首次 capture 显示 `Runtime 已保存用户原文`；重复 capture 沿用同一 record ID 并显示 `Runtime 幂等重复`；`Cmd+R` 后 Today/Recent 仍显示原文；关闭并重开 `.app` 后记录恢复。
- 最终复制 DB：SQLite `quick_check=ok`、`user_version=104`、1 条固定合成 record、2 条 audit（`capture_saved`、`capture_repeat`）。
- 离线 Rust tests：9 passed，0 failed。结构化 unit trace 另行证明 first/repeat/second/refresh/reopen，以及 injected atomic failure 前后 DB 与 sentinel hash 不变。
- Runtime command inventory 与 renderer invoke inventory 均精确为 `capture_record`、`get_today`、`runtime_status`；capability permissions 为 `[]`；无 network、model、shell、process spawn、Vault、export、sync 或新产品 IPC。
- 最终 Tauri `.app` bundle 构建成功。离线工具链缺少 `rustfmt` component，因此没有联网安装；release build 的 `rust-objcopy` debug-strip 发出本机 `libLLVM.dylib` warning，但 cargo/Tauri 仍 exit 0 并生成可启动 bundle。两项均作为工具说明披露，不改写为产品缺陷或通过依据。

### Evidence 与谱系

- 结构化结果根：`lifeos/engineering/LIFEOS-P3-122/evidence/results/`。
- 页面矩阵：`page-matrix.json`（18/18）。
- 三档 geometry：`viewport-results.json` 与 `evidence/native-traces/{1280x1024,1160x768,700x760}.jsonl`。
- Runtime：`runtime-lifecycle.json`、`runtime-final.sqlite` 与 UI state/screenshot。
- 双 source 谱系：`source-lineage.json`。
- 禁能：`static-boundary.json`。
- ABF 行闭环：`dynamic-closure.json`（I-01～I-11、M-001～M-015）。
- 历史保全：`history-integrity.json`，10/10 Frozen inputs 在清理后仍匹配。
- 精确清理：`cleanup-proof.json`。只对唯一临时根内 5 个固定路径逐一 unlink，再对空根执行精确 rmdir；`/private/tmp/lifeos-p3-122-native-evidence-v1` 已 absent。
- Final Manifest：`lifeos/engineering/LIFEOS-P3-122/evidence/final-manifest.json`。它不包含自身，分层覆盖 authorization、task/ABF、P3-116 visual source、P3-121 Runtime source、history、current candidate、tools/tests、results/logs/screenshots、current delivery、PM inputs 与 cleanup。
- Final verifier：`manifest-verification.json`；mutation：`mutation-results.json`。pristine control 必须先 PASS，随后 visual CSS drift、P3-121 UI contamination、授权遗漏、PM Evidence 遗漏、错 logical viewport、错 screenshot 语义、candidate drift、extra/missing file、history drift 共 9 类必须全部被拒绝。

## 推断

- 本执行侧 Evidence 支持“Candidate Ready for PM Acceptance + fresh isolated independent review”，不等于 PM Pass、User Adopted、Frozen、风险关闭或 Stage 4。
- 1280×1024 的物理 screenshot 与逻辑 geometry 不同是当前宿主可见范围事实，不是 CSS 缩放图，也不是对逻辑 content 的替代证明。
- 窄屏 Workspace 单规则修正关闭了实际 P1 响应式冲突，同时保留 P3-116 原 source bytes 与页面概念；是否接受该候选仍由 PM 按 Frozen ABF 判断。

## 建议

- PM 应先复跑 `python3 -B lifeos/engineering/LIFEOS-P3-122/tools/build_evidence.py verify`，再核对 1280 物理裁剪披露、700 Workspace 单列截图和 Final Manifest mutation。
- PM 若验收通过，仍需创建全新隔离独立评审会话；本会话不得独立评审自己刚完成的 P0 Tauri/Evidence 成果。

## 待确认与关卡

- 待 PM 确认：是否按 `ABF-P3-122-v1` 接受本候选并进入全新隔离独立评审。
- PM Acceptance：Pending。
- Fresh isolated independent review：Pending。
- User adoption：Not requested / Not decided。
- Freeze、风险关闭、账本更新、Stage 4：均未执行。

## 自检结论

- I-01～I-11：11 PASS / 0 fail。
- M-001～M-015：15 PASS / 0 fail。
- P0/P1/P2/Unknown/Not Implemented：0/0/0/0/0。
- silent N/A：0。
- 包内执行侧结论：PASS；候选等待 PM 验收与新的独立复评。
- 本地模型预检：按任务卡允许场景跳过。原因是本轮涉及关键 Tauri/IPC、原生 geometry 与 Evidence 谱系高风险最终判断；本地模型不能替代 PM 或独立评审结论。
