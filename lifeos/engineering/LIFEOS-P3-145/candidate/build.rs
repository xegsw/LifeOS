use std::env;

const TASK: &str = "LIFEOS-P3-145";
const SYNTHETIC_PARENT: &str = "/private/tmp";
const ENGINEERING_BASENAME: &str = "lifeos-p3-145-engineering-v1";
const REVIEW_BASENAME: &str = "lifeos-p3-145-independent-review-v1";
const REVIEW_RUN_ID: &str = "v1";
const PILOT_PARENT: &str = "/Users/xxe/Documents";
const PILOT_BASENAME: &str = "LifeOS-Self-Use-Pilot-7";
const PILOT_RUN_ID: &str = "pilot-7";

fn emit(name: &str, value: &str) {
    println!("cargo:rustc-env={name}={value}");
}

fn main() {
    for name in ["LIFEOS_P3_145_ROOT_PROFILE", "LIFEOS_P3_145_REVIEW_RUN_ID"] {
        println!("cargo:rerun-if-env-changed={name}");
    }

    let profile = env::var("LIFEOS_P3_145_ROOT_PROFILE").unwrap_or_else(|_| "engineering".into());
    let review_run_id = env::var("LIFEOS_P3_145_REVIEW_RUN_ID").ok();

    let (parent, basename, marker_schema, owner, run_id, marker_run_id, run_mode) =
        match profile.as_str() {
            "engineering" => {
                if review_run_id.is_some() {
                    panic!("review run id is only valid for the independent-review root profile");
                }
                (
                    SYNTHETIC_PARENT.to_owned(),
                    ENGINEERING_BASENAME.to_owned(),
                    "lifeos.p3-145.engineering-root.v1".to_owned(),
                    ENGINEERING_BASENAME.to_owned(),
                    "engineering".to_owned(),
                    String::new(),
                    "synthetic".to_owned(),
                )
            }
            "independent-review" => {
                if review_run_id.is_some() {
                    panic!(
                    "independent-review uses the frozen v1 root and rejects dynamic review run ids"
                );
                }
                (
                    SYNTHETIC_PARENT.to_owned(),
                    REVIEW_BASENAME.to_owned(),
                    "lifeos.p3-145.independent-review-root.v1".to_owned(),
                    "lifeos-p3-145-independent-review".to_owned(),
                    REVIEW_RUN_ID.to_owned(),
                    REVIEW_RUN_ID.to_owned(),
                    "synthetic".to_owned(),
                )
            }
            "pilot-7" => {
                if review_run_id.is_some() {
                    panic!("review run id is invalid for the pilot-7 root profile");
                }
                (
                    PILOT_PARENT.to_owned(),
                    PILOT_BASENAME.to_owned(),
                    "lifeos.p3-145.pilot-7-root.v1".to_owned(),
                    "lifeos-p3-145-pilot-7".to_owned(),
                    PILOT_RUN_ID.to_owned(),
                    PILOT_RUN_ID.to_owned(),
                    "real_gate".to_owned(),
                )
            }
            _ => panic!("root profile must be engineering, independent-review, or pilot-7"),
        };

    if basename.is_empty()
        || basename.contains('/')
        || basename == "."
        || basename == ".."
        || !parent.starts_with('/')
    {
        panic!("compiled root authority is not a canonical absolute direct child");
    }

    emit("LIFEOS_P3_145_COMPILED_ROOT_PROFILE", &profile);
    emit("LIFEOS_P3_145_COMPILED_ROOT_PARENT", &parent);
    emit("LIFEOS_P3_145_COMPILED_ROOT_BASENAME", &basename);
    emit(
        "LIFEOS_P3_145_COMPILED_ROOT",
        &format!("{parent}/{basename}"),
    );
    emit("LIFEOS_P3_145_COMPILED_MARKER_SCHEMA", &marker_schema);
    emit("LIFEOS_P3_145_COMPILED_MARKER_TASK", TASK);
    emit("LIFEOS_P3_145_COMPILED_MARKER_OWNER", &owner);
    emit("LIFEOS_P3_145_COMPILED_RUN_ID", &run_id);
    emit("LIFEOS_P3_145_COMPILED_MARKER_RUN_ID", &marker_run_id);
    emit("LIFEOS_P3_145_COMPILED_RUN_MODE", &run_mode);

    tauri_build::build();
}
