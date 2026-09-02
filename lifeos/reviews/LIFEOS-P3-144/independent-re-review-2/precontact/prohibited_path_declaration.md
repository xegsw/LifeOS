# P3-144 independent re-review-2 prohibited-path declaration

The following path is absolutely prohibited throughout this review, including
preflight, test setup, process launch, cleanup, and any failure handling:

`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`

No command, script, library call, hash, manifest, shell expansion, traversal,
cleanup routine, existence test, metadata query, open, read, write, creation,
or deletion may target that path or anything beneath it, including its DB or
any user content. The path is intentionally excluded from every allowlist,
inventory, source scan, fixture, cleanup target, and command argument.

Also prohibited in this Phase-B review: real Providers, real credentials,
real text, network access, any other Provider, and modifications to the
candidate, task contract, ABF, historical Review/Evidence/Manifest, or PM
ledger.

If any prohibited boundary is touched, the attempt is invalidated immediately;
it is not remediated by a later seal, cleanup, or substitute Evidence.
