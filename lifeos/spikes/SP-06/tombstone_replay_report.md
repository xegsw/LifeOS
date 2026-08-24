# Tombstone and restriction replay report

Tests T21-T25 prove both arrival orders: tombstone before an old upload rejects it; an accepted old version followed by a newer tombstone makes every version inactive. Revoked Authorization blocks old queued work, and disconnected Source blocks old read-derived candidates. Tombstone/restriction generations are server-authoritative and must be loaded before restore, import, reconnect, queue claim, or model publication. No production backup or cross-process implementation is claimed.
