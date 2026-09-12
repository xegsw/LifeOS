# P3-155 正常安全切换增量

状态：ABF-09切换工程证据完成，等待用户ABF-10及最小视觉验收；任务未Complete。Codex专项，L3；独立评审继续暂停，不是Independent Pass。PM依据D-0656与engineering_gate_review明确批准从检查点接续，不新增真实权限。

## 非内容事实

旧P3-154完整包全部文件摘要匹配，精确运行身份为PID67899、bundle `local.lifeos.p3-154.c1-flow`。正常退出回执为normal_quit_requested=true、exited=true，没有强杀或删除锁。

新App：`/private/tmp/lifeos-p3-155-source-update-v1/LifeOS P3-155 Source Update.app`。
Binary：`Contents/MacOS/lifeos-p3-152`；SHA-256 `8716005747edc7d0fb21df7a816c0cf10684fb110b9b48e9fad29b984a1eb14c`。166文件完整candidate与已固定打包清单一致。

只创建一次launch claim并启动一次，PID74377，固定回执controlled_conversation_started、running=true，随后激活请求成功。切换后精确两包身份检查仅见新PID74377。PID仅描述收据时间，不保证未来持续在线。容量/环境恢复消息到达时检查了既有claim与执行结果，没有再次启动。

没有自动刷新、导入、模型发送或测试/models，没有读取真实正文、DB内容、Key、AX、截图、真实内容日志或内容hash。构建/包文件hash属于代码身份。旧App包、真实数据及凭据保留，没有迁移、重置或清理。

## 历史与检查点

原315文件工程包、原报告、FINAL_MANIFEST及原checkpoint均原文保留；旧verifier中的realSwitched=false/visualPass=false仍是当时工程状态，不作为本次启动证据。本次独立增量位于`lifeos/engineering/LIFEOS-P3-155/real-switch/`，包含parent-snapshot、切换前checkpoint副本、新checkpoint、一次claim、正常退出/启动/激活/身份回执及独立Manifest/verifier。

当前权威恢复点为该增量`checkpoint.json`，resume_from=`user_minimal_source_health_validation`。已通过208回归、13mutation及无关视觉阶段不重跑。禁止边界接触No。

## 最短用户操作（由PM收口）

1. 打开 **设置 → 数据与隐私**，确认“本地资料”和“苹果健康文件”区域文字、按钮可见，页面可滚动；点击“刷新来源”，查看实际完成或固定错误码。
2. 点击 **导入苹果健康文件 → 导出.zip**。结束后再选同一文件一次，确认提示“此文件已导入，未重复写入”。不选择其他路径、不改原件。
3. 来源处理中可点“暂停处理”，正常退出并重开同一P3-155 App，确认状态保留且未自动继续，再点“继续处理”。若刷新已结束，只需正常重启核对结果保持，不必人为制造故障。
4. 用自己的问题验证仍有效资料可用于后续对话；阅读披露后亲自确认实际发送。

只需回复全部通过，或哪一步的固定错误码；不提供正文、回答、Key或截图。未把“开始下一任务”记录成通过，也未启动156。

## 待决事项

ABF-09有非内容切换证据；ABF-10及纯视觉属性仍待用户直接使用结果。P0=0/P1=0/P2=0/Unknown=2/Not Implemented=0（视觉与真实结果待验收，已执行切换）。PM负责最终验收与账本；本增量不关闭风险、不冻结、不推进Stage、不提交推送或自动合并。
