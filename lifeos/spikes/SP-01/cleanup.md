# SP-01 清理说明

本目录只包含合成、可丢弃数据。保留报告、脚本、矩阵与 JSON 结果即可复核结论；`work/` 下三个数据库是可再生成的运行产物。

如需释放空间，仅删除以下明确目标（可通过 Finder 移到废纸篓，便于恢复）：

- `lifeos/spikes/SP-01/work/spike.db` 及同名前缀的 `-wal/-shm`
- `lifeos/spikes/SP-01/work/backup.db` 及同名前缀的 `-wal/-shm`
- `lifeos/spikes/SP-01/work/restored.db` 及同名前缀的 `-wal/-shm`

不要以仓库根目录、用户目录、`$HOME`、`~` 或通配的上级目录作为递归清理目标。重新运行 `python3 lifeos/spikes/SP-01/run_spike.py` 会重建这些文件并覆盖本 Spike 自己的结果文件；不会读取或删除其他目录数据。

