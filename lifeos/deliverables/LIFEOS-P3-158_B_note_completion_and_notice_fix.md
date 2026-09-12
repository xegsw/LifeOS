# P3-158 B公开笔记终局核验及提示修正

状态：Partial。一个公开合成笔记v8回合通过核验，不是整个B/任务Pass。

只读核验当前online-synthetic记录：turn2 committed，modelCalls2、queryCalls1；第一许可消费1789040277310，查询完成1789040283249，第二许可消费1789040372056，终局1789040377097（Unix毫秒）。这些是Host许可消费时间，非独立捕获的鼠标点击时间；工程未代点发送。第二披露queryResults与持久查询结果完全相等，query/source/fact refs及版本一致；第二许可在查询完成之后消费、有效期内提交。两条中文回答均来自note fixture的两条结果，非猜测查询成功。最终result={kind:none,businessChanged:false}，该operation的Action事件数0。精确非秘密审核收据：evidence/D0672-B-note-completion-audit.json。

旧“已读取公开合成资料，请核对发送内容”是Flow.notice在第二次确认开始及终局未清理。已在发送状态入口清空旧notice；需要二次确认/暂停/取消时仍显示对应新提示。没有修改历史业务或再次发送。实际IPC二阶段测试新增“二次确认前有提示、成功后notice为空且preview=null”的断言；7 IPC、20回执及flow-races受影响组全通过。检查evidence/D0672-B-notice-checks.log。

修正已离线构建、同身份严格签名并正常替换旧B实例；PID18897，D0672-B-notice完整包。恢复后原回答保留，过时提示消失，AX/截图为evidence/D0672-B-notice-before/after。此重启截图证明当前显示；不重启的状态转换由实际生产Flow/IPC回归证明，不冒充又发了一次真实模型。新构建身份D0672-B-notice-build-identity.json，相对compact候选仅controlled_conversation.ts及生成JS两项修改。

累计新开发turn2/8、query1/8、model3/16；其中首次真实length失败1模型保留，不改成成功、不退额度。旧B14/40及未见0保持。本次修正新增模型/查询0。此前截断未在本回合复现，但不能据一例断言已消除。下一步：继续B开发的另一能力案例，仍仅公开合成资料，必要预览交用户亲点；不盲重发已完成笔记。C/真实接口/旧157未触及。
