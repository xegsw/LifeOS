# P3-113 Rework 1 evidence rerun

Run from the repository root. These commands only parse text/JSON, compute hashes, inspect the exact task-local temporary-root absence, and never run an app, database, model, network or external source.

```bash
for f in lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/*.json; do python3 -m json.tool "$f" >/dev/null; done
python3 -c 'import glob,json; rows=[json.load(open(p)) for p in glob.glob("lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/*.json")]; assert len(rows)==10; assert all(r["status"]=="PASS" for r in rows)'
shasum -a 256 lifeos/deliverables/LIFEOS-P3-113_human_centered_dual_domain_self_use_mvp_product_rebaseline_rework_1.md lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/*.json lifeos/reviews/LIFEOS-P3-113/evidence/rework-1/rerun.md
test ! -e /private/tmp/lifeos-p3-113-product-rebaseline-v1
```

Compare the resulting hashes to `MANIFEST.md`. The Manifest is non-self-referential and deliberately excludes its own hash. Also verify the protected initial deliverable, initial Evidence Manifest, PM Review and PM initial Manifest against `initial_asset_integrity.json`; do not access Pilot-2 or any other restricted path.
