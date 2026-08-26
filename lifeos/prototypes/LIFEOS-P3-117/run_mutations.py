#!/usr/bin/env python3
"""Run twelve real disposable payload mutations against the P3-117 verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/tmp/lifeos-p3-117-native-capture-v1")
RESULT = TASK_ROOT / "evidence/mutation_results.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    return struct.unpack(">II", data[16:24])


def solid_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    rows = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))

    def chunk(tag: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xffffffff)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)


def doc(root: Path, rel: str) -> tuple[Path, dict]:
    path = root / rel
    return path, json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(root: Path) -> tuple[int, str]:
    completed = subprocess.run([sys.executable, "-B", str(root / "verify_evidence.py"), "--root", str(root), "--allow-temp-present", "--skip-manifest"], capture_output=True, text=True)
    return completed.returncode, (completed.stderr or completed.stdout).strip()


def first_result(root: Path, predicate) -> dict:
    rows = json.loads((root / "evidence/action_results.json").read_text(encoding="utf-8"))["results"]
    return next(row for row in rows if predicate(row))


def replace_clean(root: Path, row: dict, source: Path | None, rgb: tuple[int, int, int] | None) -> None:
    geometry_path, geometry = doc(root, row["geometry_path"])
    target = root / geometry["phases"]["clean"]["crop_path"]
    if source:
        shutil.copy2(source, target)
    else:
        width, height = png_size(target)
        solid_png(target, width, height, rgb or (255, 255, 255))
    geometry["phases"]["clean"]["crop_sha256"] = sha(target)
    write(geometry_path, geometry)
    results_path, results = doc(root, "evidence/action_results.json")
    for item in results["results"]:
        if item["case_id"] == row["case_id"]:
            item["clean_sha256"] = sha(target)
    write(results_path, results)


def mutate(root: Path, name: str) -> None:
    target = first_result(root, lambda _: True)
    if name == "blank":
        replace_clean(root, target, None, (255, 255, 255))
    elif name == "monochrome":
        replace_clean(root, target, None, (17, 34, 51))
    elif name == "duplicate":
        other = first_result(root, lambda row: row["case_id"] != target["case_id"])
        other_geom = json.loads((root / other["geometry_path"]).read_text(encoding="utf-8"))
        replace_clean(root, target, root / other_geom["phases"]["clean"]["crop_path"], None)
        results_path, results = doc(root, "evidence/action_results.json")
        for item in results["results"]:
            if item["case_id"] == target["case_id"]:
                item["expected_anchor"] = other["expected_anchor"]
        write(results_path, results)
    elif name == "wrong_viewport":
        target = first_result(root, lambda row: row["case_id"] == "M011-C01")
        geometry_path, geometry = doc(root, target["geometry_path"])
        geometry["viewport_css"] = "1279x1024"
        write(geometry_path, geometry)
    elif name == "wrong_crop":
        geometry_path, geometry = doc(root, target["geometry_path"])
        geometry["crop"]["width"] = geometry["phases"]["proof"]["raw_size"]["width"] + 1
        write(geometry_path, geometry)
    elif name == "browser_chrome":
        geometry_path, geometry = doc(root, target["geometry_path"])
        geometry["forbidden_content"] = ["browser_chrome"]
        write(geometry_path, geometry)
    elif name == "wrong_semantic":
        results_path, results = doc(root, "evidence/action_results.json")
        results["results"][0]["actual_action"] = "wrong:semantic"
        write(results_path, results)
    elif name == "source_drift":
        fixed_path, fixed = doc(root, "evidence/preflight/fixed_inputs.json")
        first_key = next(iter(fixed["inputs"]))
        fixed["inputs"][first_key]["expected"] = "0" * 64
        write(fixed_path, fixed)
    elif name == "ambient_marker":
        results_path, results = doc(root, "evidence/action_results.json")
        results["results"][0]["actual_observation"] = "ambient-chrome-tab"
        write(results_path, results)
    elif name == "probe_leak":
        geometry_path, geometry = doc(root, target["geometry_path"])
        proof = root / geometry["phases"]["proof"]["crop_path"]
        replace_clean(root, target, proof, None)
    elif name == "missing_raw_link":
        geometry_path, geometry = doc(root, target["geometry_path"])
        del geometry["phases"]["proof"]["raw_path"]
        write(geometry_path, geometry)
    elif name == "missing_cleanup":
        (root / "evidence/cleanup.json").unlink()
    else:
        raise RuntimeError("unknown mutation " + name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--temporary-root", default=str(TEMP_ROOT))
    args = parser.parse_args()
    root = Path(args.temporary_root).resolve()
    expected_root = TEMP_ROOT.resolve()
    if root != expected_root or not root.exists():
        raise RuntimeError("mutation root must be the existing exact P3-117 temporary root")
    control = root / "mutation-control"
    if control.exists():
        raise RuntimeError("mutation control already exists")
    shutil.copytree(TASK_ROOT, control, ignore=shutil.ignore_patterns("MANIFEST.md", "__pycache__"))
    exit_code, output = run(control)
    if exit_code != 0:
        raise RuntimeError("pristine disposable control did not pass: " + output)
    expectations = {
        "blank": "clean image unexpectedly blank",
        "monochrome": "clean image monochrome",
        "duplicate": "semantic-distinct clean screenshot reused",
        "wrong_viewport": "viewport does not match frozen label",
        "wrong_crop": "crop geometry outside raw parent",
        "browser_chrome": "forbidden browser chrome marker",
        "wrong_semantic": "semantic action mismatch",
        "source_drift": "fixed input ledger drift",
        "ambient_marker": "ambient marker found in task-local evidence",
        "probe_leak": "clean image still shows probe marker",
        "missing_raw_link": "missing raw lineage",
        "missing_cleanup": "cleanup proof absent",
    }
    rows = []
    for name, expected in expectations.items():
        disposable = root / ("mutation-" + name)
        shutil.copytree(control, disposable)
        mutate(disposable, name)
        exit_code, output = run(disposable)
        passed = exit_code != 0 and expected in output
        rows.append({"mutation": name, "expected_reason": expected, "exit_code": exit_code, "actual_output": output, "status": "PASS" if passed else "FAIL"})
    shutil.rmtree(control)
    for name in expectations:
        shutil.rmtree(root / ("mutation-" + name))
    result = {"task": "LIFEOS-P3-117", "clean_control": {"exit_code": 0, "status": "PASS"}, "mutations": rows, "all_pass": all(row["status"] == "PASS" for row in rows)}
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS" if result["all_pass"] else "FAIL", "mutations": len(rows)}, ensure_ascii=False))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
