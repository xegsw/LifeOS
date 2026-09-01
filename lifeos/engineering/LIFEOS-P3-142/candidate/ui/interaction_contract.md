# P3-141 交互合同

## 边界

- 所有文字、对象、来源与状态均为固定、非敏感 synthetic fixture。
- 原型只有浏览器内存态。关闭或刷新会回到初始状态；这不是持久化恢复。
- Quick Capture 先展示用户原文，再展示可忽略的 Domain／Context 建议；确认只产生演示回执，不创建真实对象。
- Global AI 与 Settings 通过固定的本地 Tauri IPC 调用受控 Runtime；UI 不直接拥有网络、文件、DB、Shell、进程或凭据持久化能力。
- Provider 设置保存非敏感配置；Cloud API Key 只会在用户明确保存时以密文写入受控本地 SQLite。密钥材料与数据库分离，凭据跨重启保留、可更新或删除，且绝不回显。
- 合成构建中的连接测试只验证受控 fixture 合同，不打开真实网络；真实模式在独立评审前失败关闭。

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
| Provider 设置 | 从弱 Settings 入口选择 Local／Cloud 与对应 profile → 保存配置 → 明确保存、更新或删除 Cloud API Key → 测试 → 选择 → 启用 | API Key 以密文保存在受控本地 SQLite，跨重启仍可用；配置或凭据变化会撤销启用；只允许刚刚成功测试且未变更的配置启用 | 用户逐次决定保存、凭据、测试、选择、启用与停用；凭据不通过进程环境提供、后台连接或隐式重试 |
| 显式理解请求 | 在右侧 Global AI 面板点击“请求当前 Context 的理解” | 显示当前 Provider、model 与 Context 范围；输出标记为 Observation/Suggestion 与合成 fixture | 不请求不会调用 ModelPort；返回内容不能自动写入 Today 或创建 Action |
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
- 没有远程字体、图片、图标或代码依赖；UI 没有 `fetch`、XHR、WebSocket、Cookie、Storage 或 Service Worker。受控本地 Runtime 的 Provider adapter 只在用户点击测试或发送后执行合同允许的操作。
- 没有“已保存”“真实 AI 已生成”“已执行”“真实健康建议”或“已验证用户价值”的回执。
- Memory 的断链与证据不足状态显式披露，不能成为候选建议依据。
