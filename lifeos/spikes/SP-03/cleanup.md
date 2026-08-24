# SP-03 清理说明

本 Spike 不创建外部资源、账号、服务、网络副本或用户数据副本。

可丢弃范围仅限：

- `lifeos/spikes/SP-03/results.json`
- `lifeos/spikes/SP-03/test_matrix.csv`
- `lifeos/spikes/SP-03/evidence_chain_samples.json`
- `lifeos/spikes/SP-03/dependency_invalidation_report.md`
- `lifeos/spikes/SP-03/export_reimport_report.md`
- `lifeos/spikes/SP-03/audit_privacy_check.md`
- `lifeos/spikes/SP-03/SP-03_report.md`
- `lifeos/spikes/SP-03/raw_logs/`

这些文件可由再次运行 `python3 lifeos/spikes/SP-03/run_spike.py` 安全重建。不要删除 `run_spike.py`、`environment.md`、`fixture_manifest.md`、`cleanup.md` 或最终 PM 交付物。清理时必须使用以上精确路径，不得以仓库根目录、用户目录或广泛通配符为目标。
