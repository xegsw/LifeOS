# P3-141 Phase A 写入白名单（预接触）

允许写入：

1. `/Users/xxe/.codex/worktrees/971c/No.2/lifeos/engineering/LIFEOS-P3-141/**`
2. `/private/tmp/lifeos-p3-141-controlled-pilot-v1/**`（仅合成运行时、构建缓存、SQLite、bundle 和临时截图；最终必须精确清理）

允许只读：

1. 本 worktree 内任务卡、ABF、固定输入、P3-137/138/139/140 指定文件及定向规则。
2. `/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/candidate/**`（只读候选基线）。
3. `/Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/evidence/FINAL_MANIFEST.json` 与 `/Users/xxe/.codex/worktrees/b381/No.2/lifeos/engineering/LIFEOS-P3-139/evidence/FINAL_MANIFEST.json`（固定谱系）。

绝对禁止：任何真实 Pilot、既有 Pilot、真实 DB、真实路径、真实文本、真实 Health、凭据、真实 Provider、网络目标或外部系统；禁止这些目标的 access、exists、stat、inventory、hash、copy、create、cleanup。禁止写 PM 账本、风险、冻结、Stage、评审根或 `lifeos/deliverables/`。

cleanup 仅可使用字面量 `/private/tmp/lifeos-p3-141-controlled-pilot-v1`；禁止 glob、父目录删除、递归清理任何其他根。
