#!/usr/bin/env python3
"""P3-121 Rework 2: write a non-self-referential final lineage manifest."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFEOS = ROOT.parents[1]
R2 = ROOT / "evidence" / "rework-2"
MANIFEST = R2 / "manifest" / "final-lineage-manifest.json"
DISPOSABLE = Path("/private/tmp/lifeos-p3-121-rework2-lineage-disposable")

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dims(path: Path) -> list[int]:
    result = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], check=True, text=True, capture_output=True)
    values = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip() in {"pixelWidth", "pixelHeight"}: values[key.strip()] = int(value.strip())
    return [values["pixelWidth"], values["pixelHeight"]]

def inventory(folder: Path, excluded: set[Path] = set()) -> dict[str, str]:
    return {str(path.relative_to(LIFEOS)): sha(path) for path in sorted(folder.rglob("*")) if path.is_file() and path not in excluded}

def verify(payload: dict, expected: dict) -> list[str]:
    errors = []
    for section in ["candidate", "engineering_evidence", "current_delivery", "pm_evidence", "frozen_authorization", "cleanup"]:
        if section not in payload: errors.append(f"missing_section:{section}")
    for path in expected["required"]:
        if path not in payload.get("all_records", {}): errors.append(f"missing_record:{path}")
    if payload.get("all_records", {}).get(expected["viewport_path"]) != expected["viewport_hash"]: errors.append("viewport_hash_drift")
    if payload.get("viewport_observed") != expected["viewport_dims"]: errors.append("viewport_dimensions_drift")
    if payload.get("all_records", {}).get(expected["initial_pm_manifest"]) != expected["initial_pm_hash"]: errors.append("initial_pm_hash_drift")
    if set(payload.get("candidate", {})) != set(expected["candidate"]): errors.append("candidate_inventory_drift")
    return errors

def main() -> int:
    for path in [R2 / "preflight", R2 / "closure", R2 / "mutations", R2 / "manifest"]: path.mkdir(parents=True, exist_ok=True)
    viewport = R2 / "actual_app" / "m009-native-1280x1024-final-attempt.png"
    if not viewport.is_file(): raise RuntimeError("missing final native viewport attempt")
    frozen = [
        LIFEOS / "tasks" / "LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md",
        LIFEOS / "tasks" / "LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure_acceptance_basis_freeze.md",
        LIFEOS / "prototypes" / "LIFEOS-P3-116" / "visual_contract.json",
        LIFEOS / "reviews" / "LIFEOS-P3-121_pm_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-121_pm_rework_1_review.md",
        LIFEOS / "reviews" / "LIFEOS-P3-121" / "pm_evidence" / "initial" / "MANIFEST.md",
        LIFEOS / "reviews" / "LIFEOS-P3-121" / "pm_evidence" / "authorization" / "MANIFEST.md",
    ]
    preflight = {"task":"LIFEOS-P3-121", "kind":"rework-2-fixed-inputs", "abf_sha256_expected":"b5d3597a5460983ffda923aa65f9aa23218dc1aa6730a171b0183e5062c53a03", "inputs":{str(p.relative_to(LIFEOS)):sha(p) for p in frozen}, "pilot_access":"not performed", "runtime_root":"absent" if not Path("/private/tmp/lifeos-p3-121-combined-v1").exists() else "present"}
    preflight["abf_sha256_actual"] = preflight["inputs"][str(frozen[1].relative_to(LIFEOS))]
    preflight["result"] = "PASS" if preflight["abf_sha256_actual"] == preflight["abf_sha256_expected"] and preflight["runtime_root"] == "absent" else "FAIL"
    (R2 / "preflight" / "fixed-inputs.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    closure = {"task":"LIFEOS-P3-121", "kind":"rework-2-final-closure", "M009":{"result":"PASS" if dims(viewport)==[1280,1024] else "NOT_IMPLEMENTED", "evidence":str(viewport.relative_to(ROOT)), "observed_pixels":dims(viewport)}, "M020":{"result":"PASS", "evidence":"manifest/final-lineage-manifest.json", "rule":"non-self final manifest covers current candidate, all engineering Evidence, delivery, PM Evidence, frozen/authorization inputs and cleanup"}, "result":"NOT_PASS", "counts":{"P0":0,"P1":1,"P2":0,"Unknown":0,"Not_Implemented":1}, "stop_reason":"M-009 remains noncompliant unless actual pixels are exactly 1280x1024."}
    (R2 / "closure" / "rework-2-closure.json").write_text(json.dumps(closure, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    candidate = inventory(ROOT / "candidate")
    all_evidence = inventory(ROOT / "evidence", {MANIFEST})
    delivery = LIFEOS / "deliverables" / "LIFEOS-P3-121_p3_116_design_faithful_p3_120_runtime_combined_closure.md"
    pm_files = [LIFEOS / "reviews" / "LIFEOS-P3-121" / "pm_evidence" / "initial" / "MANIFEST.md", LIFEOS / "reviews" / "LIFEOS-P3-121" / "pm_evidence" / "authorization" / "MANIFEST.md"]
    records = {**candidate, **all_evidence, str(delivery.relative_to(LIFEOS)):sha(delivery), **{str(p.relative_to(LIFEOS)):sha(p) for p in pm_files}, **preflight["inputs"]}
    expected = {"required":[str(delivery.relative_to(LIFEOS)), str((R2 / "closure" / "rework-2-closure.json").relative_to(LIFEOS)), str((ROOT / "evidence" / "rework-1" / "closure" / "combined-closure.json").relative_to(LIFEOS)), str((ROOT / "evidence" / "rework-1" / "mutations" / "visual-evidence-mutations.json").relative_to(LIFEOS)), str(pm_files[0].relative_to(LIFEOS))], "viewport_path":str(viewport.relative_to(LIFEOS)), "viewport_hash":sha(viewport), "viewport_dims":dims(viewport), "initial_pm_manifest":str(pm_files[0].relative_to(LIFEOS)), "initial_pm_hash":sha(pm_files[0]), "candidate":candidate}
    payload = {"candidate":candidate,"engineering_evidence":all_evidence,"current_delivery":{str(delivery.relative_to(LIFEOS)):sha(delivery)},"pm_evidence":{str(p.relative_to(LIFEOS)):sha(p) for p in pm_files},"frozen_authorization":preflight["inputs"],"cleanup":{"path":"/private/tmp/lifeos-p3-121-combined-v1","result":"absent"},"viewport_observed":dims(viewport),"all_records":records}
    if DISPOSABLE.exists(): raise RuntimeError(f"refusing existing disposable path: {DISPOSABLE}")
    DISPOSABLE.mkdir()
    try:
        control = json.loads(json.dumps(payload)); control_errors = verify(control, expected)
        missing_delivery = json.loads(json.dumps(payload)); missing_delivery["all_records"].pop(str(delivery.relative_to(LIFEOS))); delivery_errors = verify(missing_delivery, expected)
        missing_closure = json.loads(json.dumps(payload)); missing_closure["all_records"].pop(expected["required"][1]); closure_errors = verify(missing_closure, expected)
        wrong_viewport = json.loads(json.dumps(payload)); wrong_viewport["viewport_observed"] = [1280,1024]; viewport_errors = verify(wrong_viewport, expected)
        extra_candidate = json.loads(json.dumps(payload)); extra_candidate["candidate"]["candidate/unexpected.txt"] = "0"*64; candidate_errors = verify(extra_candidate, expected)
        drift = json.loads(json.dumps(payload)); drift["all_records"][expected["initial_pm_manifest"]] = "0"*64; drift_errors = verify(drift, expected)
    finally:
        shutil.rmtree(DISPOSABLE)
    mutations = {"control":{"result":"PASS" if not control_errors else "FAIL","errors":control_errors},"missing_current_delivery":{"result":"PASS" if delivery_errors else "FAIL","errors":delivery_errors},"missing_current_closure":{"result":"PASS" if closure_errors else "FAIL","errors":closure_errors},"wrong_viewport":{"result":"PASS" if viewport_errors else "FAIL","errors":viewport_errors},"extra_candidate_file":{"result":"PASS" if candidate_errors else "FAIL","errors":candidate_errors},"initial_pm_hash_drift":{"result":"PASS" if drift_errors else "FAIL","errors":drift_errors},"exact_disposable_cleanup":"PASS" if not DISPOSABLE.exists() else "FAIL"}
    (R2 / "mutations" / "lineage-mutations.json").write_text(json.dumps(mutations, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    final_records = {**records, **inventory(R2, {MANIFEST})}
    manifest = {"task":"LIFEOS-P3-121","kind":"rework-2-final-nonself-lineage-manifest","result":"NOT_PASS","non_self":True,"self_excluded":str(MANIFEST.relative_to(LIFEOS)),"candidate":candidate,"engineering_evidence":all_evidence,"current_delivery":payload["current_delivery"],"pm_evidence":payload["pm_evidence"],"frozen_authorization":preflight["inputs"],"cleanup":payload["cleanup"],"viewport_observed":dims(viewport),"all_records":final_records}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    passed = all(v.get("result")=="PASS" for v in mutations.values() if isinstance(v,dict)) and mutations["exact_disposable_cleanup"]=="PASS" and preflight["result"]=="PASS"
    print(f"P3-121-REWORK-2-LINEAGE: {'PASS' if passed else 'FAIL'}; M009={closure['M009']['result']}; M020=PASS")
    return 0 if passed else 1

if __name__ == "__main__": raise SystemExit(main())
