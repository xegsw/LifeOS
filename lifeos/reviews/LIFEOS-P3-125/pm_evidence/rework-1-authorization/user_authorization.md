# LIFEOS-P3-125 Rework-1 Authorization

- Date: 2026-08-26
- User statement: `授权 P3-125 同任务最终窄整改。`
- Authorized task: `LIFEOS-P3-125`
- Authorized round: final same-task narrow remediation, `Rework 1/1`
- Frozen basis: existing `ABF-P3-125-v1`; unchanged.
- Governing remediation boundary: `lifeos/reviews/LIFEOS-P3-125_pm_review.md`, section `Rework 1/1 最终窄整改边界`.
- Allowed result: remove the production task-ID fixed parent so the single build-time `LIFEOS_RUNTIME_ROOT` is the sole Runtime-root authority; close existing M-001 through M-012 Evidence, mutation, history, Manifest and cleanup requirements; record independently verifiable actual model/effort before engineering action.
- Allowed writes: only P3-125 task-owned engineering/deliverable/Rework Evidence paths already authorized by the task card, plus the fixed `/private/tmp/lifeos-p3-125-runtime-root-config-v1` execution root.
- Protected assets: task card, Frozen ABF, source allowlist, authorization freeze assets, P3-122/P3-124 history, and P3-125 initial candidate/Evidence/delivery remain read-only; Rework Evidence must not overwrite initial Evidence.
- Prohibited: directory, data, IPC, schema/API, UI, architecture, product capability, real-data, network/model-product, risk, freeze or stage expansion.
- Stop condition: if actual model/effort cannot be independently recorded, stop before Rework engineering action. If Rework-1 does not meet the unchanged ABF, close P3-125 as `Closed — Acceptance Not Met`; no further same-task Rework.
- Non-effect: no P3-126 creation, no risk/freeze change, and no Stage 4 advancement.
