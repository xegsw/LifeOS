# LIFEOS-P3-077｜本地受控权限设置运行时能力包

## 结论

- **事实：**在 `lifeos/engineering/LIFEOS-P3-077/` 新建了仅处理非敏感测试文本的 task-local SQLite 权限设置运行时、操作者 CLI、测试与 Evidence。
- **事实：**包内交付前自检在干净临时副本完成，结果为 **15 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**；覆盖首次操作、重复／幂等、撤回、关闭重开、正负反例、原子失败和审计追溯。
- **事实：**唯一、当前有效且精确绑定的 `grant` 在 `CONFIRM` 后才会返回 `allowed_local_synthetic`。当前有效 `deny` 优先；歧义、过期、撤回、确认缺失或绑定不匹配一律 fail-closed。
- **事实：**所有 allow／deny／拒绝回执都固定声明 `external_action: none`；没有网络、云、AI 消费、真实路径／文件、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户通道。
- **推断：**该最小实现可作为 PM 验收和后续全新隔离独立安全／体验复评的受控 Evidence 输入。
- **非结论：**不构成真实权限、真实 AI／云处理、R-0013／R-0014／R-0015／R-0021／R-0040 关闭、工程基线恢复、冻结或 Stage 4 准入。

## 运行时语义

操作者首先通过 `preview` 查看本次目的、位置、处理者、数据边界、默认拒绝和确认 token。决定必须精确绑定固定合成 Project、数据类别、目的、位置和处理者，且给出有效期、幂等键及 `CONFIRM`。撤回必须给出授权 ID、幂等键及 `REVOKE`。

消费门只查询当前未过期的精确绑定记录：存在 deny 时拒绝；仅有一项 grant 时允许本地合成决定；多 grant 时按歧义拒绝；其他情况默认拒绝。grant、deny、撤回和拒绝都写入 task-local 审计，保留原因、确认与幂等键。失败注入时 SQLite 事务回滚，测试确认不会留下权限半成品。

操作者入口：

```sh
python3 lifeos/engineering/LIFEOS-P3-077/scripts/permission_cli.py preview
python3 lifeos/engineering/LIFEOS-P3-077/scripts/run_self_check.py
```

## 自检、Evidence 与边界

完整的“验收标准 → 测试 → Evidence”矩阵、逐项结果、日志、快照、hash 和复跑方式见 [Evidence Manifest](../engineering/LIFEOS-P3-077/evidence/MANIFEST.md)。本任务只写入自身工程目录、交付物和 task-local Evidence；P3-065／P3-066、P3-075／P3-076 与项目账本保持只读。

未覆盖且明确非范围：真实身份、个人数据、真实 DB／路径／文件、生产耐久与物理故障、真实恢复、并发／WAL、Tauri/IPC、网络／云／第三方、导出、同步、多设备、L3 和外部用户。

## 角色与关卡

- 主责：Codex 工程执行；本包内自检通过。
- 协审视角（执行侧）：AI 信任与安全（显式确认、deny 优先、撤回和 fail-closed）；数据与来源（授权、确认和审计分离）；产品／体验（preview 与可见失败回执）；技术架构（task-local SQLite 与静态关闭态）。
- Gate 1–4：仅本受控合成能力的适用项已自检；Gate 5 与全部 Stage 4 Gate 未通过／不适用。
- 后续关卡：必须经 PM 验收、一次**全新隔离**独立安全／体验复评和用户采纳。资产保持 Not Frozen。

## 需要 PM 决策

需要。请 PM 验收本能力包并决定是否创建全新隔离独立安全／体验复评；不需要、也不请求在本任务中授权任何真实能力、风险关闭、冻结或阶段变更。
