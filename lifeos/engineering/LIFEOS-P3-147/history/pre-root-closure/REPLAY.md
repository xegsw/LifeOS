# P3-147 合成工程复跑与 App

本包仅运行任务自有合成库和注入 Transport。五项公共 IPC 已批准，原20项保留。不得将本入口用于真实目录、真实网络、Provider、凭据或旧 Pilot。

## 自动检查

在本工程 worktree 中执行：

```sh
python3 -B lifeos/engineering/LIFEOS-P3-147/candidate/tools/run_internal_checks.py
```

脚本校验/创建唯一合成根 marker，首次创建合成来源夹具；不覆盖既有来源。使用本机锁定离线 Cargo、Node/Python 和 Swift。每次结果写新的 `evidence/checks-时间/`。需要补跑时，脚本可接收逗号分隔阶段名，例如 `ui_build,build,public_api`，不重跑无关阶段。

71项：Rust14、解析11、注入Web14、Application/继承31（原30+来源上下文1）、公共IPC生命周期1。格式、UI生成、离线构建及别名辅助程序构建另计。

## 打开实际 App

自动检查完成后执行（标签必须唯一）：

```sh
python3 -B lifeos/engineering/LIFEOS-P3-147/candidate/tools/launch_app.py preview01 desktop
```

窄窗口使用 `narrow`。启动脚本返回直接PID及二进制hash，App位于 `/private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS P3-147.app`。不要同时启动两个实例。

Settings → 数据与隐私 → 来源 → 连接合成目录。查看分批进度、原件状态；可暂停/继续、取消/刷新、断开。Memory → 本地检索，输入“项目计划”，打开原文依据。自然表达保存后自动准备有限相关片段。直接引用中的具体合成网页和目录外文件需要分别点击授权；未授权不获取。这里没有真实目录选择器和真实联网能力。

原件在自有根 `artifacts/`，解析临时结果在 `.runtime/`，数据库不进入工程目录。完成演练后保留该根供恢复及操作App；不是已执行物理清理。若要回收合成环境，先停止并核对所有本任务PID，再运行 `task_root.py cleanup`；marker不匹配、PID仍存活或WAL未关闭时拒绝清理。真实根不在脚本范围。

## Evidence

`FINAL_MANIFEST.json` 非自指，覆盖候选、原始失败记录、继承快照、逐行矩阵、检查点和主报告hash。`verify_release.py` 只验证完整性和证据关联，不产生PM/独立评审结论。最终校验输出及内存内Manifest反例输出显式排除，避免自引用。

此前Partial与待API批准版本完整保留在 `history/pre-public-api/`，不得解释成当前仍待批准。各轮原生证据绑定各自二进制；最终原生条目由Manifest明确指定，早期不同二进制不替代最终证明。窗口启动空白、AX/工具暂不可用等记录保留；恢复只补原生阶段。
