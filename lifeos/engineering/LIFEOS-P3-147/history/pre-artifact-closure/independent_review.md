# P3-147 合成独立安全评审

- 结论：**Rework — Candidate P0**，同任务交 PM Closure Cycle。评审停止有效，不是环境暂停，也不是评审尝试失效。
- 风险：L3 / 强制安全 Gate；主责 AI 信任与安全，协审数据/来源、技术架构及体验视角。
- 固定候选：b3f6/No.2 commit `640ebb6fe8d87398a05940b30f1263dad157dfa0`；candidate SHA256 `23349765174036d834261311232915dd1705431159e5dbeda1e1fbbaf2678d89`。
- ABF：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-147_synthetic_independent_review_ABF.md`，SHA256 `7629e457abd84fc8d94e20e61277d60277590c90ef39470e4df6ddc8d331d9f9`。同目录完整任务卡SHA256 `6cfcd9c5c53fd91a847b003262f9b39b057c5cc4d65b268d050a0aef348e4e06`。
- 执行授权：PM投递完整任务路径和本次合成独立安全评审派工；全新隔离7fdc会话，未转派。

## 核心事实

独立 runner 使用未修改候选源码新构建的 `independent-review` binary，先执行正常对照，再将目标原件子目录替换为指向评审根内合成哨兵目录的符号链接。正常对照成功；链接反例没有失败关闭。

**IR-P0-147-001：外部目标原件目录跟随符号链接，发生目标目录外写入。**

候选 `candidate/src/source_targets.rs:149–157` 拼出 `artifacts/target-<fixture hash>` 后调用 `create_dir_all` 和 `set_permissions`，未检查该子目录是否为符号链接；后续文件创建也会沿祖先链接进入目标。`runtime_root::verify()`只验证顶层 artifacts，不能阻止这一层链接替换。

动态复现使用公共五IPC中的连接、状态、目标授权入口及其生产worker，无测试挂钩、无产品源码改动、无工程测试导入：

1. 连接自编合成 Markdown 中的直接引用 `https://synthetic.invalid/article`。
2. 对照fixture `ir-target-control` 正常获取，哨兵目录0750及canary不变。
3. 反例fixture `ir-target-link` 在授权前放置 `artifacts/target-<hash>` → `ir-target-link-sentinel` 链接；两者均位于唯一授权评审临时根内。
4. 授权目标后，哨兵目录从0750变为0700，新增 `target-1f377adff16b2d3ce0a2dae20be0033f-1`，状态仍为 `fetched`。
5. 原canary内容未变化；新原件SHA256为 `e672f371cd1bc5789371d7c0bec0cb3b7365bd75d259027858f632fb2534fc7e`。实际before/after、IPC请求/回复及PID保存在 `target-boundary-results.json`。

这是 ABF M02/M04 的授权文件写入边界违反，合并计一个P0。攻击模拟目录位于授权根内，因此本次实际没有接触真实或禁止路径。对根外真实目标的影响属于同一缺失检查所带来的风险推断，本评审没有向真实目标验证。URL由候选注入Transport处理，未产生真实HTTP/DNS/socket。

## 独立性及已完成验证

2026-09-08T05:40:47Z完成自编设计、write_allowlist、prohibited_paths及precontact seal，随后才首次读取候选。固定563条Manifest、主报告及55候选文件从精确Git blob复算，前后零漂移；候选树摘要独立复算一致。没有以HEAD替代固定提交。

评审根首次不存在后创建，root0700/marker0600；55文件源码副本创建于其work/candidate。Cargo `build --locked --offline`退出0，用review profile从新缓存构建；全部55项构建后仍与固定blob一致。binary SHA256见动态结果，direct进程44705和44713均退出。没有启动GUI或声称获取PID→AXWindow→WebArea→截图链。

自编动态反例2项：1正常对照PASS、1攻击FAIL。语义mutation 0，native GUI 0。工程77项中的63新跑+14历史仅是工程输入口径，不计入本轮独立测试。

矩阵：M01、M12 PASS；M02、M04 FAIL（同一个P0）；M03/M05/M06/M07/M08/M09/M10/M11共8行未完成。发现P0后按ABF停止正向验证，未完成行不推定通过，也不虚构候选缺陷。

计数：**P0=1 / P1=0 / P2=0 / Unknown=0 / Not Implemented=8**。本轮未评估工程所述既有导航滚动P2，不将其计为新发现。

## Closure List 与 PM 决定

建议同一P3-147修复外部目标原件目录的完整目录链、所有权和权限检查，采用锚定目录FD/相对创建等避免检查后替换竞态；在chmod或创建原件前拒绝符号链接。应覆盖Web与本地外部文件两个目标分支，保留该失败历史。普通 `lstat` 后再按字符串路径写入不能单独证明竞态安全。

请PM接收该P0并回工程同任务Closure。本评审不改原候选、不调整ABF、不启动后继。修复后由PM绑定新固定候选和受影响验证范围；未变且可信的工程历史不需机械重建。独立安全Gate当前未通过，真实Gate持续Pending，**不需要Key**。

## 关卡与保留状态

Gate2数据来源、Gate3权限、Gate4技术安全：未通过，受上述P0阻断。Gate1未形成独立完整结论；Gate5用户真实亲验Pending。没有PM终局Pass、风险关闭、关键冻结或Stage切换。

唯一临时根 `/private/tmp/lifeos-p3-147-independent-review-v1` 保留；marker已复核，自有writer和DB进程已关闭。合成反例链接及原件保留供复核，未自动物理清理。`checkpoint.json`明确candidate_failure和safe_to_resume=false，当前候选不得继续正向执行；不是等待解锁的环境故障。

本地CURRENT_STATUS仍为2026-09-03的P3-144索引，当前派工ABF和任务卡的范围优先。治理与模板读取中出现的输出截断已针对缺失段补读；停止后未继续展开与当前缺陷无关的规范或历史。未写PM账本、Git元数据、push或merge。
