# P3-157 Closure-1 修正设计

2026-09-10，Partial / 设计待PM裁定；L3，Codex原工程会话。用户实际ABF08未通过；不修改上一交付的报告/Manifest/checkpoint，不切换当前真实App。独立评审继续暂停。

已用原交付的真实Domain/Application JS和无IO合成Repository double完成7例复现，其中2个缺口成立：未列入动词表的明确安排，以及不匹配固定后缀的明确撤销，均返回undefined并进入普通AI披露，action_event=0。另5例为支持创建/固定取消/否定/引用/歧义对照。未读取用户原话、截图、真实DB、Key或重发请求；不能宣称掌握用户具体记录状态。

修正建议是四类分流：普通聊天、明确但未支持、歧义、支持的行动。只有普通聊天可进入AI披露；未支持须明确未写入并保留草稿，歧义只问一个必要问题，成功状态必须来自本地事务回执。解析改以明确第一人称意图句式承接事项原文，避免逐词补白名单；撤销须有有限撤销句式及既有planned事项精确唯一匹配，区别否定新意图、词内“不”、无目标、多目标和终态。不增加云端解析或任务按钮。

当前仅设计，尚未实施。wire v6/字段/14命令/物理Schema不需改变；但确认语义从动词表/固定后缀扩展为意图槽位及事项匹配，需要PM明确裁定范围，不能用“字段没变”掩盖语义变化。安全下限的本地未写入提示不扩展写权限，但不能仅做该下限便宣称Closure完成。

完整方案：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-157/closure-1/design/minimal-correction.md。

7例实际复现：closure-1/evidence/reproduction.json；入口closure-1/tools/reproduce.mjs。

24例修正验收设计：closure-1/design/acceptance-cases.json，尚未执行，不计为通过。

恢复点：closure-1/checkpoint.json，approved_correction_implementation。原241项交付及报告hash在history-snapshot保全；当前真实运行实例未触碰。

工程自评为一个P1级确认/持久化反馈缺口的两个表现，最终严重级别由PM裁定；无证据表明真实数据已被改坏。需PM决定该明确语义delta及后续实现边界；ABF08仍未通过，真实切换暂不进行，不启动后继。
