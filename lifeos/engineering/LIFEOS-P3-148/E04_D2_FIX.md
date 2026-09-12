# IR-D2-001 同包修复

2026-09-08；工程修复完成，等待独立差异验证。PM明确授权原任务窄修；GUI环境暂停不作为候选缺陷，不重做无关GUI。

缺陷事实：旧start每次重试重新截取当前serial。第一次open失败，用户随后输入新草稿，重试返回旧pendingDraft时两者serial相等，导致覆盖新输入。原测试只返回空恢复对象，遗漏该反例。

修复：恢复内容仅在本Flow从未发生用户编辑（serial===0）时采用。只要发生过编辑，无论是在首次打开前、打开过程中或多次失败之间，都保留当前草稿，包括用户主动清空；恢复成功后保存保留的草稿。没有编辑时首次成功或多次重试成功仍正常恢复旧草稿。

仅候选application/conversation_flow.ts及对应生成ui/conversation_flow.js两文件变化，其余85文件不变。无UI布局、业务存储、Raw DTO、凭据、权限或根配置变更。

新增tools/test_e04_retry.mjs五项反例：失败→编辑→返回旧pendingDraft；多次失败/编辑/主动清空；首次无编辑恢复；多次失败无编辑恢复；首次调用前已有输入。旧版2通过/3失败，修复后5通过；加原9项flow回归共14通过，离线locked构建通过。日志evidence/E04-D2-retry-before.log、E04-D2-retry-after.log、E04-D2-build.log。读review仅限指定INTERIM.md，路径/hash见E04-D2-fix-lineage.json。

原486包/Manifest/报告已完整保存在history/pre-E04-D2-fix-package.zip，不覆盖旧失败历史。现有E04图仅作为未改UI的继承证据，不宣称新binary已重跑GUI。原工程核验器已明确接受恰好这两项受测差异，仍拒绝其他候选漂移。

新候选87文件SHA256：80f982969a2f49fe96f25672ee1a34470fa88f058f1666d7836edc8f88038d7a；新binary：a436c5b70f1ec576491ef9a6d21837586a869b4dcc73b11553cb02811026549d。全部本任务App保持停止，未访问评审root或真实根/DB/OS凭据/网络，无push/merge或账本修改。需PM将修复交原独立评审作delta验证；不是Independent Pass或真实Gate。
