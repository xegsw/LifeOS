# LIFEOS-P3-126 Explicit Boundary Confirmation

- Date: 2026-08-26
- User statement: `确认 P3-126 仅使用 lifeos/engineering/LIFEOS-P3-126/、/private/tmp/lifeos-p3-126-clean-closure-v1 和全新合成 DB；P3-125 Rework-1 候选、Evidence、Review 全部只读；仅允许 LIFEOS_RUNTIME_ROOT 及 capture_record、get_today、runtime_status 三项 IPC；禁止对旧 P3-122 Runtime root 进行任何 access、stat、hash、create 或 cleanup；不访问 Pilot、真实 DB、真实路径、真实文本、网络或产品模型。`
- Interpretation: exact synthetic-only Tauri/IPC execution boundary confirmation for `ABF-P3-126-v1`.
- Allowed roots: `lifeos/engineering/LIFEOS-P3-126/` and `/private/tmp/lifeos-p3-126-clean-closure-v1` only, plus the task-specific deliverable/local-precheck paths stated in the task card.
- Allowed data/interfaces: fresh synthetic SQLite, build-time `LIFEOS_RUNTIME_ROOT`, and existing `capture_record`, `get_today`, `runtime_status` only.
- Protected inputs: all P3-125 Rework-1 candidate, Evidence and Review assets remain read-only.
- Explicit prohibition: no old P3-122 Runtime-root access, stat, hash, create or cleanup; no Pilot, real data/path/text, network or product model.
- Non-effect: no product/runtime/schema freeze, no risk change, no independent review creation, and no Stage 4 advancement.
