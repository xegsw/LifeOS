# LIFEOS-P3-078 Independent Evidence Manifest

## 边界与复跑

- 评审对象：`lifeos/engineering/LIFEOS-P3-077/` 当前 hash，仅限非敏感测试文本、task-local SQLite 与新建临时副本。
- 独立 runner：`runner/independent_permission_review.py`；它不导入、调用或复制 P3-077 的 `tests/test_permission_runtime.py` 或 `scripts/run_self_check.py`。
- 复跑命令：`PYTHONDONTWRITEBYTECODE=1 python3 lifeos/reviews/LIFEOS-P3-078/runner/independent_permission_review.py`
- 结果：15 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0，退出码 0。
- 临时副本由 runner 以系统临时目录 `lifeos-p3-078-independent-*` 创建并在结束时自动清理；不会写入 P3-077 或历史资产。

## 验收标准 → 独立反例 → Evidence

| 任务卡标准 | 独立反例 | Evidence | 结果 |
| --- | --- | --- | --- |
| preview 可理解、默认拒绝、唯一精确 grant + CONFIRM | IR-01、IR-02、IR-03、IR-13 | `independent_results.json`、日志 | PASS |
| 当前 deny 优先；错误确认／绑定不匹配／过期／歧义 fail-closed | IR-04、IR-05、IR-06、IR-11 | 同上 | PASS |
| 幂等与冲突不得扩大授权 | IR-07、IR-08 | 同上、快照 | PASS |
| 撤回审计、重启后拒绝与可追溯性 | IR-09、IR-10 | 同上、`independent_snapshot.json` | PASS |
| 原子失败无半成品 | IR-12（task-local SQLite trigger 注入 audit 写入失败） | 同上、快照 | PASS |
| 禁止通道继续关闭 | IR-14（AST import 静态检查） | `independent_results.json` | PASS |
| 当前候选 hash 与历史只读输入未被覆盖 | IR-15；下列 hash 核对 | 本 Manifest、P3-077 historical hash 文件 | PASS |

## Hash

| 文件 | SHA-256 |
| --- | --- |
| `P3-077/src/permission_runtime.py` | `1aca35f29e3a09505f7b825a33e5f386932aae946817da4bc8d91ca9615df9fa` |
| `P3-077/scripts/permission_cli.py` | `8bea310d2eda9137c5387e571dd1ff7083f3e6f7771e3fec1c7eec4b0413d6d2` |
| `P3-077/scripts/run_self_check.py` | `4ea17642fe89c0e0843ffbed7f62a8df140d3c79f2da64eff96a2aad7ce3cb4a` |
| `P3-077/tests/test_permission_runtime.py` | `f513bbdc973c7f0fdabaac522b0b717c6606f7a294607ac7bca219c8fb81e48f` |
| `runner/independent_permission_review.py` | `397fe484ce95748ca77e46a319c97fd80ec51aad176f61f2644c1139736963c4` |
| `evidence/independent_results.json` | `c3e7fa069add9d084ab82dd262e897359812361a3f070a0ce2e409cc4f5f55fa` |
| `evidence/independent_review.log` | `db14ae7ee3acb07c4d9a5cdf942f189b5cec65242768a519486a0bce1052cdc3` |
| `evidence/independent_snapshot.json` | `14a394d12fcbbfb9259e445af5e9b85a4f91f9f28c5d54c45f31da0d3f84c6a9` |

P3-077 的 7 项历史只读输入与其 `evidence/historical_input_hashes.json` 中 hash 一致；本任务未写入其路径。候选工程其余 6 项受控 Evidence hash 亦与 P3-077 `evidence/MANIFEST.md` 一致。

## 静态关闭态与非范围

独立 AST import 检查未发现网络、云／第三方、Tauri/IPC、Vault 或多进程通道；候选仅使用 Python 标准库与 caller-supplied SQLite。代码与 CLI 未实现真实个人数据、真实 DB／路径／文件、AI 消费、导出、同步、多设备、L3 或外部用户。上述关闭态不外推为真实能力验证，也不改变 R-0013、R-0014、R-0015、R-0021 或 R-0040。

## Local Precheck

`lifeos/local_prechecks/LIFEOS-P3-078_LIFEOS-P3-078_local_runtime_permission_settings_fresh_isolated_independent_re_review_local_precheck.md` 已生成，但因本地模型不可用而跳过；未参与本独立结论。
