# LIFEOS-P3-072 Authorized Rerun Evidence Manifest

All listed artifacts belong to the authorization granted in D-0302. The
pre-existing P3-072 directory and its evidence were not modified or used as
this submission's evidence.

- `src/sandbox_export.py`: `76997bded53f6aa1c943deb8705fb725ba03385bb423d05f5916ea3862c070fb`
- `tests/test_sandbox_export.py`: `e3392e0f5778f6daa31ad3e39e69d5364926b166eb5ff458c440be59f28e08a5`
- `scripts/run_tests.py`: `0a4d2dc3c705e32716ac5e415d947f5b00d50aa20d50f0770879bc5c14a7db8a`
- `scripts/make_evidence.py`: `ac88a6d984238000859c5e8429abe16ae4f6b74e73354814639b6062a94f6fd2`
- `evidence/test_results.json`: `0757dcd6ff55d3d9caf10023b5e3225fdc059239c087b2f6df80fc01f7f2ff56`
- `evidence/export_receipt.json`: `dc7e89e8037fbff04406b84b120112ff90ca66ea4f724c40e679124cb69d4847`

## Verification summary

- `python3 scripts/run_tests.py`: 8 PASS / 0 FAIL, exit code 0.
- `python3 scripts/make_evidence.py`: captures only a redacted receipt, then
  removes the newly-created system temporary sandbox and its sole output.
- Negative coverage blocks and audits non-exact confirmation, mismatched
  preview token, source/version mismatch, unknown content, conflict, revocation,
  tombstone, a state change after preview, repeat export, collision, path escape,
  and injected write failure.
- A successful operation uses only a fresh `tempfile.mkdtemp` child of the
  system temporary directory and atomically publishes one new file via a link
  that cannot overwrite an existing destination.
- No network, Tauri/IPC, Vault, real DB, cloud, sync, multi-device, L3,
  external-user, or non-temporary-path capability is present. This does not
  implement real file export and does not affect R-0040, freeze, baseline, or
  Stage 4 status.
