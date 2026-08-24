# LIFEOS-P3-114 Rework 1 rerun

Run from the repository root. The runner only reads frozen Markdown/JSON, verifies SHA-256 and byte counts, checks each Frozen ABF row's exact action/test/Evidence mapping, and tests the exact authorized temporary-root absence. It does not run an application, database, model, network, external source or real-data path.

```bash
python3 lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence/tools/verify_rework_mapping.py
python3 -m json.tool lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence/matrix_mapping.json
python3 -m json.tool lifeos/reviews/LIFEOS-P3-114/rework/rework-1/evidence/results.json
test ! -e /private/tmp/lifeos-p3-114-product-review-v1
```

Then compare every listed rework file with the non-self-referential `MANIFEST.md`. A successful rerun only shows that P3-114's evidence mapping has been corrected; it does not freeze P3-113, authorize a prototype, close risks or admit Stage 4.
