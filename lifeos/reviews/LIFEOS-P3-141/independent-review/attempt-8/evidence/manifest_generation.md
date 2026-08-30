# Receipt-bound review evidence Manifest

`evidence/tools/render_review_manifest.py` renders the exact schema accepted by the candidate's independent-receipt verifier. It rejects any linked or non-regular artifact and excludes exactly `FINAL_MANIFEST.json` (self reference) and the future `phase_b_pass_receipt.json` (which binds this fixed Manifest). The tree hash is SHA-256 over component-ordered `path-byte-length / path / content-byte-length / content` for every listed review artifact.

The Manifest is generated only after the provisional synthetic review is complete. Subsequent Phase-C-gate and cleanup records are supplemental: they are committed after the receipt-gate positive control and intentionally do not rewrite this bound Manifest.
