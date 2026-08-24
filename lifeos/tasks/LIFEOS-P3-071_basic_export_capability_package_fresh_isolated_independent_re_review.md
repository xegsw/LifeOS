# LIFEOS-P3-071｜基础导出受控能力包全新隔离独立复评

仅限 P3-070 只读工程资产与合成数据，使用新隔离 Codex 会话（`gpt-5.6-terra` + `xhigh`，不得降级）。新会话先读 `AGENTS.md`、`CURRENT_STATUS.md`、本任务卡、独立评审和会话回复模板，并定向读取 P3-070 PM Review、R-0040、相关 P0／独立评审规则与冻结状态。

新写独立 runner，不得导入、调用或复制 P3-070 测试。仅在临时副本验证：计划默认不执行；来源／身份／版本／范围／目标类别可见；只有 `CONFIRM` 产生 `local_confirmed_plan_only` 且 `external_action=none`；无确认、错配、冲突、撤回、tombstone、未知输入 fail-closed 并审计；工程与 Evidence hash 只读保留；网络、路径、Tauri/IPC、Vault、真实导出、云、同步、多设备、L3、外部用户关闭。

不得写真实文件或路径，不关闭风险、不冻结、不恢复基线、不启用真实能力、不进入 Stage 4。输出 Review、Evidence Manifest、结构化结果与交付物。Pass 仅作合成计划能力包的 PM／用户输入。
