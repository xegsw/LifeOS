#!/usr/bin/env python3
"""Fail-closed verifier for P3-117 native image and action-semantic Evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TASK_ROOT.parents[2]
TEMP_ROOT = Path("/private/tmp/lifeos-p3-117-native-capture-v1")
FIXED = {
    "lifeos/prototypes/LIFEOS-P3-116/index.html": "d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b",
    "lifeos/prototypes/LIFEOS-P3-116/app.js": "c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f",
    "lifeos/prototypes/LIFEOS-P3-116/styles.css": "cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3",
    "lifeos/prototypes/LIFEOS-P3-116/fixtures.js": "a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93",
    "lifeos/prototypes/LIFEOS-P3-116/interaction_contract.md": "584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393",
    "lifeos/prototypes/LIFEOS-P3-116/state_machine.json": "2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc",
    "lifeos/prototypes/LIFEOS-P3-116/visual_contract.json": "c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49",
    "lifeos/prototypes/LIFEOS-P3-116/ia_reconciliation.md": "bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467",
    "lifeos/reviews/LIFEOS-P3-116_pm_review.md": "09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa",
    "lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/MANIFEST.md": "58e778aeeb3f8c7306d8981409a1a0aae234c7137fae9eb3b660355c1cdc969b",
    "lifeos/prototypes/LIFEOS-P3-116/evidence/rework-1/attempt-2/MANIFEST.md": "e41fe9514af6df1b6e272f92cf4c100f4b9f1bc1c3f4137c69a8a2a591aa3799",
    "lifeos/reviews/LIFEOS-P3-116/pm_evidence/rework-1/attempt_2_blocked_assessment.md": "4dde5d041f7d29875a5efb131c1568c425f2ff63d359eb90dd1f4a32a797fc2a",
    "lifeos/ACCEPTANCE_GOVERNANCE.md": "86b2837ea0c78b1d4d1609680114c6e213f9a31b7b751db1dfb052540aa4372c",
}


class VerificationError(RuntimeError):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_color(value: str) -> tuple[int, int, int]:
    value_hash = 2166136261
    for char in value:
        value_hash ^= ord(char)
        value_hash = (value_hash * 16777619) & 0xffffffff
    return tuple(56 + ((value_hash >> shift) & 0x8f) for shift in (0, 8, 16))


def read_png(path: Path) -> tuple[int, int, int, bytes]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise VerificationError("image is not a decodable PNG")
    offset, width, height, bit_depth, color_type, chunks = 8, None, None, None, None, []
    while offset < len(data):
        if offset + 12 > len(data):
            raise VerificationError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        tag = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        if len(body) != length:
            raise VerificationError("truncated PNG body")
        if tag == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", body)
            if compression or filter_method or interlace or bit_depth != 8 or color_type not in (2, 6):
                raise VerificationError("unsupported PNG encoding")
        elif tag == b"IDAT":
            chunks.append(body)
        elif tag == b"IEND":
            break
        offset += 12 + length
    if not width or not height or not chunks:
        raise VerificationError("PNG missing image payload")
    channels = 4 if color_type == 6 else 3
    stride = width * channels
    packed = zlib.decompress(b"".join(chunks))
    if len(packed) != height * (stride + 1):
        raise VerificationError("unexpected PNG scanline length")
    rows, prior, cursor = bytearray(), bytearray(stride), 0
    for _ in range(height):
        kind = packed[cursor]
        cursor += 1
        raw = bytearray(packed[cursor:cursor + stride])
        cursor += stride
        for index in range(stride):
            left = raw[index - channels] if index >= channels else 0
            up = prior[index]
            up_left = prior[index - channels] if index >= channels else 0
            if kind == 1:
                raw[index] = (raw[index] + left) & 0xff
            elif kind == 2:
                raw[index] = (raw[index] + up) & 0xff
            elif kind == 3:
                raw[index] = (raw[index] + ((left + up) // 2)) & 0xff
            elif kind == 4:
                prediction = left + up - up_left
                pa, pb, pc = abs(prediction - left), abs(prediction - up), abs(prediction - up_left)
                raw[index] = (raw[index] + (left if pa <= pb and pa <= pc else up if pb <= pc else up_left)) & 0xff
            elif kind != 0:
                raise VerificationError("unsupported PNG filter")
        rows.extend(raw)
        prior = raw
    return width, height, channels, bytes(rows)


def image_stats(path: Path, target: tuple[int, int, int] | None = None) -> dict:
    width, height, channels, pixels = read_png(path)
    sample_step = max(1, (width * height) // 20000)
    samples, colors, luminance_sum, luminance_sq = 0, set(), 0, 0
    marker = 0
    for pixel_index in range(0, width * height, sample_step):
        offset = pixel_index * channels
        red, green, blue = pixels[offset:offset + 3]
        colors.add((red // 8, green // 8, blue // 8))
        lum = (red * 299 + green * 587 + blue * 114) // 1000
        luminance_sum += lum
        luminance_sq += lum * lum
        samples += 1
    if target:
        red_target, green_target, blue_target = target
        for offset in range(0, len(pixels), channels):
            red, green, blue = pixels[offset:offset + 3]
            if abs(red - red_target) <= 5 and abs(green - green_target) <= 5 and abs(blue - blue_target) <= 5:
                marker += 1
    mean = luminance_sum / samples
    variance = luminance_sq / samples - mean * mean
    return {"width": width, "height": height, "colors": len(colors), "variance": variance, "marker_pixels": marker}


def json_file(root: Path, relative: str) -> dict:
    path = root / relative
    if not path.is_file():
        raise VerificationError("missing required file: " + relative)
    return json.loads(path.read_text(encoding="utf-8"))


def fail(condition: bool, reason: str) -> None:
    if condition:
        raise VerificationError(reason)


def verify_manifest(root: Path) -> None:
    path = root / "MANIFEST.md"
    if not path.exists():
        raise VerificationError("Manifest absent")
    listed = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| ([^|]+) \| (\d+) \| ([0-9a-f]{64}) \|$", line)
        if match:
            listed[match.group(1)] = (int(match.group(2)), match.group(3))
    actual = {}
    for item in root.rglob("*"):
        if item.is_file() and item != path and "__pycache__" not in item.parts:
            rel = str(item.relative_to(root))
            actual[rel] = (item.stat().st_size, sha(item))
    fail(set(listed) != set(actual), "Manifest missing or extra payload entry")
    for rel, value in actual.items():
        fail(listed[rel] != value, "Manifest hash or byte mismatch")


def verify(root: Path, allow_temp_present: bool, check_manifest: bool) -> dict:
    for relative, expected in FIXED.items():
        fail(sha(PROJECT_ROOT / relative) != expected, "fixed input source drift")
    fixed = json_file(root, "evidence/preflight/fixed_inputs.json")
    for relative, expected in FIXED.items():
        item = fixed["inputs"].get(relative)
        fail(item is None or item.get("expected") != expected or item.get("sha256") != expected or not item.get("match"), "fixed input ledger drift")
    probe = json_file(root, "evidence/preflight/probe_audit.json")
    fail(probe.get("result") != "PASS" or probe.get("forbidden_hits"), "probe audit failed")
    plan = json_file(root, "test_plan.json")
    results_doc = json_file(root, "evidence/action_results.json")
    expected_cases = {item["case_id"]: item for item in plan["cases"]}
    result_rows = results_doc.get("results", [])
    seen_cases, semantic_hashes = set(), {}
    action_count = 0
    for row in result_rows:
        case_id = row.get("case_id")
        fail(case_id not in expected_cases or case_id in seen_cases, "closure case missing or duplicated")
        seen_cases.add(case_id)
        case = expected_cases[case_id]
        fail(row.get("status") != "PASS", "closure row not PASS")
        fail(row.get("actual_action") != case["action"], "semantic action mismatch")
        geometry_rel = row.get("geometry_path")
        geometry_path = root / geometry_rel
        fail(not geometry_path.is_file(), "missing geometry linkage")
        fail(row.get("geometry_sha256") != sha(geometry_path), "geometry hash mismatch")
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
        fail(geometry.get("signature", "").split("|", 1)[0] != case["action"], "probe semantic action mismatch")
        if case.get("viewport"):
            fail(geometry.get("viewport_css") != case["viewport"], "viewport does not match frozen label")
        fail(geometry.get("forbidden_content"), "forbidden browser chrome marker")
        phases = geometry.get("phases", {})
        for phase in ("proof", "clean"):
            fail(phase not in phases, "missing raw lineage")
            phase_info = phases[phase]
            raw = root / phase_info.get("raw_path", "")
            crop_path = root / phase_info.get("crop_path", "")
            fail(not raw.is_file() or not crop_path.is_file(), "missing raw lineage")
            fail(phase_info.get("raw_sha256") != sha(raw) or phase_info.get("crop_sha256") != sha(crop_path), "raw or crop hash mismatch")
            raw_stats = image_stats(raw)
            crop_stats = image_stats(crop_path)
            crop = geometry["crop"]
            fail(crop["x"] + crop["width"] > raw_stats["width"] or crop["y"] + crop["height"] > raw_stats["height"], "crop geometry outside raw parent")
            fail((crop_stats["width"], crop_stats["height"]) != (crop["width"], crop["height"]), "crop dimensions mismatch")
            fail(crop_stats["width"] < 500 or crop_stats["height"] < 350, "page crop too small")
            fail(crop_stats["colors"] < 8 or crop_stats["variance"] < 5, "clean image unexpectedly blank" if phase == "clean" else "proof image unexpectedly blank")
            fail(crop_stats["colors"] < 16, "clean image monochrome" if phase == "clean" else "proof image monochrome")
        signature_color = marker_color(geometry["signature"])
        proof_stats = image_stats(root / phases["proof"]["crop_path"], signature_color)
        clean_path = root / phases["clean"]["crop_path"]
        clean_stats = image_stats(clean_path, signature_color)
        fail(proof_stats["marker_pixels"] < 80, "probe semantic marker missing")
        fail(clean_stats["marker_pixels"] >= 40, "clean image still shows probe marker")
        clean_hash = sha(clean_path)
        semantic = row["matrix"] + "|" + row["expected_anchor"] + "|" + geometry["viewport_css"]
        if semantic in semantic_hashes and not row.get("allow_same_state"):
            fail(semantic_hashes[semantic] == clean_hash, "semantic-distinct clean screenshot reused")
        semantic_hashes[semantic] = clean_hash
        action_count += 1
    fail(set(expected_cases) != seen_cases, "closure required action missing")
    raw_action_text = (root / "evidence/action_results.json").read_text(encoding="utf-8")
    fail("ambient-chrome-tab" in raw_action_text or "browser-history-export" in raw_action_text, "ambient marker found in task-local evidence")
    cleanup = root / "evidence/cleanup.json"
    fail(not cleanup.is_file(), "cleanup proof absent")
    cleanup_doc = json.loads(cleanup.read_text(encoding="utf-8"))
    if allow_temp_present:
        fail(cleanup_doc.get("status") not in ("pending", "complete"), "cleanup proof invalid")
    else:
        fail(cleanup_doc.get("status") != "complete" or TEMP_ROOT.exists(), "cleanup result not final")
    if check_manifest:
        verify_manifest(root)
    return {"result": "PASS", "actions": action_count, "fixed_inputs": len(FIXED), "manifest_checked": check_manifest, "cleanup_status": cleanup_doc["status"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(TASK_ROOT))
    parser.add_argument("--allow-temp-present", action="store_true")
    parser.add_argument("--skip-manifest", action="store_true")
    parser.add_argument("--write", type=str)
    args = parser.parse_args()
    try:
        result = verify(Path(args.root).resolve(), args.allow_temp_present, not args.skip_manifest)
        if args.write:
            destination = Path(args.write)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"result": "FAIL", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
