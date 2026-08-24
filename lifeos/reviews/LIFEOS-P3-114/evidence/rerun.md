# LIFEOS-P3-114 rerun instructions

Run from the repository root. These commands only parse static JSON, calculate SHA-256, inspect the fixed synthetic fixture and verify exact temporary-root cleanup. They do not run an app, database, model, network, external source or real-data path.

```bash
python3 lifeos/reviews/LIFEOS-P3-114/evidence/tools/verify_candidate_integrity.py
python3 lifeos/reviews/LIFEOS-P3-114/evidence/tools/verify_counterexamples.py lifeos/reviews/LIFEOS-P3-114/evidence/fixed_counterexamples.json
python3 -m json.tool lifeos/reviews/LIFEOS-P3-114/evidence/results.json
test ! -e /private/tmp/lifeos-p3-114-product-review-v1
```

The submitted manifest is non-self-referential. Verify every listed file against its SHA-256 and byte count; do not infer this candidate-only review to be a freeze, risk action, real-capability authorization or Stage 4 admission.
