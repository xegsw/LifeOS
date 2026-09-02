use std::env;

const RUN_ID: &str = "finalgui-20260902";
const ROOT: &str = "/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902";

fn emit(name: &str, value: &str) {
    println!("cargo:rustc-env={name}={value}");
}

fn main() {
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_143_ROOT_PROFILE");
    println!("cargo:rerun-if-env-changed=LIFEOS_P3_143_REVIEW_RUN_ID");
    let profile = env::var("LIFEOS_P3_143_ROOT_PROFILE")
        .expect("independent review requires explicit root profile");
    let run_id = env::var("LIFEOS_P3_143_REVIEW_RUN_ID")
        .expect("independent review requires explicit run id");
    assert_eq!(profile, "independent-review", "review profile must remain sealed");
    assert_eq!(run_id, RUN_ID, "review run id must remain sealed");
    emit("LIFEOS_P3_143_COMPILED_ROOT_PROFILE", "independent-review");
    emit("LIFEOS_P3_143_COMPILED_ROOT_PARENT", "/private/tmp");
    emit("LIFEOS_P3_143_COMPILED_ROOT_BASENAME", "lifeos-p3-143-independent-review-finalgui-20260902");
    emit("LIFEOS_P3_143_COMPILED_ROOT", ROOT);
    emit("LIFEOS_P3_143_COMPILED_MARKER_SCHEMA", "lifeos.p3-143.independent-review-root.v1");
    emit("LIFEOS_P3_143_COMPILED_MARKER_TASK", "LIFEOS-P3-143");
    emit("LIFEOS_P3_143_COMPILED_MARKER_OWNER", "lifeos-p3-143-independent-review");
    emit("LIFEOS_P3_143_COMPILED_RUN_ID", RUN_ID);
    emit("LIFEOS_P3_143_COMPILED_MARKER_RUN_ID", RUN_ID);
}
