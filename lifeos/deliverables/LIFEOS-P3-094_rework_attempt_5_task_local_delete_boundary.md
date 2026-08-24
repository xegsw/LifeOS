# LIFEOS-P3-094 Rework attempt-5｜Task-local 删除目标边界 P0 整改交付物

## 任务信息

- 任务 ID：LIFEOS-P3-094（Rework attempt-5）
- 执行 Agent：Codex；任务卡路由 `gpt-5.6-terra` + `high`，未降级
- 任务类型：P0 受控真实本地能力包内删除边界窄整改
- 更新时间：2026-08-22
- 执行授权证据：用户于 2026-08-22 将更新后的 `lifeos/tasks/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md` 重新投递至已结束 attempt-4、未承担 P3-095 独立评审的同一 Codex 工程会话；接收时间 2026-08-22 18:12 CST。D-0389 仅授权强制绑定 DB 同目录精确 `today.html`、拒绝越界／规范化／链接路径并补负向回归。

## 修复目标与事实结论

D-0388 证明 attempt-4 的 `delete_all(..., output_path)` 和 CLI `clear --output` 可删除 DB 父目录外的任意可写文件并继续清空 DB。该 P0 已在本轮实现层收口：CLI 完全移除 `--output`；运行时保留第三参数只作为兼容性拒绝入口，任何调用方目标均在文件或数据库变更前返回 `CaptureError`。

唯一删除目标现在只能由运行时内部推导为绝对、无 `..` 的 `db_path.parent / "today.html"`。清理前先以 `lstat` 确认 DB 父目录、DB 文件和页面目标边界：DB 父目录必须是非链接目录，DB 必须是现有非链接普通文件；页面不存在或为非链接普通文件时才可继续。页面若为符号链接、目录、FIFO／特殊文件或类型无法确认，操作在任何变更前拒绝且不跟随链接。

合法路径继续保持 attempt-4 顺序：先精确失效内部页面并确认目录项不存在，再进入 SQLite 事务清理。页面失效失败时 DB 不变；数据库清理失败时不得报告成功。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`：加入内部唯一目标推导、DB／父目录／页面 `lstat` 类型与链接边界门。
- `lifeos/engineering/LIFEOS-P3-094/scripts/operator_cli.py`：移除 `clear --output`。
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`：扩展至 12 项正负回归。
- `lifeos/engineering/LIFEOS-P3-094/README.md`：对齐唯一删除目标及 fail-closed 合同。
- `lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/`：新增干净副本 runner、逐项结果、哨兵 hash、日志、源码 hash、历史 hash、Manifest 与追溯矩阵。

## 非范围与历史保全

- 未使用真实用户文本、既有个人文件／DB 或真实凭据；测试仅使用固定非敏感文本与哨兵。
- 未启用网络、HTTP、云／第三方、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 未覆盖 attempt-1／2／3／4、P3-095、P3-094 PM Review／PM Evidence 或项目账本；80 个历史只读文件前后 hash 相同。
- 未关闭 R-0051，未恢复基线，未冻结资产或 Schema/API，未进入 Stage 4。

## 测试与包内自检

复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/scripts/run_attempt_5.py
```

结果为 **18 PASS / 0 FAIL**，覆盖：首次捕获与渲染、幂等、真实新进程复读、合法精确清理；API DB 外哨兵；非标准文件名、相对路径、规范化与 `..` 绕路；CLI `--output` 拒绝；页面符号链接、目录、FIFO；DB 父目录符号链接、DB 文件符号链接；页面删除失败；原子写入失败、损坏 DB、禁止能力关闭态；12 项干净副本单元回归、零残留与历史保全。

API、CLI 和链接目标三类固定哨兵的前后 SHA-256 均为 `45937ac2a9ddfd122952197ed7e30ecc836aff82e35b8230bd3d6d188b22d2d2`；操作失败时哨兵、DB 记录和内部页面均保持不变。合法页面清理后 DB 为零、旧页面不存在且重渲染明确失败。

问题计数：P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。当前 Evidence 不包含 SQLite、HTML、FIFO、链接、缓存、记录 ID 或原文。本地模型预检已跳过：任务卡禁止网络／模型，且这是删除与真实本地数据边界的 P0 高风险判断，局域网模型不得替代人工反例复核。

## Evidence

- Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/evidence/MANIFEST.md`
- 结构化结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/evidence/results.json`
- 哨兵 hash：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/evidence/sentinel_hashes.json`
- 验收追溯：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/evidence/acceptance_matrix.md`
- 历史保全：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-5/evidence/historical_read_only_hashes.json`
- 操作日志／复跑：`operation_log.md`、`test_run.log`、`rerun.md`

## 角色与关卡

- 主责角色：技术架构负责人／Codex 工程执行。
- 协审视角：数据与来源、AI 信任与安全、体验设计。
- Gate 2：执行侧范围内通过；删除目标无法由调用方越出 task-local DB 同目录，链接不被跟随。
- Gate 3：执行侧关闭态通过；显式 `DELETE` 确认保留，无 AI 或外部处理。
- Gate 4：执行侧包内回归通过；D-0388 P0 反例及规范化、链接、特殊文件路径均有结构化证据。
- Gate 1：仅做范围一致性核对；Gate 5 未覆盖且未写成通过。
- 尚需关卡：PM 验收、用户采纳、另一全新隔离独立复评。

## 风险、推断与建议

事实：在固定非敏感、单进程、task-local SQLite／HTML 边界内，D-0388 的任意删除通道已移除；当前矩阵和历史 hash 支持本轮整改结论。

推断：`lstat` 和唯一内部目标消除了已知调用方路径、最终链接和直接父目录链接绕过；本任务不外推为多进程竞态、生产文件系统或所有平台级链接语义证明。

建议：提交 PM 按 attempt-5 当前 hash 验收。PM Pass 与用户采纳后，必须由另一全新隔离会话完成独立反例和 Chrome `file:` 动态矩阵；本执行会话不自行启动后续任务。

## 是否触发 PM／用户确认

- 当前需要 PM 决策：Yes；验收 attempt-5 是否 Pass。
- 后续需要用户采纳与独立复评：Yes。
- 是否请求扩大范围：No。
