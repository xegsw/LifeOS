// Compile build.rs as a test module so its Revision-2 gate tests exercise the
// same schema, duplicate-key parser and file-boundary helpers as the build gate.
#[path = "../build.rs"]
mod revision_2_gate;
