# Procedural deviation — 2026-08-31

- Finding: a Swift helper compile check was mistakenly emitted to the exact
  temporary file `/private/tmp/lifeos-p3-141-native-window-capture-compile-check`,
  outside the one authorized Closure root.
- Scope: this file was a locally compiled helper only; it did not read or write
  Pilot-6, real DB/text, Health values, Provider, credential, network, cloud,
  model, or any old temporary root.
- Containment: the exact regular file was immediately deleted and literal
  absence was confirmed.  No recursive deletion was used.
- Consequence: this is a procedural P0 for this Closure package.  A later
  successful authorized-root run cannot erase it.  The package must remain
  `Blocked`; this record preserves rather than conceals the failed history.
