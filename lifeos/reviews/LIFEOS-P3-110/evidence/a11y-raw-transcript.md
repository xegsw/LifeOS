# P3-110 当前实际 app 的 AX 结果摘录

来源：本次隔离 wrapper 的 `@oai/sky` 实际操作返回；以下为操作时的原始关键行摘录。

```text
Tab 后：
The focused UI element is 3 link 跳到主要内容, Value: tauri://localhost/restricted-offline.html#main-content

Enter 后：
50 scroll bar (settable, float) 0.1957774
The focused UI element is 16 container

700×760 受限页滚动后：
50 scroll bar (settable, float) 1
44 container 固定非敏感快速捕获
49 button 明确保存固定非敏感文本
```

解释：该摘录只陈述已发生的 Tab、Enter、skip-link、main-content 焦点与滚动位置；未把 AX 暴露当作未发生的动作证据。
