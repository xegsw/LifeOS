# Constraint inheritance report

- Strict multi-input Derivation: `derivation-multi-v1` inherits `client_secret`, local-only, no external disclosure, and 7-day retention.
- Legal subset: `derivation-subset-v2` is a new Derivation, excludes `artifact-client`, and discloses `1 restricted input omitted`.
- Empty external intersection: request `r32` is denied and creates no output.

Project, folder, tag, wiki-link, candidate Link, and user confirmation are not authorization sources and cannot widen this envelope.
