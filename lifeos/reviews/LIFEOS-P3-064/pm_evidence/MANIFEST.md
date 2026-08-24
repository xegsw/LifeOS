# LIFEOS-P3-064 PM Evidence Manifest

## PM 隔离复跑

- 复跑方式：将 `lifeos/engineering/LIFEOS-P3-063/` 复制到 `/private/tmp/lifeos-p3064-pm-review.R0Zumt/LIFEOS-P3-063/`；PM 未覆盖 P3-063 执行侧、P3-064 独立侧或历史 Evidence。
- 独立 runner：以 P3-064 新建 `independent_runner.py` 对该临时副本运行，得到 9 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0，退出码 0。
- 候选回归：在同一临时副本运行 P3-063 `scripts/run_tests.sh`，得到 11 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0，退出码 0；仅作补充。
- hash：候选 `mvp.py` `f35f5651477d1a6fd8cc6e16339b3c63d59ada23c7d00b10ad2954bf72bb632f`、`run_demo.py` `8eaff37b5b108f7046455e9752561a590f4ff7ffa27882dfd60245df9b5e04e4`、`run_demo.sh` `82e3489a1e551573b17c2b40b230dc8767eae02f5a986aeb6cd5a2983d8da694`、`test_mvp.py` `dd0e464cce7becefcd6959fc2768176c6e09516853c4059330bdcc2eb3ecdcf8` 及独立 runner `a2acdd8831f28ad23bcc76998e116d90f9c1ce56ca0c3e67946320f2b03b5c43` 均与独立 Evidence 一致。

## PM 判断边界

- 独立 runner 的九项断言与执行侧测试分离，且覆盖新操作者输入、确认、空输入、缺失确认标志、非法运行标签、冲突、提交前失败、重启／幂等、未知 Project 和静态关闭态。
- 本证据仅确认当前 hash 在合成 SQLite、单用户、单进程和隔离临时副本内的受控闭环；不确认真实 Tauri/IPC、真实路径／个人数据、耐久／恢复、导出、权限设置、Alpha、风险关闭、冻结、基线恢复或 Stage 4。
