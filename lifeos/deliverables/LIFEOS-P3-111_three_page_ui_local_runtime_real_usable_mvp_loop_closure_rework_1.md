# LIFEOS-P3-111 Rework 1/2｜Evidence-only mutation specificity 收口

## 任务信息

- 任务 ID：`LIFEOS-P3-111`
- 执行轮次：正式 Rework 1/2（Evidence-only 窄整改）
- 执行 Agent：Codex；`gpt-5.6-terra + xhigh`（用户于 D-0451 确认）
- 当前状态：Completed — 包内 Rework 自检通过，等待 PM 验收
- 需要 PM 决策：Yes
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-111-v1`／`24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395`
- Frozen ABF 在本轮工程动作前核对：Yes；本轮未发现歧义，未修改 ABF。

## 执行摘要

- 修复了 `semantic_verifier.py` 的绝对 `/disposable/` 子串过滤：过滤依据改为相对所传 Evidence root 的直接子目录，因此位于任意祖先 `disposable/noop` 下的完整副本不再被错误排除。
- 新 runner 仅在全新 `evidence/rework-1/` 生成 Evidence；初次 Evidence 被只读复制为新 payload 输入，未覆盖或修改。candidate/runtime/UI 未改。
- 未篡改 `disposable/noop-final` 最终 payload 副本 exit 0，且 missing／extra／drift／semantic errors 全为空。
- 六类实际 mutation 在分别创建的 disposable 副本中各自 exit 1，并精确匹配预期 missing、hash drift 或 semantic reason；不是由路径或无关错误造成的非零退出。
- 最终 payload 38/38 文件可复算，root verifier PASS；所有 disposable 临时副本已移除。
- 未再次 capture；未打开、读取、hash、复制、覆盖或清理 Pilot-2／`capture.sqlite`；未联网。

## PM finding 对应整改

| PM finding | 本轮事实 | Evidence |
|---|---|---|
| `PM-CE-001`：未篡改 `/disposable/noop` 副本也失败 | `noop-final` exit 0，完整 38 文件 payload 无 missing／extra／drift／semantic error。 | `evidence/rework-1/semantic-verifier-result.json` |
| 六类非零不能证明特异性 | 六项均有独立实际副本、exit 1 与严格原因匹配；runner 对任何额外／缺少／错误 reason fail-closed。 | `evidence/rework-1/mutation-results.json`；`mutations/*.json` |
| 初次 Evidence／真实边界必须保全 | 初次三个关键 Evidence hash 不变；新 Evidence 无 Pilot 访问，candidate/runtime/UI 无本轮写入。 | `raw/rework-source-snapshot.json`；`MANIFEST.md` |

## 包内自检

- P0：0；P1：0；P2：0；Unknown：0；Not Implemented：0。
- 这一计数仅覆盖本轮已授权的 Evidence-only Rework。PM 的初次 P0 finding 已由本轮测试闭环处理，但只有 PM 复验可裁定正式 Rework 是否通过。
- 最终 manifest SHA-256：`16dbe0f05d825bca4f7e08f723dd5c3b7b90606bad0a4af1d9feaaea34641d22`；semantic result SHA-256：`d3afbc9e13a1a3bfc3b81b83cc878dfa3a2f2bb228ec6a4088b3fa8f5443f011`。
- 高风险 Evidence 结论跳过本地模型预检；该预检不得决定 P0 PM 验收。

## 角色与关卡

- 主责角色：本地 MVP 工程与数据生命周期（本轮仅 Evidence verifier／QA 整改）。
- 协审检查点：数据与来源（retained 零访问）、AI 信任安全（无网络／新能力）、独立 QA（mutation specificity 由后续 PM 复验）。
- 覆盖：ABF-I-10／I-11、ABF-M-011／M-012 的 Evidence、Manifest、disposable cleanup 子项；原有 UI／运行时结果只读保全，不以本轮重跑替代。
- 未覆盖为通过：PM 正式验收、用户对 PM Pass 的采纳、P3-112 全新隔离独立复评；不冻结、不关闭／重开风险、不进入 Stage 4。

## 会话与边界

- 执行方式：Reused Session；上一轮提交已结束并进入 PM Rework，用户明确授权同任务窄整改。
- 授权证据：本轮用户消息“继续执行 LIFEOS-P3-111 Rework 1/2”；D-0451 已采纳、授权 Evidence-only 整改并确认模型路由。
- 本轮重新读取：`AGENTS.md`、`CURRENT_STATUS.md`、P3-111 原任务卡／Frozen ABF、PM Review、初次 PM Evidence Manifest 与 noop counterexample、验收治理及模板。
- 未发现旧授权漂移；写入仅限 `lifeos/engineering/LIFEOS-P3-111/tools/`、`evidence/rework-1/` 与本交付物。

## 交付物

- [Rework 交付物](/Users/xxe/Documents/No.2/lifeos/deliverables/LIFEOS-P3-111_three_page_ui_local_runtime_real_usable_mvp_loop_closure_rework_1.md)
- [Rework Evidence Manifest](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-111/evidence/rework-1/MANIFEST.md)
- [最终语义／mutation 结果](/Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-111/evidence/rework-1/semantic-verifier-result.json)

## 需要 PM 决策

请在新隔离副本复验本轮 relative-path verifier、未篡改 control 与六类 precision mutation。仅在 PM Pass 且用户采纳后，才能新建 P3-112；本会话不自行推进。
