# LIFEOS-P3-073 Evidence Rework PM Replay Manifest

- PM 在另一新建临时目录镜像中复跑 `evidence/authorized_rerun/independent_runner.py`：退出码 0，18 PASS / 0 FAIL。
- 可复查 runner、逐项 `independent_results.json` 与 README 的 SHA-256 均与 D-0306 Evidence Rework Manifest 一致。
- 复跑验证授权复跑六项资产 hash、旧未授权提交六项 hash、runner 不依赖执行侧测试、默认不写、确认／token／状态变化阻断、来源／版本／冲突／撤回／tombstone／未知、单次／路径／原子失败／审计与关闭态。
- PM 复跑只写入临时目录；项目中的 P3-072 工程、旧 P3-073 Evidence 与授权复跑 Evidence 未被写入。
