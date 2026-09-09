# E03 独立合成执行配置

PM任务卡顶部E03授权已另存contract-inputs/E03-task-card.md及E03-sha256.json。旧346项Manifest、检查点、报告及完整candidate ZIP保存在history/pre-E03-*；原设计/E01/E02与GUI历史不改。

新增编译期independent-review，只对应任务卡字面评审根，marker文件.lifeos-p3-148-owner.json，owner=LIFEOS-P3-148-independent-review，schema=lifeos.p3-148.independent-review.root.v1；marker完整对象由root_profiles.json指定。工程未对评审根做exists/stat/read/create/hash或运行夹具。所有编译缓存和纯测试可执行文件均位于既有工程根。

## 模式检查

真实判定唯一是runtime_root::is_real()的编译常量等于source-pilot-1。没有profile非engineering就启用真实能力的分支，故无需改业务模式分派。两合成配置均经相同SyntheticKeyPort和SyntheticModel：provider_store的解密/加密/删除/models、conversation_store的发送选择均显式先判断is_real；provider_transport::call在进程启动前拒绝非真实模式。main的真实窗口/诊断及stdio限制也用同一判断。repository使用本profile根下合成数据库；runtime_root的source_path、helper、marker和子目录随编译根；source_file限定fixtures下来源，source_worker将来源ID映射至该根fixtures。source_api的合成目标分支保持原模拟实现。工程与真实两个既有profile对象逐字值相同。

## 定向验证

见evidence/e03-20260908T105845Z-result.json及其6份日志。两个profile分别离线build通过，各2项新E03纯配置/模拟端口测试，加1项既有环境不能开启transport测试，共每profile3项。各自--profile-info正常纯常量返回；8项运行环境覆盖（未知/其他合成/真实build profile、real模式、4种root覆盖）均退出2/profile_rejected。未知配置纯select拒绝。未运行整套旧测试、GUI、数据库夹具或真实profile。review profile测试只计算常量/内存模拟/拒绝路径，没有调用根验证或文件系统入口。

两份Rust改动仅在原完整文件后追加cfg(test)模块；其余生产差异仅root_profile.rs允许第三个名称、root_profiles.json新增一个固定对象。原业务和UI字节不变。evidence/E03-lineage.json保存精确前后候选与二进制摘要；先编译评审profile，再恢复工程profile二进制。评审须在自己的新根从该候选重新构建、自建夹具/PID/证据，不复用工程缓存二进制、DB、GUI或测试结论。继承工具中标为147的旧runner/复制脚本不作为148独立评审入口。

原GUI绑定E03前二进制，未宣称当前E03二进制已跑GUI；PM明确不重跑无关GUI，按配置变更谱系继承业务证据。此为工程增量通过，不是独立评审Pass、PM验收或真实亲验。
