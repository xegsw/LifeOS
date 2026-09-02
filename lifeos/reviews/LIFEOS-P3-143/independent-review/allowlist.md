# LIFEOS-P3-143 independent review — precontact allowlist

This allowlist is effective before first candidate/engineering contact. It is a read-only contract except for files created in this review output directory and the one exact review-owned disposable root named below.

## Permitted fixed and review paths

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation_acceptance_basis_freeze.md`
- `lifeos/tasks/LIFEOS-P3-143_acceptance_freeze_manifest.json`
- `lifeos/ACCEPTANCE_GOVERNANCE.md`, `lifeos/CI_CD_GOVERNANCE.md`, and the task-specified sections of `lifeos/PM_OPERATING_MODEL.md`, `lifeos/ROLE_MATRIX.md`, and `lifeos/STAGE_GATES.md`
- `lifeos/architecture/LifeOS架构基线V1.0.md`, `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`, and `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- Exact P3-142 predecessor paths frozen in `lifeos/tasks/LIFEOS-P3-143_acceptance_freeze_manifest.json`, read-only.
- Exact P3-143 review subjects, read-only and only after this seal: `lifeos/engineering/LIFEOS-P3-143/`, `lifeos/deliverables/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`, and `lifeos/reviews/LIFEOS-P3-143_pm_review.md`.
- Review-owned writes only: `lifeos/reviews/LIFEOS-P3-143/independent-review/`.
- Review-owned temporary runtime only: `/private/tmp/lifeos-p3-143-independent-review-v1`; no other `/private/tmp` root is allowed.

## Permitted real-gate boundary if and only if later reached

- The user may manually interact with the review App and manually provide a DeepSeek key in its UI; the reviewer has no access to that value.
- Only a user-triggered HTTPS action to `https://api.deepseek.com` may occur, and only after documented synthetic gate Pass. Evidence remains non-content and excludes Key, prompt, response, model identifier and error body.

Any path, data source, Keychain item, provider target, network target, tool or temporary root not listed above is prohibited.
