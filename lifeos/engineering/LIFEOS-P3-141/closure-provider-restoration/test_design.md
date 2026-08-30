# P3-141 Provider Restoration Closure test design

Scope is limited to the revision-2 provider delta.  The mutable candidate and all
new evidence remain under this closure directory; the runtime fixture, loopback
server, bundle target, and all transient state are confined to
`/private/tmp/lifeos-p3-141-provider-restoration-closure-v1`.

The positive path exercises all five profiles through their ModelPort probe and
inference envelopes, then verifies explicit save -> credential reference where
needed -> test -> enable -> one send.  The state-machine checks that only one
profile is enabled, that the first send persists its profile lock, that restart
does not resend the request, and that changing to another profile fails.

Negative protocol controls independently mutate Custom OpenAI-compatible
responses, envelopes, mode, credentials, request order, and HTTP behavior.
Each must fail before a derived object or an enable transition is committed.
The non-provider suite protects the 20-IPC contract, resolver, Work/Health,
durable-memory, feedback, restart, root-lifecycle and receipt gates.

The actual-Tauri run uses only the synthetic fixture and this task's direct
bundle PID.  Each of 1280x1024, 700x760, and 560x640 must bind PID -> exact
title AXWindow -> native AXWebArea, retain the post-settle receipt for the same
PID, and render the restored Cloud/Local provider labels without credentials or
personal text.  The run fails closed if any of those links is absent.
