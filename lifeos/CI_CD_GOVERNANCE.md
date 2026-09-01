# LifeOS CI/CD 与可恢复执行治理 V1

生效日期：2026-09-01
适用决策：D-0635 及以后

## 目标

CI/CD 的目标是尽早阻止已经确认的产品能力、架构基线和 Task Contract 被后继任务静默改坏；它不把宿主机锁屏、窗口暂时不可见或一次截图不合格误判成工程失败。

长期原则：

> 确定性问题自动失败；可恢复环境问题暂停并从检查点继续；只有授权边界或证据可信度被不可逆破坏时才使本次尝试失效。

## 失败分类与动作

| 类别 | 典型事实 | 状态 | 处理 |
|---|---|---|---|
| Candidate Failure | 自动测试、合同断言、数据生命周期或失败关闭不满足 | Closure Cycle | 同任务修正候选，只重跑受影响测试及其依赖门禁 |
| Evidence Gap | 截图尺寸错误、缺少一档视口、Manifest漏项，但候选和边界未受污染 | Evidence Closure | 排除错误产物，补取受影响 Evidence；不重做已验证的构建和测试 |
| Recoverable Environment | 锁屏、登录会话不可见、AXWindow暂不可得、截图服务不可用、runner临时离线 | Paused — Resumable | 写检查点，安全停止 App/写入者；环境恢复后从最早受影响阶段继续 |
| Recoverable Procedure | 错用了无敏感内容的截图尺寸或目标，但未接触禁止数据／路径 | Paused — Resumable | 将错误产物列入 excluded artifacts，重做该 Evidence 阶段 |
| External Blocker | 必要外部条件在有界恢复尝试后仍不可用 | Blocked | 保留检查点，等待外部条件或 PM 变更路线 |
| Irrecoverable Invalidation | 接触禁止路径／真实数据／网络／凭据；修改只读候选或历史；正 Evidence 无法与污染分离 | Invalidated Attempt | 保全事故记录；仅重启受污染的评审／Evidence attempt，不自动重建工程候选 |
| Contract Change | 用户结果、范围、数据、权限、风险、架构、Schema/API或冻结合同改变 | Superseded / New Task | 关闭或取代原合同，建立新任务 |

错误截图只有在包含任务外真实信息且无法证明已精确隔离和清除，或由禁止的全屏／外部目标采集造成越界接触时，才升级为安全事件。普通尺寸、裁切、窗口定位或渲染错误均不得使整个工程尝试失效。

## 检查点与恢复

推荐阶段：

1. `preflight`
2. `build_test`
3. `data_lifecycle`
4. `app_launch`
5. `native_window_binding`
6. `visual_capture`
7. `cleanup`
8. `manifest`

L2/L3/Gate 动态执行必须在阶段边界写入符合 `lifeos/templates/EXECUTION_CHECKPOINT_TEMPLATE.json` 的 `checkpoint.json`。暂停时至少记录：

- Task Contract、候选和基线摘要；
- 已完成、待完成与需重跑的检查；
- 暂停原因及是否触及禁止边界；
- 已排除产物；
- App/PID、DB、临时根和清理状态；
- `resume_from` 与 `safe_to_resume`。

恢复必须同时满足：

- Task Contract、候选与基线摘要未变化；
- 已完成 Evidence 的 hash 仍一致；
- 没有禁止路径、数据、网络或凭据接触；
- 临时根仍符合 marker／权限合同，或已按合同精确清理并可重新创建；
- 没有遗留写入者、PID或DB锁冲突。

若以上条件成立，只从 `resume_from` 继续。已经通过且未受影响的构建、自动测试、mutation和hash复算不得机械重做。若候选或合同发生变化，从其最早影响阶段重跑，而不是默认从阶段0开始。

## CI 门禁

GitHub Actions 工作流位于 `.github/workflows/lifeos-ci.yml`，包含：

1. **Governance Guard**：校验确认基线 hash、治理模板、检查点 Schema、未来任务卡 CI/恢复字段和 JSON 语法。
2. **Deterministic Regression**：在 macOS runner 上执行 `lifeos/ci/task_checks.json` 注册的自动测试；禁止接触真实数据、Pilot、凭据和外部 Provider。
3. **Synthetic Candidate Package**：仅通过手工 `workflow_dispatch` 生成内部合成候选包；不是生产发布、真实能力启用、产品冻结或 Stage 切换。

CI 必须失败的情况：

- 确认基线内容发生变化但基线登记、决策记录未同步；
- 新任务缺少 CI 检查清单或可恢复执行策略；
- 自动测试、合同断言、回退检测或结构化 Evidence 校验失败；
- 工作流尝试使用真实 DB、Pilot、真实文本、凭据或 Provider。

CI 不应失败的情况：

- 本地桌面锁屏或前台会话暂不可用；
- GUI／AX／截图人工 Gate 尚未执行；
- 需要用户亲验但尚未到该 Gate。

这些情况应在专项执行中记为 `Paused — Resumable`，不进入 CI 红灯，也不生成新的工程任务。

## CD 边界

当前 CD 仅指“通过确定性门禁后，打包不含 DB、Evidence、凭据、缓存和真实内容的合成候选源码包”。它：

- 只允许手工触发；
- 不签名、不公证、不上传商店、不自动部署；
- 不包含真实 Provider 能力或 Pilot 数据；
- 不改变风险、冻结、产品验收或 Stage 状态。

未来若需要真实发行、签名、公证、自动更新或外部用户部署，必须建立新的 Task Contract 和风险评审。

## 普通任务自动提交与合并

D-0636 起采用以下长期授权：

- 普通 L0/L1/L2 任务 PM Pass 后，执行方自动创建或复用 `codex/l0-*`、`codex/l1-*`、`codex/l2-*` 任务分支，只提交任务合同内文件并推送该分支；
- GitHub CI 全绿、远端 `main` 未分叉、提交中不存在未声明文件或敏感资产时，允许自动快进合并 `main`；
- CI 失败时保持原任务 Closure Cycle，不合并 `main`；
- 锁屏／GUI Gate 暂不可用时保持 `Paused — Resumable`，不因自动化等待创建新任务；
- L3/Gate、真实数据、凭据、网络、外部用户、风险关闭、关键冻结与 Stage 切换始终禁止自动合并；
- 工作区存在无关修改、远端和本地主线双向分叉、合并冲突、基线变更或疑似敏感文件时，自动化必须停止并报告精确原因。

“自动合并”仅指满足上述条件的 Git 快进更新，不授权 force push、历史重写、删除远端分支保护或覆盖他人提交。

## 责任边界

- CI：确定性回归与基线防漂移。
- 专项执行会话：写检查点、在安全点暂停、环境恢复后定向继续。
- PM：判断类别、受影响最早阶段、是否允许恢复，以及是否真正达到不可恢复失效。
- 用户：只在真实数据、凭据、网络、不可逆动作、风险／冻结／Stage等新增边界时确认；解锁桌面或恢复前台会话不构成新授权。
