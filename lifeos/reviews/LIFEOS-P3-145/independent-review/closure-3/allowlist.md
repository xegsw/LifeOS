# Closure-3 allowlist

After the Closure-3 precontact seal only: immutable Git objects for fixed commit `579914d06923db65db8c3b421b2da663a1950354`; the candidate's detached read-only snapshot at `/private/tmp/lifeos-p3-145-independent-review-closure-3/candidate`; exactly the P3-144 Task/ABF/candidate/Review/Evidence/Manifest inputs named by the Frozen P3-145 task; the Closure-3 review directory; the closure-3 temporary build root; a new review-owned synthetic runtime root at `/private/tmp/lifeos-p3-145-independent-review-v1`; fixed fixtures named in `test_design.md`; and non-content process/socket/SQLite metadata.

The existing opaque `com.lifeos.p3-145.aead-key.v1` Keychain item observed in Closure-2 is explicitly excluded: do not read, stat, delete, list, or otherwise probe it. macOS Keychain and every other real Credential Store are prohibited.

No Pilot-7 root, real DB/text, real credential, real Provider endpoint, network, candidate modification, PM ledger, frozen-input modification, or historical-artifact modification is allowed.
