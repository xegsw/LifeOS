# P3-091 Chrome `file:` 动态操作日志

- 浏览器：Google Chrome (`com.google.Chrome`)；控制面：Computer Use `@oai/sky`。
- task-local 副本：`/private/tmp/lifeos-p3-091-clean-app`；入口：`file:///private/tmp/lifeos-p3-091-clean-app/default-recovery.html`。
- 预检：在新标签页直接加载入口成功；未使用 HTTP、网络、CDP、命令行浏览器、浏览器持久化或策略绕过。
- 默认页：核对四类身份／边界说明；输入固定非敏感文本并明确确认；grant 后准备预览、输入精确 `CONFIRM`，出现仅页面内合成回执；重复 `CONFIRM` 维持幂等。
- 撤回与失败：撤回清理恢复预览与回执；模拟失败清理输入／显示并披露“未保存、未授权、未恢复或处理任何真实内容”。
- 三页：导航至“暂无可靠建议”，确认其拒绝凭痕迹生成建议；导航至“权限受限 · 离线”，确认默认拒绝与不读取／处理内容。
- 刷新：在默认页确认文本后 Chrome 重新加载，显示恢复为“尚未确认”，输入和回执已清除。
- 可访问性／响应式：Chrome AX 树公开 skip link、main、带名称导航、status/live 反馈、输入与按钮；视觉记录含宽屏与缩放后的窄视图。CSS 静态验证覆盖可见焦点与 `prefers-reduced-motion`。
