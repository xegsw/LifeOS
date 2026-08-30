# LIFEOS-P3-141 模型设置基线纠正 PM Review

## 结论

**Closure Cycle — 撤回D-0620当前正向效力，Phase C暂停。**

历史独立评审在ABF-v2范围内真实通过，不追溯改写；但ABF-v2本身遗漏了用户已明确确认的凭据持久化要求，并错误合并Cloud DeepSeek／Kimi可见选项，因此不能继续作为真实Phase C准入依据。

## 当前缺口

| ID | 事实 | 严重级别 | 处理 |
|---|---|---|---|
| CL-MS-01 | 当前UI把DeepSeek／Kimi合并在Custom文案中，不是Cloud独立Provider选项 | P0 | 按MODEL_SETTINGS_BASELINE_V1恢复五个Cloud可见选项 |
| CL-MS-02 | 当前API Key仅会话内存，关闭App删除；未加密写入本地DB、不可跨重启 | P0 | 实现密文持久化、更新、删除、重启及明文排除 |

## 五类计数

- P0：2
- P1：0
- P2：0
- Unknown：0
- Not Implemented：2

## 边界

- P3-141保持同一活动任务，Revision 3与ABF-v3由用户本次明确确认。
- Pilot-6、真实DB／文本／Health、真实Provider／凭据／网络继续暂停且不得探测。
- R-0056保持Open；不冻结产品实现、不关闭风险、不进入Stage4。
