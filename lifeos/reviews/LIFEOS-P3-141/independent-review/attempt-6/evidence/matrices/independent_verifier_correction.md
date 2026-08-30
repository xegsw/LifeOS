# attempt-6 verifier correction

The initial attempt-6 verifier output (`candidate_lineage_initial.json`) is preserved as an invalid reviewer-tool result.  It incorrectly compared the P3-141 candidate tree to the distinct P3-140 baseline tree merely because both have 79 files.  That comparison is not an ABF requirement and the mismatch is not a candidate defect.

The corrected verifier uses the framing algorithm from the fixed P3-141 candidate verifier, validates P3-140 against its own frozen 79-file tree hash, binds the P3-141 candidate to the supplied commit separately, and checks the engineering Final Manifest independently.  No prohibited asset was accessed and no candidate file was changed.
