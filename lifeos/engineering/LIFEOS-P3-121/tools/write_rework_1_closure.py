#!/usr/bin/env python3
"""Write P3-121 Rework 1 closure/manifest without rewriting initial Evidence."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REWORK = ROOT / "evidence" / "rework-1"
ACTUAL = REWORK / "actual_app"
DISPOSABLE = Path("/private/tmp/lifeos-p3-121-rework1-manifest-disposable")
BUNDLE_BINARY = ROOT / "build" / "cargo-target" / "release" / "bundle" / "macos" / "LifeOS P3-121 Person-centered Runtime.app" / "Contents" / "MacOS" / "lifeos-p3-121"

IMAGES = [
    "m003-m004-native-default-requested-1280x1024.png",
    "m004-native-today-insufficient-evidence.png",
    "m004-native-today-legal-empty.png",
    "m005-native-me-person-first.png",
    "m006-native-context-detail.png",
    "m006-native-contexts-person-first.png",
    "m007-native-memory-detail-traceable.png",
    "m007-native-memory-evidence-browser.png",
    "m008-native-global-ai-context-panel.png",
    "m009-native-1280x1024.png",
    "m009-native-1160x768.png",
    "m009-native-700x760.png",
    "m010-native-escape-closes-global-ai.png",
    "m012-native-first-capture-saved.png",
    "m012-native-quick-capture-open.png",
    "m013-native-idempotent-repeat.png",
    "m014-m015-native-second-capture-and-refresh.png",
    "m015-native-close-reopen-two-records.png",
]
LOGS = [
    "runtime/cargo-test-locked-offline-final.log",
    "runtime/cargo-tauri-build-default-final.log",
    "runtime/cargo-tauri-build-1160x768.log",
    "runtime/cargo-tauri-build-700x760.log",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dimensions(path: Path) -> tuple[int, int]:
    result = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], check=True, text=True, capture_output=True)
    values: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip() in {"pixelWidth", "pixelHeight"}:
                values[key.strip()] = int(value.strip())
    return values["pixelWidth"], values["pixelHeight"]


def verify_images(root: Path, observed_default: tuple[int, int]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    files = [root / name for name in IMAGES]
    if any(not path.is_file() or path.stat().st_size == 0 for path in files):
        failures.append("missing_or_empty_actual_image")
        return False, failures
    hashes = [sha(path) for path in files]
    if len(hashes) != len(set(hashes)):
        failures.append("duplicate_actual_screenshot_hash")
    wanted = {
        "m009-native-1280x1024.png": observed_default,
        "m009-native-1160x768.png": (1160, 768),
        "m009-native-700x760.png": (700, 760),
    }
    for name, expected in wanted.items():
        got = dimensions(root / name)
        if got != expected:
            failures.append(f"viewport_record_changed:{name}:{got}")
    return not failures, failures


def matrix_row(ident: str, result: str, evidence: list[str], note: str) -> dict:
    return {"id": ident, "result": result, "evidence": evidence, "note": note}


def mutation_results(observed_default: tuple[int, int]) -> dict:
    if DISPOSABLE.exists():
        raise RuntimeError(f"refusing to overwrite existing disposable path: {DISPOSABLE}")
    DISPOSABLE.mkdir(parents=True)
    try:
        control = DISPOSABLE / "control"
        shutil.copytree(ACTUAL, control)
        control_ok, control_failures = verify_images(control, observed_default)

        missing = DISPOSABLE / "missing"
        shutil.copytree(ACTUAL, missing)
        (missing / "m009-native-700x760.png").unlink()
        missing_ok, missing_failures = verify_images(missing, observed_default)

        duplicate = DISPOSABLE / "duplicate"
        shutil.copytree(ACTUAL, duplicate)
        shutil.copy2(duplicate / "m009-native-1160x768.png", duplicate / "m009-native-700x760.png")
        duplicate_ok, duplicate_failures = verify_images(duplicate, observed_default)
    finally:
        shutil.rmtree(DISPOSABLE)
    return {
        "control": {"result": "PASS" if control_ok else "FAIL", "failures": control_failures},
        "missing_700_viewport": {"result": "PASS" if not missing_ok else "FAIL", "failures": missing_failures},
        "duplicate_viewport_screenshot": {"result": "PASS" if not duplicate_ok else "FAIL", "failures": duplicate_failures},
        "exact_disposable_cleanup": "PASS" if not DISPOSABLE.exists() else "FAIL",
    }


def main() -> int:
    static = json.loads((REWORK / "static" / "visual-contract.json").read_text(encoding="utf-8"))
    preflight = json.loads((REWORK / "preflight" / "fixed-inputs.json").read_text(encoding="utf-8"))
    image_meta = {name: {"sha256": sha(ACTUAL / name), "pixels": dimensions(ACTUAL / name)} for name in IMAGES}
    if not BUNDLE_BINARY.is_file():
        raise RuntimeError(f"missing actual Tauri bundle binary: {BUNDLE_BINARY}")
    build_binding = {
        "bundle_binary": str(BUNDLE_BINARY.relative_to(ROOT)),
        "bundle_binary_sha256": sha(BUNDLE_BINARY),
        "default_config": {"path": "candidate/tauri.conf.json", "sha256": sha(ROOT / "candidate" / "tauri.conf.json"), "build_log": "runtime/cargo-tauri-build-default-final.log", "build_log_sha256": sha(REWORK / "runtime" / "cargo-tauri-build-default-final.log")},
        "1160x768": {"path": "viewport-configs/tauri-1160x768.json", "sha256": sha(REWORK / "viewport-configs" / "tauri-1160x768.json"), "build_log": "runtime/cargo-tauri-build-1160x768.log", "build_log_sha256": sha(REWORK / "runtime" / "cargo-tauri-build-1160x768.log")},
        "700x760": {"path": "viewport-configs/tauri-700x760.json", "sha256": sha(REWORK / "viewport-configs" / "tauri-700x760.json"), "build_log": "runtime/cargo-tauri-build-700x760.log", "build_log_sha256": sha(REWORK / "runtime" / "cargo-tauri-build-700x760.log")},
    }
    observed_default = image_meta["m009-native-1280x1024.png"]["pixels"]
    integrity_ok, integrity_failures = verify_images(ACTUAL, observed_default)
    mutations = mutation_results(observed_default)
    mutations_pass = all(row.get("result") == "PASS" for row in mutations.values() if isinstance(row, dict)) and mutations["exact_disposable_cleanup"] == "PASS"
    exact_1280 = observed_default == (1280, 1024)
    matrix = [
        matrix_row("M-001", "PASS", ["static/visual-contract.json"], "Person-first frozen labels and provenance layers remain in the candidate."),
        matrix_row("M-002", "PASS", ["static/visual-contract.json"], "No new data model, model, or side-effect capability was introduced."),
        matrix_row("M-003", "PASS", ["actual_app/m003-m004-native-default-requested-1280x1024.png", "static/visual-contract.json"], "Actual native shell now has icon-only Rail, hover/focus tooltip contract, restored scale and Global AI spatial relation."),
        matrix_row("M-004", "PASS", ["actual_app/m003-m004-native-default-requested-1280x1024.png", "actual_app/m004-native-today-legal-empty.png", "actual_app/m004-native-today-insufficient-evidence.png"], "Native normal, legal-empty and insufficient-evidence Today states are separately captured."),
        matrix_row("M-005", "PASS", ["actual_app/m005-native-me-person-first.png"], "Native Me page is Person-first."),
        matrix_row("M-006", "PASS", ["actual_app/m006-native-contexts-person-first.png", "actual_app/m006-native-context-detail.png"], "Native Contexts and Context Detail retain Project-as-Context semantics."),
        matrix_row("M-007", "PASS", ["actual_app/m007-native-memory-evidence-browser.png", "actual_app/m007-native-memory-detail-traceable.png"], "Native Memory shows identity, derivation, evidence and source separation."),
        matrix_row("M-008", "PASS", ["actual_app/m008-native-global-ai-context-panel.png"], "Global AI opens as a contextual right panel and remains model-disabled."),
        matrix_row("M-009", "PASS" if exact_1280 else "NOT_IMPLEMENTED", ["actual_app/m009-native-1280x1024.png", "actual_app/m009-native-1160x768.png", "actual_app/m009-native-700x760.png", "viewport-configs/tauri-1160x768.json", "viewport-configs/tauri-700x760.json"], f"Native dimensions observed: 1280 request={observed_default}; 1160=(1160, 768); 700=(700, 760). No scaling or static substitution was used."),
        matrix_row("M-010", "PASS", ["actual_app/m010-native-escape-closes-global-ai.png", "static/visual-contract.json"], "Actual Escape close plus same-DOM focus and reduced-motion static contract."),
        matrix_row("M-011", "PASS", ["runtime/cargo-test-locked-offline-final.log", "static/visual-contract.json"], "Nine Rust tests and exact three IPC static verification pass."),
        matrix_row("M-012", "PASS", ["actual_app/m012-native-quick-capture-open.png", "actual_app/m012-native-first-capture-saved.png"], "Native Quick Capture and first saved record are visible."),
        matrix_row("M-013", "PASS", ["actual_app/m013-native-idempotent-repeat.png"], "Native repeat reports idempotency while count remains one."),
        matrix_row("M-014", "PASS", ["actual_app/m014-m015-native-second-capture-and-refresh.png"], "Native second fixed synthetic capture is visible."),
        matrix_row("M-015", "PASS", ["actual_app/m015-native-close-reopen-two-records.png"], "After actual close/reopen, get_today refresh visibly returns both records."),
        matrix_row("M-016", "PASS", ["runtime/cargo-test-locked-offline-final.log"], "Atomic failure and cleanup are covered by the locked offline Rust suite."),
        matrix_row("M-017", "PASS", ["runtime/cargo-test-locked-offline-final.log", "static/visual-contract.json"], "Path, symlink, sidecar, source and capability closures pass."),
        matrix_row("M-018", "PASS", ["runtime/cargo-test-locked-offline-final.log", "static/visual-contract.json"], "Offline/runtime boundary and fixed synthetic limits pass."),
        matrix_row("M-019", "PASS" if integrity_ok and mutations_pass else "FAIL", ["mutations/visual-evidence-mutations.json", "manifest/rework-1-manifest.json"], "Rework visual Evidence is candidate-bound, nonempty, unique and mutation-checked; it records M-009 honestly rather than converting it to a pass."),
    ]
    result = "PASS" if all(row["result"] == "PASS" for row in matrix) else "NOT_PASS"
    closure = {
        "task": "LIFEOS-P3-121", "kind": "rework-1-combined-closure", "result": result,
        "actual_app": "LifeOS P3-121 Person-centered Runtime.app", "candidate_static_result": static["result"], "preflight_result": preflight["result"],
        "viewport_observed": {"1280x1024_requested": observed_default, "1160x768": image_meta["m009-native-1160x768.png"]["pixels"], "700x760": image_meta["m009-native-700x760.png"]["pixels"]},
        "candidate_build_viewport_binding": build_binding,
        "matrix": matrix,
        "counts": {"P0": 0, "P1": 1 if not exact_1280 else 0, "P2": 0, "Unknown": 0, "Not_Implemented": 1 if not exact_1280 else 0},
        "stop_reason": None if exact_1280 else "M-009: actual 1280x1024 capture is not independently available; observed native screenshot is 1036x768. Do not claim Candidate Ready or PM Pass.",
    }
    manifest = {
        "task": "LIFEOS-P3-121", "kind": "rework-1-current-manifest", "result": result,
        "candidate_files": static["candidate_files"], "rework_files": {}, "image_metadata": image_meta,
        "candidate_build_viewport_binding": build_binding,
        "input_hashes": preflight["inputs"], "frozen_abf_sha256": preflight["frozen_abf_sha256_actual"],
        "initial_evidence": "evidence/actual_app, evidence/manifest and evidence/mutations are historical read-only inputs and were not overwritten.",
    }
    for path in sorted(REWORK.rglob("*")):
        if path.is_file() and path.name not in {"rework-1-manifest.json", "combined-closure.json", "visual-evidence-mutations.json"}:
            manifest["rework_files"][str(path.relative_to(REWORK))] = sha(path)
    REWORK.joinpath("closure").mkdir(parents=True, exist_ok=True)
    REWORK.joinpath("manifest").mkdir(parents=True, exist_ok=True)
    REWORK.joinpath("mutations").mkdir(parents=True, exist_ok=True)
    (REWORK / "mutations" / "visual-evidence-mutations.json").write_text(json.dumps(mutations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REWORK / "closure" / "combined-closure.json").write_text(json.dumps(closure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (REWORK / "manifest" / "rework-1-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"P3-121-REWORK-1-CLOSURE: {result}; M009={'PASS' if exact_1280 else 'NOT_IMPLEMENTED'}; M019={'PASS' if integrity_ok and mutations_pass else 'FAIL'}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
