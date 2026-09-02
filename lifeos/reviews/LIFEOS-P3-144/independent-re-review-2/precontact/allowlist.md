# P3-144 independent re-review-2 pre-contact allowlist

This list is effective only after the accompanying pre-contact seal verifies.
It is deliberately narrow and does not authorize a path probe outside the
listed read/write targets.

## Read before seal

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md`
- `lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop_acceptance_basis_freeze.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`
- `lifeos/CI_CD_GOVERNANCE.md`
- the task-directed sections of `lifeos/PM_OPERATING_MODEL.md`,
  `lifeos/ROLE_MATRIX.md`, `lifeos/STAGE_GATES.md`, and
  `lifeos/architecture/LifeOS架构基线V1.0.md`

## Read after seal

- The exact P3-144 Closure-2 report and Manifest named by the task.
- The prior `independent-re-review-1` report, including its full Closure List.
- Read-only P3-144 candidate fixed at commit `461423b3` (full SHA verified
  after seal), its required source/baseline inputs, and its CI registration.
- Only the named P3-144 Closure-2/previous-review materials needed for
  lineage, closure coverage, and independent verifier assertions.

## Write

- Only `lifeos/reviews/LIFEOS-P3-144/independent-re-review-2/`, excluding all
  prior review directories.
- Only the fixed synthetic root
  `/private/tmp/lifeos-p3-144-independent-review-v1`, with a review-owned
  ordinary marker and review-owned non-sensitive DB/fixtures; cleanup is
  allowed only after marker validation.

## Execution

- Offline Cargo/Rust/Tauri tools and local macOS AX/screenshot facilities for
  the review-owned synthetic App only.
- No network request, real Provider request, proxy, redirect, real credential,
  real content, or non-allowlisted filesystem target.
