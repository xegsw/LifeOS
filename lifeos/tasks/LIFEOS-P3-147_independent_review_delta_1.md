# P3-147 独立安全 Delta 1 派工补充

2026-09-08，PM接收同合同工程Closure并核对新包613项完整性/证据关联通过。此为原ABF的候选版本和可恢复执行补充，不覆盖原ABF或原Rework，不关闭风险、不批准真实Gate。

新固定候选仓库 `/Users/xxe/.codex/worktrees/b3f6/No.2`，commit `801e478a5bf0c62a87d740c68a765fc219e81406`。范围仍为原ABF M01–M12、原25IPC与原精确独立评审临时根。工程报告、FINAL_MANIFEST、design/artifact-safety-closure.md及evidence/artifact-closure-diff.json均从该commit读取。65项本轮+29历史=94项工程组合，另2复现；不是独立测试结果。

允许原独立评审会话继续，独立性未污染，不重新开工程任务。先在自身 `lifeos/reviews/LIFEOS-P3-147/independent-review/delta-1/` 封存delta测试计划和写入清单，再接触新候选。原review/结果/Manifest/失败反例只读保全。唯一既有 `/private/tmp/lifeos-p3-147-independent-review-v1` 不改名、不清理，先核对原marker及已知writer退出；其余真实/工程运行根完全禁止接触。

新源码、编译缓存、App、DB和合成夹具必须与旧版本隔离；首选同根新delta子目录。若固定runner必需work/candidate等路径，先按逐文件hash把旧work/DB/artifacts及相关夹具隔离保存到同根独立history子目录，验证保全后才创建新版本运行布局，不覆盖/删除旧物，不把旧DB/PID/App/截图用作新Evidence。无法安全隔离则先报告PM，不删除marker或放宽根合同。采用独立profile，禁止工程profile。

必做：M01/M12对新固定候选重取；M02/M04重新执行原公共IPC正常/链接反例，覆盖Web/local输出目录与文件、祖先替换竞态、staging/parser/发布/recovery，哨兵内容及权限不变且失败无fetched。再完成之前未执行M03/M05/M06/M07/M08/M09/M10/M11八行，不将“未完成”误计为新缺陷。M10至少四独立语义mutation，副本基准恢复；M11用新binary fresh direct PID链，不能借工程截图。原文档允许的资源监控限制如实报告，不突然引入未约定OS硬沙箱验收。

产物写delta-1独立报告、矩阵、自编测试、前后hash、checkpoint、非自指Manifest。有效旧证据只说明可继承事项；候选安全缺陷未关闭不能Pass。环境故障checkpoint续跑，不全量重做。停止自有writer，保留marker根，不自动清理；不得访问真实数据/网络/Keychain、推送、合并或更新PM账本。最终提交给PM用于判断，不自授真实能力。
