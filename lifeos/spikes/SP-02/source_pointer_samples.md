# SP-02 Source Pointer Samples

Machine-readable samples are in `source_pointer_samples.json`.

- File pointer: Source + Artifact + exact observed Version + relative path.
- Heading pointer: adds heading text, with file/nearby-text fallback.
- Block pointer: adds explicit block token, with heading/file fallback.
- Gap pointer: retains the last observed version and a scope token, states `source_unavailable_not_latest`, and never pretends to resolve the current file.

Paths are display/return locators, not Artifact permanent identity. Pointer resolution must re-run scope, exclusion, connection and reachability checks.
