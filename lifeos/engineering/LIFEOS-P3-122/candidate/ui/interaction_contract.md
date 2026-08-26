# P3-116 交互合同

## 边界

- 所有文字、对象、来源与状态均为固定、非敏感 synthetic fixture。
- 原型只有浏览器内存态。关闭或刷新会回到初始状态；这不是持久化恢复。
- Quick Capture 先展示用户原文，再展示可忽略的 Domain／Context 建议；确认只产生演示回执，不创建真实对象。
- Global AI、AI Workspace 和 Future Agent Task 均为界面合同，不调用模型、工具、网络、DB、文件、Tauri 或 IPC。

## 核心流

| 流程 | 操作 | 可观察结果 | 用户权威 |
|---|---|---|---|
| Today → Context | 查看 Focus 的为什么 → 进入 Context → 确认／调整 Next | Focus 最多一项，Evidence 可达，Next 标为用户确认或候选 | Action 只在用户确认后显示演示回执 |
| Today 概览 | 阅读问候、Day Overview、已确认日程与 Recent | 轻量状态、日程和最近记录只作辅助；日程不打开日历，状态不构成评分或建议 | 内容固定合成且非持久化，不改变 Focus 或任何对象 |
| Today 空／不足 | 切换合法空状态或证据不足 → 查看缺口 | 不凑建议，不把未知说成事实 | 用户可自己转向 Context 或 Capture |
| Quick Capture | 点击 Global AI Bar 的 `+` → 打开捕获面板 → 确认或忽略关联 | 捕获与提问是两个明确动作；原文与建议分开 | 忽略不会删除、确认不会持久化 |
| Context 候选 | 查看建议创建 → 确认或拒绝 | Context 是候选，Project 只是类型 | 系统不会静默创建 |
| Memory 追溯 | 浏览身份 → 打开 Detail → Understanding → Derivation → Evidence → Source | 七类身份、来源、确认状态、范围可见 | 可将 Observation 标为准确、不准确或纠正 |
| Global AI | 点击或提交底部 Global AI Bar → 右侧渐进展开 → 查看 Person/Page/Selection → 移除 Health | 底部输入与侧栏是同一个全局 AI 入口；可见使用范围，移除后回答变化 | 提问仅在本次浏览器内存演示中；移除只影响当前临时上下文，不改持久事实 |
| AI Workspace | 从 Global AI 展开 → 检查 Conversation + Work + Inspector | Work + Health 仅表达 Observation/Inference 与依据 | Action／Decision 均为候选，需确认、编辑、拒绝、忽略或纠正 |
| Domain Gate | 尝试启用 Finance | 一次只能一个；数据、价值、反馈、安全 Gate 均可见 | Gate 未满足时保持未启用 |

## 可访问性与运动

- `main` 前有 skip link；主导航和状态切换使用原生 `button`。
- Today、Me、Memory 与 AI Workspace 共用窄 Icon Rail、日期 chrome、可见焦点与底部／工作区 AI 入口；视觉统一不新增一级导航、账户 Profile 或真实日历能力。
- 所有交互控件具备可见 `:focus-visible` 焦点；Tab／Shift+Tab 由原生顺序支持。
- Enter 激活原生按钮；Escape 关闭 Global AI 或对话框并把焦点放回主要内容。
- `prefers-reduced-motion: reduce` 与原型“低动态预览”把位移动画降为近即时淡化；不依赖自动播放的运动表达状态。
- 三个冻结 viewport 使用同一 DOM：1280×1024、1160×768 与 700×760；窄屏把 Grid 堆叠，仍保留 Global AI、主操作与完整标题。

## 明确关闭态

- 没有通知中心、铃铛、宽 Sidebar、左下头像或账户 Profile。
- 没有远程字体、图片、图标或代码依赖；没有 `fetch`、XHR、WebSocket、Cookie、Storage 或 Service Worker。
- 没有“已保存”“真实 AI 已生成”“已执行”“真实健康建议”或“已验证用户价值”的回执。
- Memory 的断链与证据不足状态显式披露，不能成为候选建议依据。
