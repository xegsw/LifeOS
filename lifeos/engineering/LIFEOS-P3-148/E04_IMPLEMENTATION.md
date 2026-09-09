# E04 工程交付：自动恢复、自然对话与视觉恢复

2026-09-08，Codex专项工程，L3，同一 P3-148。E04 工程增量完成，待 PM 安排受影响差异复核及统一用户验收。不是新的独立 Pass、真实安全 Gate 或产品冻结。

## 结果与实现

- `application/conversation_flow.ts` 负责启动恢复、串行草稿保存、准备/确认状态与失效处理。启动仅调用现有 open_conversation，再读会话/配置/已有投影；原 backend/Raw DTO/Root/凭据/Transport 均未改。启动失败保留输入，单一显式重试，不后台循环。
- `application/source_ui.ts` 直接底栏输入，“发送”只本地保存/准备，然后自动展开右侧同一对话。“确认发送”前重新读取当前 packet 并交后端验证。编辑、移除、过期、取消/撤权后旧确认不可继续；无自动重发或 fallback。
- 确认默认只展示实际 N 段笔记、M 条纠正、DeepSeek/模型。展开包含原样转义后的问题、片段、纠正、固定说明和实际 JSON。无匹配不提供确认发送。
- 答案和引用直接显示，反馈折叠且可选。来源/长期信息/Settings 入口保留。输入节点跨重绘/Settings复用，选区保持；Enter 准备，Shift+Enter 换行，Escape 关闭面板。
- `ui/design116.css` 是指定116 CSS字节级复制；SVG从指定116 app.js取得。Today使用当前有效状态或诚实空态，不生成Focus/健康结论。Settings保留142二级导航、主要服务、配置/能力/低权重高级结构，8云/4本地目录及148加密持久语义保持。局部能力行挤成竖排问题已修正，早期截图保留为修正历史。

## U01–U06 验收增量矩阵（工程覆盖）

| 行 | Evidence | 结果及界限 |
|---|---|---|
| U01 自动恢复/失败重试/幂等 | E04-flow-01.log 前2项；app-e04narrowrestart2.json；app-e04desktopfinalstart3.json | 9项流程测试中覆盖一次启动、延迟恢复不覆盖新输入、显式失败重试；actual跨PID恢复草稿/对话。启动故障为mock repository验证，不冒充live故障注入 |
| U02 准备→一次确认→回答 | E04-flow-01.log；app-e04desktopfinalpreview3/answer3；app-e04narrowconfirmedkeyboard2/answer2 | 准备无发送、重复确认一次、未知结果不重发；actual两尺寸准备及回答，derivations只在确认后新增 |
| U03 精确披露和旧确认失效 | E04-disclosure-01.log；E04-flow-01.log；app-e04narrowdisclosure2；E04-edit-invalidated.json | 实际渲染函数验证完整转义内容与JSON/类别数量、默认折叠；mock移除/过期/撤权；actual编辑立即取消确认；后端旧四P1验证引用/幂等边界 |
| U04 回答/来源/可选反馈 | app-e04narrowanswer2；app-e04desktopfinalanswer3；继承此前IR正常引用/反馈证据 | 答案直接显示，C1和可选反馈可达；发送不要求反馈；来源取证链后端未修改 |
| U05 桌面/700×760/键盘/草稿光标 | E04-desktop-controls.json；E04-narrow-controls.json；E04-caret-before/after.json；app-e04desktopescape3；E04-visual-comparison.html | 原生按钮和输入框有界且不重叠；文本及选区位置9完全一致；CUA Return真实准备、Left移动光标、Escape关闭已观察。自写CG按键投递无效果不作为键盘Pass |
| U06 启动零OS/网络/扫描、Settings及旧P1 | E04-passive-01.log（1项）；E04-ir-regression-01.log（5项）；E04-flow-01.log最后1项；E04-verifier-01.json | MockCredentialPort被动读无OS调用；启动repository仅open/read/settings；Rust/Raw DTO/Ports/Root相对原387包逐文件未变；实际运行工程模拟profile，无真实Provider或OS访问 |

## 视觉对照及谱系

`evidence/E04-visual-comparison.html` 包含6对：116 Today/Global AI、142 Settings，分别桌面与窄屏。设计参考为独立WKWebView的纯合成本地文件渲染，CSP禁止网络；142无Runtime桥接，显示其原始未配置视觉态，只证明设计形态。

App原生窗口1280×949、700×760；去标题栏后内容1280×917、700×728，与参考视口一致。对照页仅CSS隐藏标题栏，原图未改；不宣称文案或像素完全相同。116含原型示例与额外演示控件，148按E04用实际数据/空态，未导入假事实或假能力。

最终候选87文件 SHA256 `cd5306dfb828f220aaab135498436d6d76a8bf7c417a042c6c272fad5d1275a0`；二进制 `134ab82cb5cbfa4e922e94d07cfb5e28494080fad60511af71b2a03d186843cd`。最终窄屏PID79996、桌面PID80386使用同一binary。早期PID79815仅作为CSS修正历史，最终取证已更新。所有App已停止；唯一工程合成根保留。

原387项工程包在 `history/pre-E04-package.zip` 逐项hash复算通过。Delta1报告/Manifest摘要与PM固定输入相符，仅继承原有限合成Pass，不覆盖当前E04。旧顶层Not Pass及失败历史不改。早期两张键盘投递无变化图、两张错误AI参考（实际是Today）排除正Evidence，见E04-lineage.json。

## 复跑入口与边界

`python3 -B tools/verify_e04.py` 只读核对历史、指定设计/Delta1摘要、测试记录、源谱系、原生几何/选区、进程停止。`node --test candidate/tools/test_e04_flow.mjs` 运行9项flow测试；`node tools/test_e04_disclosure.mjs` 核对实际披露渲染函数。Rust命令在 evidence/E04-ir-regression-01.log、E04-passive-01.log，使用已批准engineering profile、唯一工程cache、--locked --offline，未重跑无关旧测试或平台排除项。

没有真实根/DB/正文/凭据/Provider网络、评审根触达、历史修改、PM账本修改、push/merge、风险关闭、Frozen或Stage切换。无新的产品/权限决策；下一步由PM处理E04差异复核，最后统一用户验收。真实亲验仍未实施。
