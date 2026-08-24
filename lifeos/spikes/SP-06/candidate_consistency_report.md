# Candidate consistency report

Candidate Action/Decision/Link content remains L1 Derivation by default. The replay proves that acceptance, edited acceptance, and rejection require an explicit user operation and matching object version. Concurrent decisions are preserved as explicit conflicts; AI regeneration cannot move an Artifact current pointer or overwrite user-confirmed state.

Materializing every candidate as L3 adds an object version, feedback projection, conflict path, tombstone/restriction participation, queue fences, audit entry, and user-resolution state for each object type. This is materially more complex than L1 display. Recommendation: keep all three candidate types at L1 in V1 unless each type later passes an independent L3 value and UX test; this needs PM confirmation.
