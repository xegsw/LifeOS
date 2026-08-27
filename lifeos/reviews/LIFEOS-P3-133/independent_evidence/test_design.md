# P3-133 独立评审测试设计（冻结前置）

- 评审任务：`LIFEOS-P3-133`；评审角色：全新隔离独立评审。
- 编写时点：已验证 `ABF-P3-133-v1`、冻结 manifest 及三项固定输入的 SHA-256；尚未读取 P3-133 candidate、P3-133 工程 Evidence／PM Review，尚未创建评审临时根或启动 actual Tauri。
- 禁止目标：不访问、探测或提及真实 Pilot-3 文件系统对象；不使用网络、模型、云、外部进程、凭据、真实文本或真实 DB；不执行 write-capable `verify_engineering.py`。
- 允许写入：仅本目录、`independent_review.md` 及精确临时根 `/private/tmp/lifeos-p3-133-independent-review-v1`。候选、P3-133 工程 Evidence、P3-132及此前历史资产为只读。

## 独立性策略

1. 先将本设计 SHA-256 固定，再读取任何 P3-133 PM／工程 runner、结果或历史 Evidence。
2. 用本评审自行编写的 runner 与 verifier。不得 import、调用、复制或执行工程攻击 runner、工程结果或原 `verification.json`；工程 manifest 只作反向的声明／hash 对照，不作正 Evidence。
3. 只从只读候选创建审查临时副本；编译缓存、SQLite DB、日志、截图、runner 输出全部位于精确评审临时根。所有合成 payload 均固定为非敏感标记，最终 Evidence 对其做 taint 扫描。
4. 每个 ABF 行保留独立原始 JSON、前后 hash／SQLite 状态、命令和退出码；最终 verifier 只由这些独立原始文件重算结论。保留未变 negative control 与必需 mutation。

## 矩阵与证据计划

| ABF 行 | 独立验证 | 原始 Evidence |
|---|---|---|
| M-001 | 复算冻结固定输入及候选 source lineage、类型与 IPC 清单 | `source-lineage.json` |
| M-002～M-004 | 规范根正例、链接／相对／父级／文件型根、已有或非普通 DB 拒绝 | `root-positive.json`、`root-mutations.json`、`db-type-mutations.json` |
| M-005～M-006 | actual-Tauri 合成 taint 闭环；3 条／200 字符与写前拒绝 | `privacy-taint.json`、`input-limit.json` |
| M-007～M-009 | 未确认无 Action／Focus，显式确认后单 Action，Today 0／1 稳定 | `unconfirmed-state.json`、`confirmed-action.json`、`today-focus.json` |
| M-010 | 真实模式路径模拟下 Understanding／Feedback 固定不可用，adapter 计数零 | `model-disabled.json` |
| M-011 | quit/reopen 后 opaque ID、计数与确认状态相同，无 sidecar／复制 | `restart.json` |
| M-012 | 本独立包的矩阵、Manifest、访问 ledger 与可复跑入口 | `independent-matrix.json`、`FINAL_MANIFEST.json` |
| M-013 | 不执行真实自用；标记 `Not Executed`，不将它解释为 Pass | `real-use-not-executed.json` |
| M-014 | 只精确清理评审临时根，并从 cleanup 收据复算 | `cleanup.json` |

## 判定规则

- P0/P1/Unknown/Not Implemented 任一非零或任一 M-001～M-012/M-014 不可独立复核，即不是独立 Pass；同合同工程缺口一次性列为 Closure List，绝不改候选。
- M-013／AC-12 的真实步骤在此阶段明确 `Not Executed`，不计入独立合成评审的工程缺口，也不触发真实运行或风险关闭。
- 独立 Pass 最多说明合成评审门槛通过；不构成 PM 验收、真实运行授权、资产／Runtime／IPC／Schema/API 冻结、R-0053 关闭或 Stage 4 准入。
