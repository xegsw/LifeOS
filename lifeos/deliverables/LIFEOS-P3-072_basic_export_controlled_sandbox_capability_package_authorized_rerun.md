# LIFEOS-P3-072｜基础导出受控沙盒能力包：授权复跑交付物

## 结论

事实：在 D-0302 明确授权后，本次在全新、任务卡唯一允许写入的目录 `lifeos/engineering/LIFEOS-P3-072/authorized_rerun/` 完成干净重建与复跑。8 项受控合成测试通过（8 PASS / 0 FAIL，退出码 0）。此前 P3-072 未授权提交、PM Evidence 和原工程目录均未修改，也未被作为本次可采纳 Evidence。

本能力包只实现合成记录的预览→精确 `CONFIRM`→一次性新建系统临时沙盒文件→来源／身份／内容 hash 回执。它不是真实文件导出、R-0040 关闭、工程基线恢复、资产冻结或 Stage 4 准入结论。

## 实现事实

- 仅使用内存 SQLite 与非敏感合成记录；不存在真实 DB、用户路径或已有文件的读写。
- `preview()` 默认不写，披露来源、内容身份／版本／内容 hash、范围、目标类别、确认、覆盖及失败语义。
- 只有精确 `CONFIRM` 且 token 与当前预览一致时才尝试输出；确认前若状态变为 revoked/tombstoned，操作被阻断。
- 成功时只在新建的系统临时目录生成一个新文件。以临时 pending 文件写入、`fsync`、硬链接发布的方式避免覆盖；目标存在、路径逃逸、碰撞及写入失败均失败关闭。
- 写入失败或碰撞后会清理临时目录，无可见输出；所有阻断与失败均进入内存审计。
- 成功回执绑定 `source`、content identity/version/hash、plan hash、export hash 和文件名；项目 Evidence 只保留脱敏回执，运行生成的临时输出已删除。
- 静态与运行期边界均明确关闭：网络、Tauri/IPC、Vault、真实 DB、云、同步、多设备、L3、外部用户和非临时路径。

## 验收矩阵与结果

| 任务卡要求 | 覆盖结果 |
| --- | --- |
| 默认预览、精确确认和单次输出 | PASS：预览披露、精确确认、一次性限制 |
| 来源／版本／范围／确认绑定与回执 | PASS：来源、identity/version/content hash、plan/export hash 均核验 |
| conflict／撤回／tombstone／未知／确认错配 fail-closed | PASS：含预览后状态变化反例 |
| 越界路径、重名／覆盖、写入失败与半成品不留输出 | PASS：路径逃逸、已有目标、碰撞与注入写失败均为 0 可见输出 |
| 外部能力与非临时路径关闭 | PASS：边界断言与静态导入检查通过 |
| 合成临时输出清理 | PASS：复跑后无 `lifeos-p3-072-authorized-*` 临时目录残留 |

## 角色与关卡

- 主责：技术架构负责人——原子新建、临时沙盒限制、失败清理和可复现测试已验证。
- 协审：AI 信任与安全（明确确认、撤回／tombstone、fail-closed／审计）；数据／领域模型（来源、身份与版本／内容 hash）；产品／体验（“仅临时合成输出”及阻断语义可观察）。
- Gate 2／Gate 3／Gate 4：在严格合成、单进程、系统临时目录边界内通过。
- Gate 1／Gate 5：仅有限覆盖；不构成真实用户价值、真实导出或 Stage 4 依据。

## Evidence

- [授权复跑工程说明](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-072/authorized_rerun/README.md)
- [结构化测试结果](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-072/authorized_rerun/evidence/test_results.json)
- [脱敏导出回执](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-072/authorized_rerun/evidence/export_receipt.json)
- [Evidence Manifest](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-072/authorized_rerun/evidence/MANIFEST.md)

## 推断、建议与待确认

推断：在任务卡的受控合成边界中，实现满足“默认不写、精确确认、一次临时输出、失败关闭并清理”的能力包完成定义。

建议：交由 PM 进行一次正式验收；若 PM 通过，仍须创建全新隔离、只读的独立复评，再由用户决定是否采纳。

需 PM 确认：本交付物是否可进入上述正式 PM 验收。不得将它外推为真实路径／文件导出授权、R-0040 关闭、工程基线恢复、资产冻结或 Stage 4 准入。
