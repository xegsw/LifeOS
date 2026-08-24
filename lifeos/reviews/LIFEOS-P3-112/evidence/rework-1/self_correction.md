# Rework runner 包内自纠正记录

- 发生时间：2026-08-24 Asia/Shanghai。
- 第一次 rework runner 已以预存离线 Cargo 执行 test/build；在随后静态审计阶段，Python 正则写成了双重转义，触发 `re.error: missing ), unterminated subpattern`。
- 该错误发生在 P3-112 自有 runner，尚未形成任何候选质量结论；未修改 P3-111、未访问 Pilot-2、未启动真实 app、未联网。
- 修正：将 UI `invoke(...)` 扫描模式改为正确的原始正则；精确清理 `/private/tmp/lifeos-p3-112-review-v1` 后，从空根重跑完整 M-005～M-013。
- 处理性质：执行侧提交前的同范围自检修正，不计正式 Rework，不改变 Frozen ABF 或 PM 已记录的正式 Rework 1/2。

## 第二次运行后的输出判读修正

- 第二次完整运行已实际完成离线 \`cargo test\`（退出码 0）和 \`cargo build\`（退出码 0），但测试通过数提取模式仍为双重转义，未能从日志中读取 \`8 passed\`，使 M-005 误报失败。
- 同次运行的自有初始 Evidence 载荷核验把 P3-111 后续产生的同级 \`rework-1/\` 历史后继包当作初始 37 文件载荷的 extra；该目录不属于其冻结的 Initial Manifest 载荷。将自有核验的排除范围明确为 \`disposable/\` 与该历史后继 \`rework-1/\`，而 Rework 38 文件载荷仍逐项核验。
- 两项均仅修正 P3-112 runner 的结果提取／历史载荷边界；不改动 P3-111 候选、冻结 ABF 或任何被评审 Evidence。将再次精确清理 \`/private/tmp/lifeos-p3-112-review-v1\`，从空根完整重跑 M-005～M-013。
