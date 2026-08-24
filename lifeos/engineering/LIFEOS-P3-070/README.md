# LIFEOS-P3-070 Synthetic Export Plan

This is a controlled, in-memory plan and receipt drill. It never writes an
export, accesses a path, or connects to an external capability. `CONFIRM`
creates only a local confirmed-plan receipt with `external_action=none`.

Run `scripts/run_tests.sh` for the acceptance checks.
