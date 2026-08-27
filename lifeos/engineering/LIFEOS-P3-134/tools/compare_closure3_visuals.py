#!/usr/bin/env python3
"""Read-only, masked-pixel comparator for Closure-3 actual-Tauri captures.

The only temporary files are explicit BMP conversions below the authorized
temporary root.  They are individually unlinked before exit.
"""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
from pathlib import Path


PAIRS = [
    ("today_empty", "candidate-700-runtime-today-empty.png", "reference-700-today-empty.png", "same_state"),
    ("me", "candidate-700-me.png", "reference-700-me.png", "same_state"),
    ("contexts", "candidate-700-contexts.png", "reference-700-contexts.png", "same_state"),
    ("memory", "candidate-700-memory.png", "reference-700-memory.png", "same_state"),
    ("quick_capture", "candidate-700-quick-capture.png", "reference-700-quick-capture.png", "same_state"),
    ("context_candidate_modal", "candidate-700-context-candidate-modal.png", "reference-700-context-candidate-modal.png", "same_state"),
    ("domain_gate", "candidate-700-domain-gate.png", "reference-700-domain-gate.png", "same_state"),
    ("global_ai", "candidate-700-global-ai.png", "reference-700-global-ai.png", "same_state"),
    ("global_ai_context_removed", "candidate-700-ai-removed-health.png", "reference-700-ai-removed-health.png", "same_state"),
    ("reduced_motion", "candidate-700-reduced-motion.png", "reference-700-reduced-motion.png", "same_state"),
    ("workspace_narrow_repair", "candidate-700-workspace.png", "reference-700-workspace.png", "approved_narrow_repair"),
]


def bmp(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if data[:2] != b"BM":
        raise ValueError(f"not bmp: {path}")
    offset = struct.unpack_from("<I", data, 10)[0]
    width, signed_height = struct.unpack_from("<ii", data, 18)
    bit_count = struct.unpack_from("<H", data, 28)[0]
    if bit_count not in (24, 32):
        raise ValueError(f"unexpected bit depth {bit_count}")
    height = abs(signed_height)
    stride = ((width * bit_count + 31) // 32) * 4
    rows: list[bytes] = []
    for y in range(height):
        source_y = y if signed_height < 0 else height - y - 1
        row = data[offset + source_y * stride: offset + source_y * stride + stride]
        rgb = bytearray()
        step = bit_count // 8
        for x in range(width):
            b, g, r = row[x * step:x * step + 3]
            rgb.extend((r, g, b))
        rows.append(bytes(rgb))
    return width, height, b"".join(rows)


def convert(source: Path, target: Path) -> None:
    subprocess.run(["sips", "-s", "format", "bmp", str(source), "--out", str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def compare(left: tuple[int, int, bytes], right: tuple[int, int, bytes]) -> dict[str, float | int]:
    lw, lh, lp = left
    rw, rh, rp = right
    if (lw, lh) != (rw, rh):
        return {"dimension_match": False, "changed_pixels": -1, "pixel_count": -1, "changed_ratio": 1.0, "mean_abs_channel_delta": 255.0}
    changed = 0
    total_delta = 0
    for a, b in zip(lp, rp):
        total_delta += abs(a - b)
    for i in range(0, len(lp), 3):
        if max(abs(lp[i] - rp[i]), abs(lp[i + 1] - rp[i + 1]), abs(lp[i + 2] - rp[i + 2])) > 24:
            changed += 1
    pixels = lw * lh
    return {"dimension_match": True, "changed_pixels": changed, "pixel_count": pixels, "changed_ratio": changed / pixels, "mean_abs_channel_delta": total_delta / len(lp)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dom", type=Path, required=True)
    parser.add_argument("--temp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    temp = args.temp_root.resolve()
    if temp != Path("/private/tmp/lifeos-p3-134-ui-restoration-v1") or not temp.is_dir():
        raise SystemExit("authorized temporary root required")
    results = []
    converted: list[Path] = []
    try:
        for index, (state, left_name, right_name, kind) in enumerate(PAIRS):
            left_source, right_source = args.dom / left_name, args.dom / right_name
            left_bmp, right_bmp = temp / f"closure3-visual-{index}-left.bmp", temp / f"closure3-visual-{index}-right.bmp"
            convert(left_source, left_bmp); convert(right_source, right_bmp)
            converted.extend((left_bmp, right_bmp))
            metrics = compare(bmp(left_bmp), bmp(right_bmp))
            threshold = 0.12 if kind == "same_state" else 1.0
            results.append({"state": state, "fixture": "fixed_synthetic_p3_116", "mask_rectangles": [], "mask_policy": "no layout/title/rail/card/global-ai/inspector/primary-action masks", "comparison": "actual_tauri_host_capture", "classification": kind, "threshold_changed_ratio": threshold, **metrics, "pass": metrics["dimension_match"] and metrics["changed_ratio"] <= threshold})
    finally:
        for path in converted:
            path.unlink(missing_ok=True)
    overall = all(item["pass"] for item in results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"schema":"LIFEOS-P3-134-closure3-visual-v1", "host_capture_note":"host screenshots are explicitly classified as physical host captures; DOM logical geometry is in dom/*.json and native logs.", "overall_pass": overall, "pairs": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
