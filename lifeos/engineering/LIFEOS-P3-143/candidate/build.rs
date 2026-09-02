use std::env;

const TASK: &str = "LIFEOS-P3-143";
const PARENT: &str = "/private/tmp";
const ENGINEERING_BASENAME: &str = "lifeos-p3-143-real-ai-secure-activation-v1";
const REVIEW_PREFIX: &str = "lifeos-p3-143-independent-review-";

fn valid_review_run_id(value: &str) -> bool {
    (8..=48).contains(&value.len())
        && !value.starts_with('-')
        && !value.ends_with('-')
        && value
            .bytes()
            .all(|byte| byte.is_ascii_lowercase() || byte.is_ascii_digit() || byte == b'-')
}

fn emit(name: &str, value: &str) {
    println!("cargo:rustc-env={name}={value}");
}

fn main() {
    for name in ["LIFEOS_P3_143_ROOT_PROFILE", "LIFEOS_P3_143_REVIEW_RUN_ID"] {
        println!("cargo:rerun-if-env-changed={name}");
    }

    let profile = env::var("LIFEOS_P3_143_ROOT_PROFILE").unwrap_or_else(|_| "engineering".into());
    let review_run_id = env::var("LIFEOS_P3_143_REVIEW_RUN_ID").ok();

    let (basename, marker_schema, owner, run_id, marker_run_id) = match profile.as_str() {
        "engineering" => {
            if review_run_id.is_some() {
                panic!("review run id is only valid for the independent-review root profile");
            }
            (
                ENGINEERING_BASENAME.to_owned(),
                "lifeos.p3-143.real-ai-secure-activation-root.v1".to_owned(),
                ENGINEERING_BASENAME.to_owned(),
                "engineering".to_owned(),
                String::new(),
            )
        }
        "independent-review" => {
            let run_id = review_run_id
                .filter(|value| valid_review_run_id(value))
                .unwrap_or_else(|| {
                    panic!(
                        "independent-review requires a safe 8-48 character lowercase/digit/hyphen run id"
                    )
                });
            (
                format!("{REVIEW_PREFIX}{run_id}"),
                "lifeos.p3-143.independent-review-root.v1".to_owned(),
                "lifeos-p3-143-independent-review".to_owned(),
                run_id.clone(),
                run_id,
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

    emit("LIFEOS_P3_143_COMPILED_ROOT_PROFILE", &profile);
    emit("LIFEOS_P3_143_COMPILED_ROOT_PARENT", PARENT);
    emit("LIFEOS_P3_143_COMPILED_ROOT_BASENAME", &basename);
    emit(
        "LIFEOS_P3_143_COMPILED_ROOT",
        &format!("{PARENT}/{basename}"),
    );
    emit("LIFEOS_P3_143_COMPILED_MARKER_SCHEMA", &marker_schema);
    emit("LIFEOS_P3_143_COMPILED_MARKER_TASK", TASK);
    emit("LIFEOS_P3_143_COMPILED_MARKER_OWNER", &owner);
    emit("LIFEOS_P3_143_COMPILED_RUN_ID", &run_id);
    emit("LIFEOS_P3_143_COMPILED_MARKER_RUN_ID", &marker_run_id);

    tauri_build::build();
}
