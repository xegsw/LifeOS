# Rerun

From the project root, with the same explicit retained-read authorization:

```bash
python3 -B lifeos/reviews/LIFEOS-P3-103/evidence/runner.py
```

The runner writes only task-owned P3-103 Evidence, uses fresh fixed non-sensitive `/private/tmp` fixtures, and removes them precisely. It must not be run after authorization or retained-state changes without PM review.
