# P3-158 B首回合失败与错误展示修复

状态：Partial，同任务修正，模型截断未解决；无需重新输入Key。Host持久错误为provider_response_truncated；前端对已失败回合重新准备时缺少终态分支，误报dto_rejected。已保留原错误并阻止终态生成新预览，不自动重发。

生产前端回执20项、实际IPC7项通过，online-synthetic离线构建及完整同身份签名通过。正常替换旧B包后，PID17869实际App显示“模型输出达到限额，响应不完整，未更改安排”，失败草稿保留。检查后新预算仍turn1/query0/model1，旧B14/40保持；零查询、零本回合Action。未提高1024输出额度、换模型、修改ACL/信任或访问157/C。

证据：lifeos/engineering/LIFEOS-P3-158/evidence/D0672-B-terminal-result.json；构建身份D0672-B-terminal-build-identity.json；检查D0672-B-terminal-error-checks.log；启动D0672-B-terminal-launch.json。相对前包仅application/controlled_conversation.ts及其生成JS改变；其余测试继承。不把错误展示修复当作真实模型语义通过，模型截断的具体原因和修复仍待后续定位。

包：/private/tmp/lifeos-p3-158-main-chain-v1/build/signing-v1/D0672-B-terminal/LifeOS P3-158 Online Test.app。PM已获失败预算与修复进度；后续候选与预算以此增量为准，原已见失败不改写，不重新定义为未见样本。
