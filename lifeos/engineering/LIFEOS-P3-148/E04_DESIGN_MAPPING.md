# E04 视觉恢复：实施前差异映射

范围：同一 P3-148 工程增量；2026-09-08。此文在 E04 UI 修改前形成并交 PM，不是新的冻结或独立 Pass。

精确输入路径与完整 SHA-256 见 `contract-inputs/E04-visual-bindings.json`。P3-142 任务卡 hash 与 PM 指定一致；Delta1 REPORT 与 FINAL_MANIFEST 两个 hash 均与任务卡一致。Delta1 仅覆盖此前候选，旧顶层 Not Pass 和 387 项工程包由 `history/pre-E04-package.zip` 保全。新视觉补充单独保存在 `contract-inputs/E04-visual-task-card.md`，不覆盖先前 E04 输入。

| 部位 | 只读设计依据 | 当前 148 偏差 | 同范围恢复 |
|---|---|---|---|
| Shell/Rail | 116 styles.css 的 app-shell/icon-rail；app.js icon/navButton | 80px Rail、Unicode 图形；整体继承 142 紫色 | 直接复用 116 SVG 和 92px Rail、52px 按钮，Settings 底部弱入口；四个主导航保留 |
| 色彩/文字 | 116 :root、page-wrap、page-head | 紫色 #615cff 和密集配置卡替代个人首页 | 全局 #176df5、#101a31、#f7f9fd、SF Pro Text、20px 圆角、原留白/日期层级 |
| Today | 116 todayPage / today-grid | 全屏对话卡墙取代 Today | 恢复问候、双列卡片与安静空状态；已有有效记录按当前快照展示，不复制原型健康/工作假数据 |
| Global AI | 116 composer / aiPanel / Escape | 大型固定输入卡；确认时输入消失；对话占首页 | 紧凑底栏打开同一右侧对话面板，当前上下文仍在后面；面板内答案/来源、紧凑确认和稳定输入；Escape 可关闭 |
| 确认 | E04 明确逐次确认 | 全量预算/正文默认展开；按钮“确认并发送（合成）” | 默认准确一句 N 段笔记/M 条纠正、Provider/模型；“查看发送内容”展开精确 body 内容；“确认发送”一次触发，保留合成未联网标记 |
| Settings | 142 secondaryNav/serviceCard/configForm/routing/advanced | 巨型 DeepSeek 控制卡 + 两列完整目录，无二级导航 | 恢复二级导航、一个主服务、分组目录、能力状态和低权重高级设置；真实行为仍由当前 148 DTO 控制 |
| 窄屏/输入 | 116 响应式 + E04 U05 | 重绘替换 textarea；隐藏输入和大底部占位 | 700×760 内面板和页内容宽度有下限；复用同一输入节点并保留选择区；确认、末尾和输入均可达 |

冲突及处理：

- 116 原型无持久化/示例行为不作为运行语义。E04 自动恢复固定 source-chat 取代原手动打开；不增加数据库创建、扫描、OS 凭据恢复或自动联网。
- 116 全局蓝色 Shell 与 142 紫色 Settings 局部不同。整体按 116，模型设置内部保留 142 结构与局部色彩；不以 116 覆盖已确认的 Settings。
- 142 原型中所有 Provider 的模拟成功、假 Key、路由策略和高级参数不复制为实际能力。8 云/4 本地目录保持，当前仅 DeepSeek 获准；自动 fallback/云端补充关闭，不制造可用开关或假成功。
- 116 快速记录、示例候选和工作区行为不能以假按钮替代当前功能；本次保留当前 148 的来源、检索、长期信息与反馈入口，不扩大 IPC 或赋予未实现的行为。
- 原 116 窄屏 composer 左偏移与 Rail 可能交叠，只按 U05 修正边界；不改系统缩放。验证记录实际原生尺寸，不把逻辑尺寸当截图尺寸。

后续验证：U01–U06 应用流程测试、既有四项 P1 必要回归、离线构建、桌面与 700×760 合成 actual Tauri、同尺寸纯合成设计对照。尚未实施/验证的结果保持 Pending；最终统一提交 E04 包供 PM 安排差异复核与用户验收。
