# P3-149 S3 受控真实导入执行报告

状态：Partial — 已完成隔离实现与合成自测，真实导入执行一次后按既有资源上限安全失败，唯一真实导入结果未达成。主责Codex专项工程，复用前一已结束工程会话；L3真实范围。用户在完整真实边界后回复“确认开始”，PM分派 `contract-inputs/task.md`；独立评审按用户明确指示暂停，不称Independent Pass、PM Pass、安全风险关闭或Stage变更。

## 实际结果

脱敏回执 `evidence/real-receipt.json`：**status=failed，code=health_zip_expansion_limit，inserted=0，failed=1，target_created=true，retained=true，network=false，model=false**。支持/重复/不支持/附件计数不可知，以null返回，不伪造0或全部成功。没有第二次真实执行，也未提高限制。

该固定错误由继承S2的ZIP目录元数据检查产生：总声明解压量超过512MiB，或某条目声明解压量超过压缩量的200倍。回执不区分二者，未打印真实ZIP目录、大小、压缩比、类型、属性或健康值，不能据此推断具体哪一项条件。守卫在读取选中XML正文之前终止；没有健康观察发布，事务回滚。程序没有修改/删除/复制原ZIP，创建的新专用目录和库均保留，未清理任何既有内容。

授权源及唯一目标以任务卡为准：只读 `/Users/xxe/Downloads/导出.zip`；新目录 `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/`，库 `health-import.sqlite`。这些为用户已给定的路径，不是探测获得的信息。程序只走这些精确目标，没有扫描Downloads其他文件或个人目录。未对真实文件或库生成工程hash；去重标识仅由本地程序内部处理，未进入回执或Evidence。本次事务没有提交任何批次。

## 实现与脱敏

S3从S2候选派生，S2的188项文件及Manifest逐项校验保持只读。S3候选新增2文件、修改6文件、删除0，详情 `evidence/candidate-diff.json`；真实执行前后候选hash一致。synthetic根改为已授权149合成根下S3，真实库不混入任何合成夹具。

固定 `--controlled-health-import` 程序分支在Tauri、运行时、Provider或凭据初始化之前完成并返回，只接受该一个固定开关，不接受任意源/目标参数或环境路径覆盖。不增加IPC，已有唯一导入IPC继续用于synthetic UI，不绕过其synthetic门禁。真实执行不启动通用App的模型/凭据功能，也不捕获真实GUI。

复用S2流式解析器与Rust Application的单事务导入/投影，新增只读描述符输入适配器。逐层无symlink打开，普通文件/owner/nlink校验，读取前后inode/mtime/ctime及目录链校验；不chmod源。目标必须新建，已存在即失败；目录0700，库0600，SQLite NOFOLLOW打开并在打开后及事务发布前校验目录/文件身份和单链接。SQLite临时存储限定内存，开发缓存只在S3合成根。首次实验的 `/dev/fd` SQLite路径在合成测试上不兼容，已改为精确固定路径打开加持有描述符的前后验证，未用真实文件调试。

真实模式保留原三类指标全部时间范围与S2映射/限制；不支持类型名在保存批次前去除，仅保留总数，不持久化其他指标记录；附件正文不读。程序关闭panic/普通stdout/stderr通道及core dump，只用独立描述符写允许的状态/计数回执。外层 `tools/run_controlled_once.py` 再校验允许字段、标量类型、状态/错误码格式，异常只返回receipt_unavailable，不输出原始结果。执行标记使用排他创建，防止工具被机械再次运行。没有网络、Provider、模型、本地模型、Keychain或云调用。

## 合成自测与证据

- Python解析 **26/26**：S3 `evidence/rerun-*.log`；解析器与S2逐字一致，含XML实体、ZIP穿越/特殊项/压缩炸弹/损坏/资源及支持类型验证。
- Rust **63个不同测试通过**：组合复跑中health筛选61项（原59+新2）、独立source-preview筛选1项，另补第3项提交前目标替换回滚测试。`evidence/controlled-tests-final.log` 的3项受控入口测试全通过。未声称全历史套件。
- 前端 **27/27**：同一组合复跑日志。已有Context/resolver/source-preview/prepare健康排除守卫继续通过。
- 受控同构测试覆盖0700/0600、新目录不可复用、symlink/hardlink拒绝、源替换、目标替换、事务中断回滚、成功重试、同文件重复幂等、损坏后保留有效数据、私有类型名不入库、回执错误内容脱敏。目标在提交前被替换时记录数仍为0。
- 离线构建成功 `evidence/build-final.log`；未运行CI。真实程序binary摘要只记录在 `real-execution-started.json`，该hash不是任何真实文件或库的hash。
- `evidence/static-boundaries.json`记录受控分支先于通用初始化、固定参数、无新增IPC和解析器保持；`candidate-before-real.json`只含工程源码hash。

合成开发中一次include路径错误、一次SQLite /dev/fd不兼容的失败日志保留，不作正证据。后续测试通过。真实运行没有调用源码调试、SQL正文查询、GUI/AX、截图或任何原文诊断；程序仅以固定代码返回资源拒绝。

## 角色、关卡与后续边界

工程视角P0=0/P1=0/P2=0/Unknown=1/Not Implemented=0；Unknown指真实包的具体资源触发项未披露，真实导入成功条件因此没有通过。该计数不等于整体Pass，PM可按合同事实裁决。S2历史P2不在本增量重新裁定。安全/授权视角已完成合成自测和限定执行，不代替独立评审。PM_OPERATING_MODEL的L3独立评审要求按当前用户明确例外暂停，不伪造评审结果；无其他关键冻结或Stage动作。

工程入口 `tools/run_checks.py`可复跑合成测试；真实入口 `tools/run_controlled_once.py`已执行，其排他标记会阻止再次调用。`checkpoint.json`为停止于合同资源限制，自动resume/retry关闭。报告与Manifest均只包含工程材料和脱敏回执；原文件、新真实库不在Manifest。

需PM：接收本次安全失败事实，向用户说明现有限额不满足该ZIP，决定是否另行明确允许资源策略变化及在同一新库的幂等重试设计。当前任务明确要求保留S2资源限制，执行侧不得自动提高上限、读取详细真实元数据、探测正文或反复尝试。没有要求用户上传文件/截图/正文；没有提交推送合并、风险关闭、冻结、账本更新或后继任务。
