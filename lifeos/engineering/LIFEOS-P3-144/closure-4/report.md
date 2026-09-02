# LIFEOS-P3-144 Closure-4 工程收口

## 结论

同一任务内已关闭真实使用阶段暴露的四项同范围缺口：DeepSeek 超时误报为网络不可用、成功回答／反馈状态未在 Global AI 原地展示、真实数据库文件名偏离冻结合同、反馈动作可被重复消费。

本工程结论为 `Engineering Pass / Awaiting Independent Delta Review`，不单独构成 PM Pass、用户最终采纳、风险关闭、产品冻结或 Stage 4 准入。

## 变更

- `curl` exit 28 归类为超时，真实请求上限由 30 秒调整为 60 秒；不新增重试或 fallback。
- Global AI 将结果明确显示为“DeepSeek 回答”，关闭重开后通过既有 IPC 恢复最新 Understanding；反馈后原地显示终态并收起反馈按钮。
- 后台反馈状态机改为单次消费；终态只允许显式“纠正”进入失效，重复确认／编辑／拒绝／忽略在写前拒绝。
- Runtime 数据库固定为合同指定的 `capture.sqlite`；旧实际数据库已在 App 停止后无损改名，零字节占位文件改名保全。
- Runtime 拒绝非普通数据库对象，并在初始化时强制 `0600`。

## 验证

- Rust 串行离线回归：26/26 Pass。
- JavaScript 离线合同：23/23 Pass；IPC 恰好 20。
- Pilot-7 离线构建与关闭重开：Pass；重启前后凭据／Understanding／反馈非内容计数一致。
- 活动数据库：`capture.sqlite` 普通文件、`0600`；旧数据库文件名 absent。
- Closure 期间未启动 DeepSeek `curl`，未重放真实请求，未读取真实正文，未清理 Pilot-7、数据库或凭据。

## 计数

- P0：0
- P1：0
- P2：1
- Unknown：0
- Not Implemented：0

P2 为旧 UI 不显示反馈已消费造成的重复反馈历史。历史未删除或改写；当前 UI 与后台单次消费保护均已补齐。

## Evidence

- `lifeos/engineering/LIFEOS-P3-144/closure-4/evidence/validation.json`
- `lifeos/reviews/LIFEOS-P3-144/real-use/real-use-receipt.json`

