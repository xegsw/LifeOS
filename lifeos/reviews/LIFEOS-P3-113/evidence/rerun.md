# P3-113 Evidence rerun

All commands are read-only checks except `python3 -m json.tool`, which only parses and prints JSON. Run from repository root.

```bash
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/session_start.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/ledger_reconciliation.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/p3_111_boundary.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/frozen_asset_impact_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/product_definition_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/memory_semantics_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/home_question_advice_feedback_contract.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/cross_domain_scenario.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/safety_degradation_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/route_and_authorization_matrix.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/input_integrity.json >/dev/null
python3 -m json.tool lifeos/reviews/LIFEOS-P3-113/evidence/temporary_residue.json >/dev/null
find lifeos/reviews/LIFEOS-P3-113/evidence -maxdepth 1 -type f -print | sort
shasum -a 256 lifeos/reviews/LIFEOS-P3-113/evidence/*.json lifeos/reviews/LIFEOS-P3-113/evidence/rerun.md
test ! -e /private/tmp/lifeos-p3-113-product-rebaseline-v1
```

The resulting file list and SHA-256 values must match `MANIFEST.md`; `MANIFEST.md` deliberately does not hash itself. A rerun must also compare the relevant current-ledger entries and ABF SHA-256 recorded in `input_integrity.json` and `session_start.json`. It must not read, locate, hash or access the prohibited Pilot-2 path.
