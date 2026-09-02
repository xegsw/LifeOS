# Precontact Allowlist

Only the following inputs and destinations may be touched by this review.

## Read-only frozen / historical inputs

- `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation_acceptance_basis_freeze.md`
- `lifeos/tasks/LIFEOS-P3-143_acceptance_freeze_manifest.json`
- The exact commit object `767301fb051d11a6bf11488413f8b03aabfc2d99` and only its declared P3-143 candidate / Closure paths after post-seal fixed-input binding.
- `lifeos/engineering/LIFEOS-P3-143/evidence/root_authority_closure.json`
- `lifeos/engineering/LIFEOS-P3-143/FINAL_MANIFEST.json`
- `lifeos/deliverables/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- Exact, frozen P3-142 inputs named by the P3-143 freeze manifest and task contract.
- The task-card-required governance, architecture, and product-baseline files already read during startup.

## Review-owned writable destinations

- `lifeos/reviews/LIFEOS-P3-143/independent-re-review-1/`
- One new canonical, non-symlink direct child of `/private/tmp`, created only after the candidate's closed profile and run-id grammar are bound. It may contain only the review-owned synthetic runtime, DB, build cache, marker, and non-content evidence.

## Prohibited methods

- No broad inventory (`find`, `ls`, or `rg --files`) of candidate, engineering, review, deliverable, `/private/tmp`, Pilot, Keychain, or user-data roots.
- No use of the candidate's verifier or tests as independent proof; candidate tooling may only be compared or attacked after review-owned test design and controls are sealed.
- No writes outside the review directory or the single validated temporary root; no candidate, history, PM-ledger, product, or governance modification.
