# LIFEOS-P3-086 独立安全／体验复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-086
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：仅 P3-085 三张纯本地、无持久化 UI 页面与 `app.js`、`styles.css`；hash 见 `evidence/MANIFEST.md`。
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-085_three_frozen_today_pages_multipage_local_ui_shell_controlled_capability_package.md`
- 独立评审角色：独立安全／体验评审
- 协审视角：产品架构、AI 信任与安全、技术架构
- 评审关卡：Gate 1／3／4 的有限 UI 边界；Gate 2、Gate 5 不作运行时批准。
- 独立评审路径：新会话、task-local 临时副本、新写静态 runner；未使用执行侧或历史 runner 作为主验证。
- 评审结论：**Blocked**

## 能力包独立性与回流规则（适用时）

- 执行侧与评审侧是否隔离：Yes。本会话未执行 P3-085 工程实现或 PM 验收。
- 是否只评审能力包的最终 Evidence／hash：Yes。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：Yes，见 `evidence/`。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes；runner 源码为新写，仅用 Node 标准库读取 task-local 副本。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：Not Implemented=1，影响完成定义；没有 P0/P1/P2、hash 冲突或独立性不足。
- 若需整改：不得创建微型整改任务；应由 PM 决定回到 P3-085 能力包或采用合规、可用的 Chrome 复评路径；完成后必须新的全新隔离独立复评。
- 更新时间：2026-08-21 CST

## 本地 `file:` 动态 Evidence 预检（仅适用时）

- 指定浏览器与 bundle id：Google Chrome（`com.google.Chrome`）。
- task-local `file:` 入口／副本 hash：`file:///private/tmp/lifeos-p3-086.amAXQ3/app/default-recovery.html`；hash 见 `evidence/MANIFEST.md`。
- 新 Chrome 标签页首次预检：Not Implemented；浏览器控制安全策略在导航前拒绝 URL，记录见 `evidence/operation_log.md`。
- 若首次失败，新 Chrome 标签页第二次预检：N/A；首次拒绝的返回明确禁止重试同一结果的替代、间接、CDP、浏览器命令或策略规避。
- In-app Browser 结果（如有）：未使用；不作为结论依据。
- 动态矩阵是否只在 Chrome 预检通过后开始：Yes；未通过，矩阵未启动。
- 若候选 Blocked：两次 Chrome 正常加载失败是否均有记录，且未使用 HTTP／网络／CDP／命令行浏览器／策略绕过：No；因此本结论是当前评审执行被外部浏览器控制策略阻断，而非工程 Chrome 动态失败的技术归因。

## 评审摘要

- 五项 P3-085 工程 hash 与 task-local 副本一致；P3-082 三项历史只读 hash 也一致，未发现覆盖或漂移。
- 新写独立静态 runner 在临时副本得到 29 PASS / 0 FAIL，覆盖三页、相对导航、叙事、确认／失败结构及禁止能力关闭态。
- 静态范围内无网络、远程 URL、浏览器持久化、文件 API、真实文件／DB、Tauri/IPC、导出、同步或模型调用。
- Google Chrome 新标签页的直接 `file:` 预检被浏览器控制安全策略在导航前禁止；按该策略不得采用替代或绕过。
- 因此动态三页、交互、刷新／关闭重开及视觉 Evidence 均 Not Implemented，不能以 P3-085 PM 动态 Evidence 或静态测试替代。
- P0=0、P1=0、P2=0、Unknown=0、Not Implemented=1；影响完成定义，不能给出 Pass 或 Pass with Conditions。

## 已通过内容

- 最终工程与历史只读资产 hash 可复核且一致。
- 独立性、runner 可复跑性与静态关闭态均成立。
- Gate 1 的“从这里继续”、无可靠建议不虚构重点，以及 Gate 3 的 AI 未启用／显式确认文案，静态核验成立。

## 关键问题

- 任务卡强制要求的独立 Chrome `file:` 动态／视觉矩阵未形成；这是影响完成定义的 Not Implemented，不能由历史 PM 复验转移或补足。

## 必须整改项

1. PM 需提供或指定一个允许直接进行 Google Chrome 新标签页 `file:` 正常加载的合规评审表面；不得使用 HTTP、网络、CDP、命令行浏览器、其他浏览器或绕过。
2. 在 Chrome 预检通过后，由与本次失败会话隔离的新独立评审会话重新完成完整动态矩阵、视觉记录、hash 和 Manifest。

## 条件通过项

无。动态 Evidence 未完成，因此不适用 Pass with Conditions。

## 关卡检查

- Gate 1 产品一致性评审：Partial。静态叙事符合“找回上下文、下一步、不过度打扰”；动态体验未验证。
- Gate 2 数据与来源评审：N/A。本任务不批准任何数据运行时能力。
- Gate 3 AI 权限与信任评审：Partial。静态 AI 未启用、显式确认与受限 fail-closed 成立；动态行为未验证。
- Gate 4 技术可行性评审：Partial。静态本地关闭态与相对资源成立；指定 Chrome 动态路径未完成。
- Gate 5 用户价值验证评审：N/A。本任务不作运行时批准。

## 风险

- 不更新风险账本。当前限制是评审环境的浏览器控制策略，并非已证实的 P3-085 工程缺陷；仍须由 PM 判断后续路径。

## 需要 PM 决策

- Yes：决定如何在不违反任务卡 Chrome-only、无绕过规则的前提下恢复独立动态／视觉验证；不得据此关闭风险、冻结资产、恢复工程基线或进入 Stage 4。

## 最终建议

不建议冻结、采纳为独立 Pass、关闭风险、恢复基线或进入下一阶段。保持 P3-085 Not Frozen；先解决合规 Chrome 动态验证的评审可达性，再形成一轮全新隔离独立复评。
