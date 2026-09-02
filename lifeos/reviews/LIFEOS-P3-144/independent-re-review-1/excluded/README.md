# Excluded capture retry

`narrow_geometry_wrong_target.png` was generated at 2026-09-02 19:31 CST while
testing a geometry-based fallback after the window-number screenshot was too
small. Visual inspection showed it captured the Codex window rather than the
target LifeOS window. It is deliberately outside `evidence/`, is not listed in
the review Manifest, and supplies no candidate conclusion. The retained narrow
evidence is the direct-launch receipt plus the PID-bound AX/CG JSON and its
window-number target-only screenshot; its limited raster resolution is noted
as a bounded visual-quality limitation in the review report.

`desktop_sky_thumbnail.jpeg` is also outside the Evidence set. It was an
in-app Computer Use thumbnail used only to establish that a visual fallback
was insufficient. The final desktop Evidence uses the native PID-bound
AX/CG target-window PNG instead.
