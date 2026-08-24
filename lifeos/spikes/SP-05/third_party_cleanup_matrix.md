# Third-party mock cleanup matrix

| Mode | Reported state | Active use |
|---|---|---|
| success | `physically_cleaned` | blocked |
| delayed | `physical_cleanup_pending` | blocked |
| unsupported | `vendor_limited` | blocked |
| failure | `physical_cleanup_failed` | blocked |

No real vendor was contacted. `vendor_limited` and `physical_cleanup_failed` are never represented as complete deletion.
