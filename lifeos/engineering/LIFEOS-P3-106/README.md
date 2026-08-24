# LIFEOS-P3-104 controlled Tauri candidate

This directory is the only mutable engineering scope for P3-104. It contains a
real Tauri 2 debug desktop candidate with local static HTML/CSS/JS, exactly
three registered IPC commands, and a backend-owned SQLite path.

## Frozen runtime boundary

- `capture_record`: accepts only the three fixed non-sensitive text/key probes
  compiled into both the UI and backend. Its request object rejects unknown
  fields. A shadow SQLite candidate is validated and atomically renamed before
  success is returned.
- `get_today`: accepts a strict empty request and returns validated records,
  source/identity fields, and a minimal audit summary.
- `runtime_status`: accepts a strict empty request and reports the explicit
  offline/AI-disabled/capability-closed state.
- The renderer receives no Tauri plugin permission. Unknown invoke commands are
  absent from `generate_handler!` and therefore denied.
- The backend requires `LIFEOS_P3_104_DB_PATH` to be an exact direct child of
  `/private/tmp/lifeos-p3-104-*/capture.sqlite`; the renderer cannot supply or
  observe this path.
- `rusqlite` uses its `bundled` feature. This is disclosed in `Cargo.toml` and
  the frozen lock inventory; SQLCipher is not enabled.

No clear/delete/export/Vault/model/network/sync/updater/telemetry command or
plugin exists. No retained pilot path or personal content is present.

## Offline verification

After the one-time Frozen bootstrap and programmatic `Cargo.lock` freeze:

```sh
cd lifeos/engineering/LIFEOS-P3-104
sh scripts/offline_verify.sh
```

The script sets `CARGO_NET_OFFLINE=true`, uses the task-local target directory,
runs deterministic static and Rust tests with `--locked`, and performs a debug
Tauri build without creating a release bundle.

## Actual app Evidence fixture

```sh
cd lifeos/engineering/LIFEOS-P3-104
sh scripts/launch_evidence_app.sh
```

This recreates only `/private/tmp/lifeos-p3-104-app-evidence`, writes the fixed
sentinel, and starts the already-built debug binary. The app must then be
operated through the Mac UI; `file:`, Chrome, HTTP, localhost, mocks, and static
accessibility exposure do not count as dynamic Evidence.

