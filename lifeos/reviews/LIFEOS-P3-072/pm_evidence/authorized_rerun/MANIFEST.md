# LIFEOS-P3-072 Authorized Rerun PM Replay Evidence Manifest

- PM 在新建临时副本复跑授权复跑目录的 `scripts/run_tests.py`：退出码 0，8 PASS / 0 FAIL。
- 授权复跑源码、测试、runner 与两项 Evidence 的 SHA-256 均与其 Manifest 一致。
- 先前未授权提交的六项资产 hash 同时复核并保持与 D-0301 时一致；未被修改或用于本次可采纳 Evidence。
- PM 复跑只使用临时副本与每次运行新建的系统临时沙盒；不触达用户路径、Vault、Tauri/IPC、网络、真实数据或外部能力。
