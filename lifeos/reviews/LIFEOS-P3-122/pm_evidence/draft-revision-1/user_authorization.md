# LIFEOS-P3-122 Draft Revision 1 User Authorization

- Date: 2026-08-25 CST (+0800)
- User statement: `授权修订 P3-122 Draft，以 P3-116 实际 DOM/CSS/视觉为强制继承基线。同时取消本任务的模型限制`
- Authorized Draft change:
  - P3-116 current `index.html`、`styles.css`、`app.js`、fixtures、visual/interaction contract、Token 与 page-specific DOM/class 成为强制视觉实现基线。
  - P3-121 current UI 不再是视觉 positive input；只允许从 P3-121 承接 Tauri shell、三 IPC Runtime 与最小 adapter source。
  - 保留主机无关 viewport、actual Tauri、Runtime failure-closed 与完整 Final Manifest lineage 目标。
  - 取消固定单一 Codex 模型／推理档位限制；执行可使用项目规则允许的模型白名单并记录实际配置，模型变化不得改变 Frozen ABF 或质量门槛。
- Not authorized by this statement:
  - 创建 P3-122 engineering／temporary root或执行 Tauri／DB／IPC；这些仍等待独立 synthetic-only 边界确认。
  - 使用项目白名单外 Codex 模型。
  - 访问 Pilot、真实 DB／路径／文本、网络或产品模型。
  - 修改 P3-116、P3-120、P3-121 历史资产；冻结产品资产；关闭风险；独立复评；Stage 4。
- Historical preservation: D-0490 Draft task/ABF exact snapshots are stored under `lifeos/reviews/LIFEOS-P3-122/pm_evidence/draft-revision-1/before/` and remain read-only.
