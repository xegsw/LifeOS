# P3-158 自然对话主链修复：当前交付状态

D-0668 最新方案：[通用查询与行动协调差异](LIFEOS-P3-158_D0668_general_query_coordination_delta.md)，取代此前天气专用前向方案；仅方案，未启用新工具/网络/多轮调用。D-0667凭据修复结果不变。

状态：Partial / B Paused — Resumable；L3。A 离线工程已验证，B 部分开发用例通过，C 未开始。需要 PM 决策；尚未 PM Pass、Independent Pass 或 Complete。

完整 174 文件基线累计至 176 文件候选，生产对话通过 v7 ModelPort 候选与 Host 事务回执完成本地操作。历史、来源、Settings 和既有状态功能保留。A 使用合成模型，不能外推真实模型语义能力。

B 已验证明确创建/调整/完成/取消、省略目标的取消、必要澄清及正常重启持久化。共消费开发14/24、未见0/16、总14/40，含失败；共有7条行动事件。剩余语义覆盖及未见集未完成。旧失败详细原因保持 Unknown，英文澄清缺陷已修提示但不能仅以离线测试宣称真实体验全部通过。条件句返回 none 仅表示无行动误写，不满足实际天气查询与条件判断体验。

D-0667 已修复凭据等待后的发送前复核，32项操作链测试、9项实际IPC/生产Flow测试通过，离线与在线模式均离线构建成功。五分钟TTL、预算及逐次用户云端确认保持；无凭据缓存或ACL修改。新源码尚未替换当前运行App，B发送仍暂停。

完整增量说明与精确待决选项：
[LIFEOS-P3-158_D0667_credential_wait_and_weather_delta.md](LIFEOS-P3-158_D0667_credential_wait_and_weather_delta.md)。签名打包工具已具备默认dry-run和缺身份拒绝路径；真实持久签名及钥匙串体验尚未验证。天气仅提出Source/Model/Host最小差异，未实施接口或定位调用。

工程与证据：`../engineering/LIFEOS-P3-158/`。A历史见 `stage-A/` 与 `evidence/A-stage-manifest.json`；本次见 `evidence/D0667-manifest.json`；逐步历史报告完整保留于 `evidence/main-report-before-D0667.md`，其中旧预算/状态均为当时检查点，不代表当前结论。

主责角色为Codex工程执行和自检；PM负责最终验收、签名输入及天气能力差异合同。独立评审依用户决定暂停。P3-157真实验收未通过事实保留，旧真实App不操作；C不读取、不切换。没有新建任务、改冻结、关闭风险或进入新Stage。

检查点：`../engineering/LIFEOS-P3-158/checkpoint.json`。恢复点为持久签名身份输入及受控包验证，之后评估B恢复；不用重新跑未受影响的A历史验证。预算跨重启保持，本轮没有触及禁止边界或新增网络请求。
