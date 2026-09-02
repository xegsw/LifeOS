use std::env;

const TASK: &str = "LIFEOS-P3-144";
const PARENT: &str = "/private/tmp";
const ENGINEERING_BASENAME: &str = "lifeos-p3-144-engineering-v1";
const REVIEW_BASENAME: &str = "lifeos-p3-144-independent-review-v1";
const REVIEW_RUN_ID: &str = "v1";

fn emit(name: &str, value: &str) {
    println!("cargo:rustc-env={name}={value}");
}

fn main() {
    for name in ["LIFEOS_P3_144_ROOT_PROFILE", "LIFEOS_P3_144_REVIEW_RUN_ID"] {
        println!("cargo:rerun-if-env-changed={name}");
    }

    let profile = env::var("LIFEOS_P3_144_ROOT_PROFILE").unwrap_or_else(|_| "engineering".into());
    let review_run_id = env::var("LIFEOS_P3_144_REVIEW_RUN_ID").ok();

    let (basename, marker_schema, owner, run_id, marker_run_id) = match profile.as_str() {
        "engineering" => {
            if review_run_id.is_some() {
                panic!("review run id is only valid for the independent-review root profile");
            }
            (
                ENGINEERING_BASENAME.to_owned(),
                "lifeos.p3-144.engineering-root.v1".to_owned(),
                ENGINEERING_BASENAME.to_owned(),
                "engineering".to_owned(),
                String::new(),
            )
        }
        "independent-review" => {
            if review_run_id.is_some() {
                panic!(
                    "independent-review uses the frozen v1 root and rejects dynamic review run ids"
                );
            }
            (
                REVIEW_BASENAME.to_owned(),
                "lifeos.p3-144.independent-review-root.v1".to_owned(),
                "lifeos-p3-144-independent-review".to_owned(),
                REVIEW_RUN_ID.to_owned(),
                REVIEW_RUN_ID.to_owned(),
            )
        }
        _ => panic!("root profile must be engineering or independent-review"),
    };

    if basename.is_empty()
        || basename.contains('/')
        || basename == "."
        || basename == ".."
        || !format!("{PARENT}/{basename}").starts_with("/private/tmp/")
    {
        panic!("compiled root authority is not a canonical direct child of /private/tmp");
    }

    emit("LIFEOS_P3_144_COMPILED_ROOT_PROFILE", &profile);
    emit("LIFEOS_P3_144_COMPILED_ROOT_PARENT", PARENT);
    emit("LIFEOS_P3_144_COMPILED_ROOT_BASENAME", &basename);
    emit(
        "LIFEOS_P3_144_COMPILED_ROOT",
        &format!("{PARENT}/{basename}"),
    );
    emit("LIFEOS_P3_144_COMPILED_MARKER_SCHEMA", &marker_schema);
    emit("LIFEOS_P3_144_COMPILED_MARKER_TASK", TASK);
    emit("LIFEOS_P3_144_COMPILED_MARKER_OWNER", &owner);
    emit("LIFEOS_P3_144_COMPILED_RUN_ID", &run_id);
    emit("LIFEOS_P3_144_COMPILED_MARKER_RUN_ID", &marker_run_id);

    tauri_build::build();
}
