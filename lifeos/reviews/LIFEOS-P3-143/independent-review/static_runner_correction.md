# Static runner correction — IPC extraction

The first run, retained as `static_runner_results.json`, used a whole-file string-literal pattern and incorrectly counted command names from non-IPC code. It is an excluded review-tool artifact, not candidate negative Evidence.

The review-owned runner was corrected to parse only the declared `const IPC: [&str; 20]` block. The rerun is stored separately as `static_runner_results.rerun.json`; no candidate, fixed input, historical asset, runtime DB, Keychain item, network target, or real credential was contacted or modified during either run.
