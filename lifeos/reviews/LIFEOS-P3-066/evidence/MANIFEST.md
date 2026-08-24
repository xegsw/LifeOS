# LIFEOS-P3-066 Evidence Manifest

## 隔离与命令

- 评审目录：`lifeos/reviews/LIFEOS-P3-066/`；仅新增本任务 Review、交付物和 Evidence。
- 被评审工程严格只读：`lifeos/engineering/LIFEOS-P3-065/` 未被写入。执行目标为一次性副本 `/private/tmp/lifeos-p3066-independent/LIFEOS-P3-065/`；副本内 runtime 可写，原目录不写。
- 独立性：`independent_runner.py` 为本任务新写，未导入、调用或复制 `P3-065/tests/test_permissions.py`；只加载隔离副本的候选实现，并以新建断言验证。CLI 路径以子进程黑盒执行。

命令与退出码：

```sh
python3 lifeos/reviews/LIFEOS-P3-066/evidence/independent_runner.py \
  /private/tmp/lifeos-p3066-independent/LIFEOS-P3-065 \
  lifeos/reviews/LIFEOS-P3-066/evidence/independent_results.json
# exit 0；14 PASS / 0 FAIL

(cd /private/tmp/lifeos-p3066-independent/LIFEOS-P3-065 && ./scripts/run_tests.sh)
# exit 0；23 PASS / 0 FAIL
```

## 独立结果

- 历史 P1 复现：同精确绑定 `grant→deny` 与 `deny→grant` 均为 `allowed=false`、`explicit_deny_current`；前者同时核对 `external_action=none`、`ai_consumption=none`。
- Fail-closed：默认无授权、四维不匹配、过期、撤回、多当前 grant 歧义均被拒绝。
- 幂等与持久化：重复 deny、重复 revoke、决定幂等键冲突、撤回幂等键冲突均通过；冲突不改变另一条授权。
- 黑盒体验路径：`preview→CONFIRM grant→consume→CONFIRM deny→consume` 通过；确认、审计身份状态与无外部动作均被检查。
- 静态关闭态扫描：源、脚本与测试中未发现网络客户端、Tauri/IPC、Vault、导出、同步、多设备或 L3 实现通道；唯一 `tauri_ipc` 命中为关闭态数据字段／断言。

## 当前与历史保留证明

| 输入／产物 | SHA-256 | 结论 |
|---|---|---|
| `src/permissions.py` | `29e33624b7988e3b18b9ec6451d1e76c97f43ae2189f65636e51d66460dca57a` | 与 Rework Manifest / PM Evidence 一致 |
| `scripts/permission_cli.py` | `342ef7bc918cb062090ad8d03866d4798822d83440818cfce14fd04f8ecb47d1` | 与 Rework Manifest / PM Evidence 一致 |
| `tests/test_permissions.py` | `fb25ba02488d3ba6f686a89f7352341c853b90db4ae5a4c01baa94d73ab0619c` | 与 Rework Manifest / PM Evidence 一致 |
| Rework `test_results.json` | `33dead70755c262e3529abb9c2cf207515cb092bafd51b3e784e0bcdd234b7cf` | 23 PASS Evidence 保留 |
| Rework `conflict_matrix_snapshot.json` | `daa6347de0c0b933ce79a7fbf0fe76558b9b474298e8d8d7d04f5d58d49b6ed2` | PM P1 修复快照保留 |
| 初版 `evidence/initial/MANIFEST.md` | `fd7546e1c69f78d075ea7804820b860ae0fcd3b30a24162cf06fad395effd00b` | 初版 14 PASS 目录仍独立存在 |
| PM Evidence Manifest | `1fd724b227dfac4e1166cc0a9fce3a4d4ddd3d51648210c6d5480073bb035e6e` | PM P1 Evidence 保留 |
| 本 runner | `39ddfc6d6ea7fec2cbfa8490061d15c9c97b5a150a8c02f7c71d530c0b5b8aab` | 独立验证方法 |
| 独立结构化结果 | `abf726ecee48894656847f88995dee77cd19f0ed2fcee8e543744155aa9a7daf` | 14 PASS / 0 FAIL |
| 候选回归日志 | `41326d6a8b1e084cd7e7d5695b981dc9ff4b01d2d949a4fdad5502de23d83ff7` | 23 PASS / 0 FAIL |

## 范围

证据仅支持当前 hash、单进程、合成 SQLite、受控 Project 与无外部动作的基础权限设置。它不验证真实身份、个人数据、真实路径／Vault、Tauri/IPC、网络／云、导出、同步、多设备、L3、并发／WAL、清理状态机、风险关闭、冻结、工程基线恢复或 Stage 4。
