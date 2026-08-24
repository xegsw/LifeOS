# LIFEOS-P3-057 PM Evidence Manifest

- PM 验收方式：在项目根目录独立执行 P3-057 新 runner；runner 仅在系统临时目录建立合成 SQLite，结果写入本目录。
- 新 runner 复跑：退出码 0；P1 312 PASS / 0 FAIL，P2 2 PASS / 0 FAIL，P0=0、Not Implemented=0、Unknown=0。
- 当前 SQL hash：`bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`；与任务 Evidence 一致。
- P3-031 合同入口：先复制到 `/private/tmp/lifeos-p3-057-pm.UZaS4h/P3-031` 后运行复制品，退出码 0；P0 18 PASS、P1 29 PASS、P2 27 PASS，合计 74/74 PASS。
- PM 未修改候选 SQL、原合同入口、历史 Review 或历史 Evidence。

| 文件 | SHA-256 |
|---|---|
| `fresh_independent_results_pm.json` | `74a7e05ccfceac06e55a78c701439485df617ba063dd2bbeff6c0cf4134f9e44` |
| `p3_031_contract_results_pm.json` | `cd4f7af5e3e3a814a2c064df44b96b25150f80caede8897d62206f61eadacbc2` |
