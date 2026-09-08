"""Audited P3-144 offline CI partition; OS credential tests remain manual gates."""
import os
import subprocess

OFFLINE = {
    "runtime::tests::" + name for name in """
registry_has_eight_cloud_and_four_local_entries
capabilities_come_from_adapter_metadata_not_provider_name
strict_dto_rejects_unknown_field_before_validation
cloud_and_local_fields_fail_closed
illegal_provider_capability_and_priority_fail_closed
router_requires_authorization_and_defaults_to_no_cloud_supplement
persistence_payload_contains_only_non_secret_reference
compiled_root_authority_is_closed_and_non_runtime_configurable
pilot_7_authority_is_exact_without_accessing_the_pilot_root
absent_review_root_creates_the_exact_marker_before_runtime_or_database
existing_review_root_missing_or_mutated_marker_fails_before_runtime_or_database
review_root_authority_rejects_root_symlink_before_writes
review_root_authority_rejects_wrong_profile_root_run_id_and_traversal_before_writes
database_symlink_is_rejected_before_open_and_sentinel_is_unchanged
database_must_be_regular_and_is_forced_to_owner_only_permissions
deepseek_requires_the_exact_https_authority
exactly_twenty_ipc_are_registered
provider_save_resets_test_and_enablement
test_models_clears_prior_selection_and_keeps_provider_disabled
understanding_feedback_is_single_use_except_explicit_correction
p3_144_phase_a_context_limits_disclosure_and_confirmation_are_fail_closed
""".split()
} | {
    "deepseek::tests::curl_timeout_is_not_misreported_as_network_unavailable",
    "deepseek::tests::http_status_classes_remain_distinct_when_curl_succeeds",
}
MANUAL = {
    "runtime::tests::" + name for name in """
credential_keychain_material_and_aead_are_separate_and_fail_closed
sqlite_ciphertext_requires_its_exact_keychain_material_and_leaks_no_canary
credential_replacement_invalidates_the_previous_ciphertext_and_reference
""".split()
}


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("CI-only runner: do not touch historical roots locally")
    if os.environ.get("LIFEOS_P3_144_ROOT_PROFILE") != "engineering":
        raise SystemExit("synthetic engineering profile required")
    base = ["cargo", "test", "--locked", "--offline"]
    listed = subprocess.run(base + ["--", "--list"], check=True,
                            text=True, capture_output=True)
    actual = {line[:-6] for line in listed.stdout.splitlines() if line.endswith(": test")}
    if actual != OFFLINE | MANUAL:
        raise SystemExit(f"Unreviewed test inventory: added={actual - OFFLINE - MANUAL}, missing={(OFFLINE | MANUAL) - actual}")
    for name in sorted(MANUAL):
        print(f"MANUAL GATE / NOT RUN (OS Keychain access): {name}", flush=True)
    sandbox = ["sandbox-exec", "-p", "(version 1)(allow default)(deny network*)"]
    for name in sorted(OFFLINE):
        result = subprocess.run(sandbox + base + [name, "--", "--exact", "--test-threads=1"],
                                check=True, text=True, capture_output=True)
        print(result.stdout, flush=True)
        if "1 passed; 0 failed" not in result.stdout:
            raise SystemExit(f"Expected one executed passing test: {name}")
    print(f"Offline PASS: {len(OFFLINE)}; manual credential gates NOT RUN: {len(MANUAL)}")


if __name__ == "__main__":
    main()
