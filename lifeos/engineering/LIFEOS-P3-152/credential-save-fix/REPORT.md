# P3-152 API Key 保存修复增量

状态：Paused — Resumable；工程修复及合成回归完成，真实保存结果待确认。主责 Codex 工程；PM 验收和独立评审未通过，独立评审继续暂停。此次延续同任务 Closure Cycle，不声明整产品 Complete。

## 事实与修复

旧主按钮仅保存 catalog，随后重绘清空输入的 Key；独立保存按钮在 Host 成功前清空 Key；异常被统一提示吞掉；catalog 已保存可能误显示已有凭据。现主按钮在保存配置后保存非空 DeepSeek Key；独立保存支持空 catalog；收到凭据保存成功后才清空对应输入，失败保留；同页重绘保留密码输入节点，离开凭据页不缓存密码。所有保存动作串行防重复点击，后续 model 步骤失败时刷新凭据 revision，避免下一次继续使用旧 CAS；不自动重试凭据写入。设置页显示实际凭据状态和允许清单中的固定错误码，未知错误不显示原始 payload。

配置与凭据不是原子事务，部分成功会明确提示，后续失败不会撤销已确认保存的凭据。Catalog 保存失败时 Key 不提交且输入保留。Key 保存成功但后续模型失败时提示已保存与后续错误。未改变后端生产凭据实现。

## 验证

- Rust Host 67/67；新增 source-engine-v1 子目录与 provider 文件 allowlist 合成验证、Keychain 失败固定码映射。
- UI 逻辑 26/26（新增 9）：主保存、独立保存、空模型、部分失败、CAS 刷新、重复点击、用户新输入保留、敏感错误屏蔽、真实凭据状态显示。
- Host 集成 14/14（新增 2）：实际合成 DTO/Host 保存及 CAS 失败后手动重试。
- 组合回归 11/11。总计 118 项；日志在 evidence/。
- 1292 项历史 Manifest 文件 hash 保持一致。候选新增 2、修改 8、删除 0；详情 evidence/candidate-diff.json。Rust 2 个文件仅新增测试。

上述不包含当前真实 Keychain 操作，也不把逻辑测试视为修正版 actual-Tauri GUI 证据。真实根兼容测试使用任务自有合成临时目录，无真实目录内容接触。Mac 解锁状态本轮未检查，因为当前真实窗口禁止 Agent AX/截图。

## 交付

修正版：`/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Credential Fix.app`，尚未启动。二进制 SHA256 `7f61c4919ec6728d806322221f34c0c83bcf723365c0563d9d879f4f34b01ccf`。当前真实 App 未关闭或覆盖，草稿与凭据未被 Agent 操作。

checkpoint.json 的 resume_from 为 pm_safe_switch_then_manual_credential_save。需要 PM 安排安全切换及用户手动确认真实保存；无需提供 Key 正文。若仍失败，仅需修正版显示的固定错误码。未确认当前真实失败是否还有系统钥匙串原因，不能认定真实问题已全部关闭。

工程增量目录为本报告同目录，复跑 tools/rerun.sh，校验 tools/verify_package.py。无 commit/push、无新权限、无风险关闭或阶段切换。
