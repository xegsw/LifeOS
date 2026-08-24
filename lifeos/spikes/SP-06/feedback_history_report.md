# Feedback history report

Confirm, edited accept, reject, correct, complete, defer, and retract are append-only events. A stale business transition is also retained as an unapplied event with a controlled reason code. Retraction creates a new event and sets the referenced event's current effectiveness to false; it does not erase that event. Tests T12 and T16-T20 cover the required histories. Production projection rebuild, long histories, and migration are not measured.
