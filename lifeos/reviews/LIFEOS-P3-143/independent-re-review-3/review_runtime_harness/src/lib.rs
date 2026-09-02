#[path = "../../../../../engineering/LIFEOS-P3-143/candidate/src/deepseek.rs"]
mod deepseek;
#[path = "../../../../../engineering/LIFEOS-P3-143/candidate/src/secure_credentials.rs"]
mod secure_credentials;

mod runtime {
    include!("../../../../../engineering/LIFEOS-P3-143/candidate/src/runtime.rs");
    #[cfg(test)]
    include!("review_probes.rs");
}
