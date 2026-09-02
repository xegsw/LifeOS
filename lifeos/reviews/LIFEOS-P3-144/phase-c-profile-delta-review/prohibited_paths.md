# Prohibited-path and capability declaration

The following are prohibited throughout this review, including for `exists`, `stat`, `lstat`, `access`, `read`, `write`, `create`, `hash`, `inventory`, `copy`, `cleanup`, process launch, compiler/runtime configuration, or indirect diagnostic probing:

- `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`
- every descendant of that root, including `capture.sqlite`

The review also prohibits real network access, real DeepSeek or any other real Provider call, real credentials, and real text.  No Pilot-7-profile App/runtime may start.  The only permitted Pilot-7 profile operation is offline compile-only validation whose inputs and outputs remain inside the review-owned temporary root and which does not address the prohibited root or database.

Candidate, Closure-1/2/3, existing engineering Evidence, and all preceding independent-review history are immutable read-only inputs after the precontact seal.  No cleanup may target any of them.
