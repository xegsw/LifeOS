# P3-115 交互合同

## 1. 边界与身份

这是一个**完全本地、固定 synthetic fixture、浏览器内存状态**的高保真原型。它没有 runtime、网络、模型、数据库、文件读写、Tauri/IPC 或持久化。所有“你”“工作”“健康／健身”“反馈”文字都是固定合成情境；页面不得把任何回执称为已保存、真实 AI 输出或真实健康建议。

动态检验只允许由 Google Chrome 直接打开干净任务副本的 `file:` URL；页面不包含远程资产或任何网络请求。

`Person` 是一级主体。`Project` 只在工作建议中以“产品演示准备”作为语境出现，不参与导航、首页选择或全局价值排序。

| 身份 | 原型中的可见表达 | 不能被误读为 |
|---|---|---|
| Source | `SRC-SYN-*` 标签、详情中的来源 | 真实用户原文或外部接入 |
| Artifact | `ART-SYN-*` 与版本 | 数据库实体或真实文件 |
| Derivation | “当天理解更新” | 用户已确认事实 |
| Advice | 可选、可拒绝、显示依据的建议 | 自动 Action／执行结果 |
| Feedback | 认可、修改后接受、拒绝、延后 | 执行或效果 |
| EXE | 用户明确报告的执行 | 反馈或结果 |
| RES | 用户报告的结果 | 医学结论 |
| Memory candidate | 待确认、有限范围、可撤销 | 已跨日生效的偏好 |

## 2. 事件、前置状态与可见回执

| Event | 前置状态 | 状态转换 | 用户可见回执 | 失败后置状态／runtime 边界 |
|---|---|---|---|---|
| `ANS_SAFE` | 唯一问题未答，来源有效 | `ANS=安全` | 出现一条低风险、可停止选项 | 仍非医疗；未来 runtime 必须保留 Answer 身份与时效 |
| `ANS_SKIP` | 唯一问题未答 | `ANS=跳过` | “跳过不是安全回答”，健康建议降级 | 无训练型建议，不自动追问／提醒 |
| `ANS_WARNING` | 唯一问题未答 | `ANS=警示` | 停止建议，提示适当专业支持 | 不诊断、不推荐治疗；未来 runtime 必须 fail-closed |
| `FDB_ACCEPT` | `ANS=安全` | `FDB=认可` | “认可为可选项；未执行” | 不创建 Action |
| `FDB_MODIFIED_ACCEPT` | `ANS=安全` | `FDB=修改后接受`，原 Advice 保留 | 修改内容和原 Advice 同时可见 | 不推定 EXE；未来 runtime 应保留两个内容身份 |
| `FDB_REJECT` | `ANS=安全` | `FDB=拒绝` | “不适用；不推定执行” | 不写长期偏好 |
| `FDB_DEFER` | `ANS=安全` | `FDB=延后` | “不自动排程或提醒” | 到期语义需 future runtime 明确实现 |
| `EXE_REPORTED` | `FDB=修改后接受` | `EXE=已执行` | “实际执行由用户报告；仍无结果” | 不推定效果 |
| `RES_REPORTED` | `EXE=已执行` | `RES=已报告` | 仅当天理解更新：今晚不再追加训练型建议 | 非医学评估；未来 runtime 应绑定输入版本 |
| `MEM_CANDIDATE` | `RES=已报告` | `MEM-CAND=待确认` | “不影响未来日期” | 未确认不得影响排序、建议或下一步 |
| `MEM_CONFIRM` / `MEM_REJECT` | `MEM-CAND=待确认` | 有限确认／拒绝 | 明示原型中状态与范围 | 不产生真实持久化；未来 runtime 需要确认、范围、时效和撤销协议 |
| `SOURCE_FAILURE` | 任意 | `missing`／`stale`／`conflict`／`unauthorized` | 显示缺口，关闭个性化建议 | 相关 Derivation/Advice stale，不复活 |
| `REVOKE_ANS_FDB_EXE_RES` | 已有任意链路 | 依赖理解/Advice stale；Source 保留 | “已撤销本次链路” | 不静默删除 Source/Artifact 历史 |
| `REFRESH_OR_CLOSE_REOPEN` | 任意 | 回到初始内存状态 | 无“恢复已保存”暗示 | 证明原型无持久化，不代表 runtime 恢复实现 |
| `CAPTURE_PREVIEW` | 任意 | 打开说明 Dialog | 明示“不会保存／发送” | 未来捕获需单独 runtime 任务、授权与耐久回执 |

## 3. 健康／健身失败关闭

| 输入状态 | 页面允许内容 | 明确禁止 |
|---|---|---|
| 未回答 | 休息、记录状态、跳过说明 | 训练型建议、诊断、保证 |
| 跳过 | 保守降级说明 | 把跳过解释为无风险 |
| 警示 | 停止建议、适当专业支持提示 | 伤病判断、治疗建议 |
| 缺失／过期／冲突／失权 | 缺口／冲突状态 | 个性化、可靠或训练型建议 |
| 无警示 | 低强度、非冲击、可随时停止的选项 | 跳跃／跑步建议、处方或医学结论 |

## 4. 可访问性、响应式与 motion

- 页面具有 skip link、语义化 `nav`／`main`／`section`／`dialog`、可见键盘焦点和 `aria-live` 回执。
- `Tab` / `Shift+Tab` 可到达主要操作，`Enter` 激活按钮，`Escape` 关闭详情与捕获说明 Dialog。
- 1280×1024、1160×768、700×760 是原型验证 viewport；窄屏依次堆叠重点卡，关键按钮不依赖 hover。
- `prefers-reduced-motion: reduce` 会移除位移和长动画；“低动态预览”仅用于让该合同可被实际操作验证，不声称修改操作系统设置。

## 5. Future runtime 对接边界

未来 runtime 只能在独立任务、独立授权和独立 ABF 下决定：真实 Source／Artifact 持久化、Answer／Feedback／EXE／RES 事件写入、版本与撤销链、Memory candidate 的确认和跨日作用、健康高风险分流、权限／时效检查、审计、模型调用或任何外部能力。本原型不预授权其中任一能力。
