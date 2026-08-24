# Default-off capability matrix

| Capability | Config | Runtime negative test | Enablement status |
|---|---:|---|---|
| Real Obsidian Vault | false | throws DisabledCapability | Not requested |
| Real Tauri / IPC | false | throws DisabledCapability | Not requested; R-0040 remains Open / Conditional |
| Filesystem export / path scope | false | throws DisabledCapability | Not requested |
| Cloud / third-party model | false | throws DisabledCapability | Not requested |
| Vector index | false | throws DisabledCapability | Not requested |
| Sync / multi-device | false | throws DisabledCapability | Not requested |
| L3 actions | false | throws DisabledCapability | Not requested |
| External users | false | throws DisabledCapability | Not requested |

All rows are closed by immutable policy object plus executable negative tests. No UI, IPC or adapter bypass is present in this skeleton.
