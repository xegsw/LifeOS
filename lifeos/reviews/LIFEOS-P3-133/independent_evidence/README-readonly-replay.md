# P3-133 independent evidence readonly replay

Run this command from any directory after the Final Manifest exists:

```sh
python3 -B /Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-133/independent_evidence/independent_readonly_replay.py
```

The entrypoint only reads the retained independent evidence. It does not access the candidate, engineering Evidence, a Tauri app, a DB, any Pilot root, or the network; it creates no files. A zero exit means the retained manifest is exact and consistently records the required non-Pass / Closure Cycle outcome. It is not an engineering verifier and does not issue a product, freeze, risk, PM, or Stage conclusion.
