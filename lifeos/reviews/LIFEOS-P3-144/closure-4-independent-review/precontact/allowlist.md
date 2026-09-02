# Precontact Allowlist

Before seal, reads are limited to:

- `/Users/xxe/Documents/No.2/AGENTS.md`
- governance, role, stage and templates named by the P3-144 Task Contract
- P3-144 Task Contract, Frozen ABF and freeze manifest read from Git commit `86d764d9`
- main ledgers read from Git commit `86d764d9`
- this review-owned precontact directory

After seal, additional allowed targets are:

- fixed candidate and declared P3-144 inputs at Git commit `86d764d9`, read-only
- predecessor state at Git commit `987dd42d`, read-only
- repository path `lifeos/reviews/LIFEOS-P3-144/real-use/real-use-receipt.json`, read-only and non-content fields only
- review output path `lifeos/reviews/LIFEOS-P3-144/closure-4-independent-review/`
- sole synthetic runtime root `/private/tmp/lifeos-p3-144-independent-review-v1`
- review-owned disposable mutation material beneath the sole synthetic runtime root

No other runtime root, Pilot, database, Provider, credential, network target or ambient application data is allowed.
