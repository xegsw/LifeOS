# Closure-2 bounded continuation

ZIP central-directory names with unset UTF-8 flag are decoded CP437-to-bytes then strict UTF-8 when valid; no replacement decoding, fuzzy names, or arbitrary XML trial reads. Match only the same fixed root/standard-directory English/Chinese export-name allowlist. Canonical duplicates fail, and HealthData root validation remains. Real observed member names are not copied to this design.

Metadata-only selection now yields a unique XML of 607353495 bytes. XML hard cap becomes 768MiB; file cap256MiB, member ratio200, directory4096/8MiB, records2million, token64KiB/depth32, database~1GiB, source128 and projection10000 remain. Unopened attachment aggregate bytes do not consume XML budget. Parser280s/application300s/wrapper330s are finite budgets. Streaming source data stays in local process/DB, never Agent output.

Resume only the exact previously-created target, via owner/mode/nlink/no-symlink checks, birth time within prior execution receipt window, exact expected schema, all data tables empty and meta revision zero. Never recreate/overwrite/migrate/reset. Create a new private closure-2 attempt marker and a distinct engineering authorization-bound invocation record; old attempt marker retained. One retry only; failure retains everything.

Validate synthetic encoded names, ambiguity/path spoofing, target origin rejection, foreign data rejection, retry marker, same-pipeline scoped-size success and budget-failure rollback, existing health/model guards; then build and perform one redacted real retry.
