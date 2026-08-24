#!/bin/sh
set -eu

shasum -a 256 \
  lifeos/reviews/LIFEOS-P3-080/pm_evidence/MANIFEST.md \
  lifeos/reviews/LIFEOS-P3-080/evidence/MANIFEST.md \
  lifeos/reviews/LIFEOS-P3-080/evidence/independent_blackbox_runner.py \
  lifeos/reviews/LIFEOS-P3-080/evidence/independent_results.json \
  lifeos/reviews/LIFEOS-P3-080/evidence/independent_snapshot.json \
  lifeos/reviews/LIFEOS-P3-080/evidence/independent_runner.log \
  lifeos/engineering/LIFEOS-P3-079/src/integrated_runtime.py \
  lifeos/engineering/LIFEOS-P3-079/scripts/operator_cli.py
