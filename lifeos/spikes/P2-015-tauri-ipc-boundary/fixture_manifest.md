# Synthetic fixture manifest

The harness recreates only `work/` inside this disposable spike.

- `synthetic_vault/notes/allowed.md`: authorized synthetic Markdown.
- `synthetic_vault/.obsidian/`, `.hidden/`, `excluded/`: default-deny probes.
- `synthetic_vault/attachments/private.bin`: unauthorized attachment probe.
- `outside_boundary/`: synthetic out-of-scope target.
- `synthetic_vault/notes/escape.md`: symlink to the synthetic outside target.
- `authorized_export/`: the only write-authorized export root.
- `authorized_export/escape_dir`: symlink escape probe.

All bodies are fixed synthetic sentinels. No path discovery, real Vault, real user
file, network, cloud, model, third party, account, or paid resource is used.
