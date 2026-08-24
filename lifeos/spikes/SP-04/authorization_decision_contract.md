# Authorization decision contract

`raw_decision ∈ {ALLOW, DENY, INDETERMINATE}`. Enforcement maps only `ALLOW` to execution; both `DENY` and `INDETERMINATE` fail closed to `DENY`.

An allow requires one currently valid Authorization to match all six dimensions—subject, complete input scope including exclusions, action, purpose, exact location/processor, and time—plus every mandatory processor-policy check and current runtime state. User confirmation can create or narrow a grant but cannot override processor qualification, unknown policy/subprocessor/region, default training/evaluation, retention/deletion failure, source restrictions, minimization failure, or credential blocking.

Every enqueue, execute, external send, output save, cross-Project display, re-derivation, candidate write, and long-task publish/index/recovery-package checkpoint is independently evaluated. The contract carries authorization set version, processor policy version, precise input digest, and lease version. A cache key additionally binds subject, Project, action, purpose, location, processor, and deterministic evaluation time.

This JSON-shaped contract is database-independent test material. It does not freeze a table layout, API, queue, policy language, or service boundary.
