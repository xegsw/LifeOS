# LIFEOS-P3-073 可复查独立复评 Evidence

本目录为 D-0306 授权的 Evidence Rework 新建子目录。旧 `lifeos/reviews/LIFEOS-P3-073/evidence/` 保持只读历史记录，未被删除或覆盖。

## 可复跑命令

在仓库根目录执行：

```bash
python3 lifeos/reviews/LIFEOS-P3-073/evidence/authorized_rerun/independent_runner.py
```

预期：退出码 `0`，标准输出 `{"pass": 18, "fail": 0}`，并重写本目录的 `independent_results.json`。runner 不导入或调用 P3-072 测试套件；它把被评审模块复制到一次性系统临时目录后加载，只调用 preview 与必然 blocked 的确认路径，绝不调用成功导出路径，因此本轮不会创建临时导出文件。

## 覆盖与限制

18 项逐项结果覆盖 D-0302 授权链／当前 hash、旧未授权资产保留、默认不写、精确确认与 token、来源／版本／未知／冲突／撤回／tombstone／预览后状态变更、单次语义、路径逃逸／覆盖、原子发布、失败清理、审计和关闭态。

路径、覆盖、原子发布和失败清理在本轮以 source-level guard 核验；这是为遵守 P3-073 “不得生成临时导出文件”限制。它不替代 P3-072 授权复跑的 8 项受控运行 Evidence，也不涉及真实文件导出、真实路径、Vault、Tauri/IPC、真实 DB、云、同步、多设备、L3 或外部用户。
