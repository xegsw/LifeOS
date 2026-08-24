# LIFEOS-P3-063 PM Evidence Manifest

## PM 隔离复跑

- 复跑方式：将 `lifeos/engineering/LIFEOS-P3-063/` 复制到 `/private/tmp/lifeos-p3063-review.eAF6kn/LIFEOS-P3-063/` 后执行；未覆盖执行侧 Evidence 或工程资产。
- 命令：`scripts/run_demo.sh`、`scripts/run_tests.sh`。
- 结果：demo 退出码 0；测试退出码 0；7 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。
- 输入实现 hash 与执行侧 Manifest 一致：`src/mvp.py` `f35f5651477d1a6fd8cc6e16339b3c63d59ada23c7d00b10ad2954bf72bb632f`；`scripts/run_demo.py` `98709bb7c41797d7b3d733d3e50cd00f4a027a00e5f309fd800fc7bbf24c79f0`；`scripts/run_tests.sh` `8d3620afd62840739eb79fccd96851bf140cc32aa5e8f839a8bb8bc67eb4b3ee`；`tests/test_mvp.py` `359f7495c6b40625ae5e0a603e686fcabf0b1b8975a1c480378e7cacfc9f76f2`。

## PM 反向验收

- 通过：事务提交后回执、提交前注入失败不报成功、幂等冲突可见、重启读取、受控 Project 恢复、AI 关闭和无外部动作均有受控测试证据。
- P1：`scripts/run_demo.py` 将原文、幂等键和下一步确认文本固定在脚本内，没有面向操作者的受控本地输入／确认入口。因此不能证明任务卡要求的“用户输入一条记录”和“用户显式确认下一步”，只能证明程序化固定夹具路径。
- 结论：执行侧的技术测试保留为 Rework 输入；不得作为可真实使用 MVP、独立复评、真实能力启用、风险关闭、冻结或 Stage 4 的依据。

## Rework 提交复核

- 用户授权 D-0273 后提交的交付物仍描述固定脚本路径；`scripts/run_demo.py`、`tests/test_mvp.py`、`evidence/test_results.json` 与执行侧 Manifest 的 hash 和 7 项用例均未变化。
- 工程目录中没有 D-0273 要求的操作者输入／确认入口文件；`run_demo.py` 仍固定原文、幂等键和下一步确认文本。
- 结论：未收到可核验的 Rework 实现或 Evidence；无需重复执行 PM 复跑，P1 继续存在。

## Rework PM 隔离复跑（D-0275）

- 复跑方式：将更新后的工程目录复制到 `/private/tmp/lifeos-p3063-rework-review.ov6h1D/LIFEOS-P3-063/`；未覆盖执行侧或历史 Evidence。
- 正常路径：以独立的 `--synthetic-only --text 'PM复核合成原文' --idempotency-key 'pm-rework-001' --next-step 'PM复核显式确认' --run-id pm-rework` 参数运行，退出码 0，显示受控闭环成功。
- 全量测试：退出码 0，11 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。
- 负路径：空 `--text` 返回“保存失败：原文与幂等键均不能为空”，退出码 1，未显示“已保存”。
- hash：`run_demo.py` `8eaff37b5b108f7046455e9752561a590f4ff7ffa27882dfd60245df9b5e04e4`、`run_demo.sh` `82e3489a1e551573b17c2b40b230dc8767eae02f5a986aeb6cd5a2983d8da694`、`tests/test_mvp.py` `dd0e464cce7becefcd6959fc2768176c6e09516853c4059330bdcc2eb3ecdcf8`，均与执行侧 Manifest 一致。
- 结论：D-0271 的 P1 已由操作者参数入口及 4 项端到端正／负测试解决；该结论仍严格限于合成 SQLite 受控边界。
