# LIFEOS-P3-120 Rework-2 Final Manifest Closure 测试设计

## 授权、范围与停止条件

- 权威输入：`lifeos/reviews/LIFEOS-P3-120_pm_review.md`，其状态为 `Rework 2/2 / User Adopted / Final Manifest Closure Authorized / Acceptance Basis Unchanged`。
- 允许写入：本目录和现有 P3-120 专项交付物。禁止重跑 `.app`、访问或创建 Runtime 临时根、修改 candidate／ABF／初次 Evidence／既有 `evidence/rework-1/` 文件、项目账本、Pilot、真实数据、网络或模型。
- 目标：关闭 PM-R1-P0-001（L1-7/L1-8/L1-10、I-10、M-015）：提供一个非自指、当前完整且可变异验证的 retained-asset Manifest；初次 Manifest 的旧交付物 hash 作为历史快照保留，不伪称为当前值。
- 停止条件：任何 history/candidate/rework asset 漂移、清单中出现链接／非普通文件、缺项／额外项、当前交付物未被 final Manifest 覆盖，或 mutation control 失败，均为 `NOT PASS`；不得通过修改这些资产消除失败。

## 固定 retained-asset 分层

1. **current candidate**：`candidate-inventory.json` 所列的 P3-120 candidate 常规文件，逐项复算 bytes/SHA-256，并拒绝 missing/extra/link/type drift。
2. **initial historical layer**：初次 `evidence/MANIFEST.md` 的 101 条记录。其原交付物 hash `ef644706…` 仅为历史提交快照；其余 100 条历史 payload 必须仍匹配，旧交付物不应被称为当前值。
3. **Rework-1 layer**：`evidence/rework-1/MANIFEST.md` 声明的 59 个 payload 和该 Manifest 本身，逐项复算。
4. **current delivery and authority**：当前专项交付物和本次 PM Review 各自以当前 bytes/SHA-256 进入 final Manifest。
5. **Rework-2 closure layer**：本目录除 `FINAL_MANIFEST.json`（唯一自排除项）外的所有普通 retained 文件，包含测试设计、verifier、builder、mutation runner、draft payload、verification results 和 mutation results。

## 测试矩阵

| 测试 ID | 动作 | 实际 Evidence | 预期 |
|---|---|---|---|
| FM-001 | 生成 draft payload，复算 five-layer inventory | `scope-payload.json` | control PASS；当前交付物、candidate、initial historical、Rework-1 与 PM Review 均有明确层级 |
| FM-002 | 在 disposable copy 运行未改动 control | `mutation-results.json` | control PASS，证明 verifier 对未篡改 payload 可用 |
| FM-003 | mutation：遗漏当前交付物、payload hash 改动、额外文件、历史/当前 lineage 混淆 | `mutation-results.json` | 每项独立 fail closed，且 disposable root 被精确清理 |
| FM-004 | 构建非自指 final Manifest，运行只读 final verifier | `FINAL_MANIFEST.json`、终端复跑命令 | 所有层逐项 bytes/SHA-256/type/missing/extra 通过；Manifest 不包含自身 |
| FM-005 | 更新专项交付报告并纳入 current delivery | final Manifest current-delivery row | 当前交付物的 hash 存在且与磁盘一致；初次旧值只标为 historical |

## Pass 公式

`FM-001` 至 `FM-005` 全部 PASS；mutation pristine control 必须通过；四项实际 mutation 必须各自以预期原因失败；disposable copy 不残留；final verifier 对 final Manifest 返回 0；M-015 不再有 Not Implemented。该自检不是 PM 重新验收或风险／冻结／阶段结论。
