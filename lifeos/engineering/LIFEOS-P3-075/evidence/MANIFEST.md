# LIFEOS-P3-075 Evidence Manifest

- Scope: non-sensitive test text; task-local SQLite; no real paths or external capability.
- Re-run: `python3 lifeos/engineering/LIFEOS-P3-075/scripts/run_self_check.py && python3 lifeos/engineering/LIFEOS-P3-075/scripts/make_manifest.py`

## SHA-256
- `README.md`: `4dbcae60cd9703b10835b83d8546971fcd1703cc0a6d42a30a09fdd527ca5c57`
- `src/local_runtime.py`: `e12db7191753bde937f328ea59704021ba339fc291de94e4c3a574b136d758d6`
- `scripts/runtime_cli.py`: `5d344c7108b44e77a4103e0ed6d936d18a477c12c0e15b19dabcd25123eee0f7`
- `scripts/run_self_check.py`: `296fc36fbb7cb2dd75e6e3cbd39ac92094c9840a5c46dc01450472af3b0cdf9a`
- `scripts/make_manifest.py`: `0bed5f3fb02bb0ce629ae0b47b12bf09996fa2d8044707d07acf72814d229752`
- `tests/test_runtime.py`: `8725029f87b1badbef5da58bb327ae23e610839e886c8ba048dde0bca6f42182`
- `evidence/self_check_results.json`: `e5a1029979c28fb4c72253dc1b01d1c7be1e9f25d74aeb78f93dfdb1edebc2b2`
- `evidence/self_check.log`: `b43a834e1d34d94b2fe1794b1c5ff78e2c9d947fa9b55d64911afe74b9ab60d7`

## Self-check result

- Clean temporary-copy end-to-end self-check: 17 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0.
- Historical read-only input hashes remained unchanged.
- This is controlled local-runtime Evidence only; it does not close R-0019/R-0040 or enable personal data, production durability, Alpha, or Stage 4.
