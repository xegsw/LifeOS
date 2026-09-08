# P3-147 合成工程复跑与 App

本包仅运行任务自有合成库和注入 Transport。五项公共 IPC 已批准，原20项保留。不得将本入口用于真实目录、真实网络、Provider、凭据或旧 Pilot。

## 自动检查

在本工程 worktree 中执行：

```sh
LIFEOS_P3_147_BUILD_PROFILE=engineering python3 -B lifeos/engineering/LIFEOS-P3-147/candidate/tools/run_internal_checks.py
```

脚本校验/创建唯一合成根 marker，首次创建合成来源夹具；不覆盖既有来源。使用本机锁定离线 Cargo、Node/Python 和 Swift。每次结果写新的 `evidence/checks-时间/`。需要补跑时，脚本可接收逗号分隔阶段名，例如 `ui_build,build,public_api`，不重跑无关阶段。

94项：Rust23、解析11、注入Web14、Application/继承31（原30+来源上下文1）、公共IPC生命周期1、root profile4、target_boundaries10。此次实际复跑65项，解析11/Web14/root profile4共29项为未改历史复用；原review runner工程适配2例另计。可指定 `format,build,rust,inherited,target_boundaries,public_api` 复跑受影响链路。格式、UI生成、离线构建及别名辅助程序构建另计。

## 打开实际 App

自动检查完成后执行（标签必须唯一）：

```sh
LIFEOS_P3_147_BUILD_PROFILE=engineering python3 -B lifeos/engineering/LIFEOS-P3-147/candidate/tools/launch_app.py preview01 desktop
```

窄窗口使用 `narrow`。启动脚本返回直接PID及二进制hash，App位于 `/private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS P3-147.app`。不要同时启动两个实例。

Settings → 数据与隐私 → 来源 → 连接合成目录。查看分批进度、原件状态；可暂停/继续、取消/刷新、断开。Memory → 本地检索，输入“项目计划”，打开原文依据。自然表达保存后自动准备有限相关片段。直接引用中的具体合成网页和目录外文件需要分别点击授权；未授权不获取。这里没有真实目录选择器和真实联网能力。

原件在自有根 `artifacts/`，解析临时结果在 `.runtime/`，数据库不进入工程目录。完成演练后保留该根供恢复及操作App；不是已执行物理清理。若要回收合成环境，先停止并核对所有本任务PID，再运行 `task_root.py cleanup`；marker不匹配、PID仍存活或WAL未关闭时拒绝清理。真实根不在脚本范围。

## Evidence

`FINAL_MANIFEST.json` 非自指，覆盖候选、原始失败记录、继承快照、逐行矩阵、检查点和主报告hash。`verify_release.py` 只验证完整性和证据关联，不产生PM/独立评审结论。最终校验输出及内存内Manifest反例输出显式排除，避免自引用。

此前Partial与待API批准版本完整保留在 `history/pre-public-api/`，不得解释成当前仍待批准。各轮原生证据绑定各自二进制；最终原生条目由Manifest明确指定，早期不同二进制不替代最终证明。窗口启动空白、AX/工具暂不可用等记录保留；恢复只补原生阶段。

## 双根与独立评审复跑

根权威为候选 `root_profiles.json`。仅 `engineering` 和 `independent-review` 两种构建profile；必须显式 `LIFEOS_P3_147_BUILD_PROFILE`，无默认根。binary 编译绑定profile/root；运行时不接受root override，profile环境值若存在必须与binary一致。`--profile-info`仅输出编译身份，不访问root，不是新增IPC。marker必须精确匹配所选配置；已有根无marker不能补造所有权。root、fixtures、.runtime、tmp、artifacts按0700验证，marker0600；两个marker的owner不同。真实根永不进入这个配置。

以下命令**仅供PM另行分派的全新独立评审会话**，先完成其test_design/precontact seal，之后才接触候选。工程会话本次没有执行这些review根操作，只做该profile的纯配置与 `cargo check --tests --locked --offline` 编译。独立会话不能复用工程测试结论代替自己的反例设计。

将 `CANDIDATE_COMMIT` 设置为PM投递的40位固定提交（不要用main/HEAD/可变分支）。从本worktree只读执行这两个helper，`-B`不写源码目录pycache：

```sh
export LIFEOS_P3_147_BUILD_PROFILE=independent-review
export CANDIDATE_COMMIT=由PM交付的40位固定提交
python3 -B /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/candidate/tools/task_root.py init
python3 -B /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/candidate/tools/prepare_review_copy.py "$CANDIDATE_COMMIT"
export CARGO_TARGET_DIR=/private/tmp/lifeos-p3-147-independent-review-v1/initial-build-cache
export TMPDIR=/private/tmp/lifeos-p3-147-independent-review-v1/tmp
export PYTHONDONTWRITEBYTECODE=1
python3 -B /private/tmp/lifeos-p3-147-independent-review-v1/work/candidate/tools/run_internal_checks.py
python3 -B /private/tmp/lifeos-p3-147-independent-review-v1/work/candidate/tools/launch_app.py reviewdesktop01 desktop
```

复制入口先验证固定Git blob与该提交Manifest每项hash/bytes；只复制candidate源码、UI、依赖helper和测试到review根 `work/candidate`，绑定清单保存在 `work/source-lineage.json`。不复制工程Evidence、DB、artifacts、App或cache。已有work目录不覆盖，按lineage继续。构建只使用锁定离线依赖；Rust产物在review根initial-build-cache、Swift模块缓存在review根swift-cache、解析临时结果在review根.runtime。源码依赖路径 `CARGO_MANIFEST_DIR` 因从review-owned源码构建而绑定review副本；不得直接在工程candidate上以review profile构建。

检查脚本仅写review-owned副本与 `work/evidence/checks-时间/`，不写工程candidate/Evidence。它是工程回归入口，不代替review-owned runner。App为review根自己的 `LifeOS P3-147.app`，launch返回fresh PID；后续AX/截图必须由该PID绑定。当前App标签仍为“LifeOS · P3-147 · 合成离线”，通过PID、binary hash与compiled_profile分辨，不能根据标题猜测身份。

如取原生Evidence，先在同一review根用 `swiftc -module-cache-path "$TMPDIR/../swift-cache" work/candidate/tools/native_evidence.swift -o "$TMPDIR/../native_evidence"`（工作目录为review根），再用副本 `record_app_evidence.py 唯一标签 直接启动PID`。不得复用工程PID/窗口/截图/DB。独立会话按自身合同保留或marker验证后清理，工程会话不操作review根。

`history/pre-root-closure/`保全双根修复前259项工程文件和报告，其旧“工程完成”只为当时交付事实。Closure只修正评审可运行性；Independent/真实Gate/PM最终仍待完成。

## artifact安全修正交付

原640ebb6候选及独立P0历史保全在history/pre-artifact-closure；本次工程修正不覆盖原Rework。新固定提交须由PM重新绑定Independent Delta及原未完成8行。完整文件差异见evidence/artifact-closure-diff.json，代码差异使用该固定父提交与新提交之间的git diff。
