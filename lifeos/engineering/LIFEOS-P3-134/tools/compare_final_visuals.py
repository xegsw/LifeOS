#!/usr/bin/env python3
"""Compare fresh actual-Tauri P3-116 reference and candidate captures by state."""
from __future__ import annotations

import argparse
import json
import struct
import subprocess
from pathlib import Path


STATES = (
    "today-empty", "today-insufficient", "today-normal", "me", "contexts",
    "context-detail", "memory", "memory-detail", "global-ai",
    "global-ai-health-removed", "workspace", "quick-capture",
    "context-candidate", "domain-gate", "settings-reduced",
)


def bmp(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if data[:2] != b"BM":
        raise ValueError(f"not BMP: {path}")
    offset = struct.unpack_from("<I", data, 10)[0]
    width, signed_height = struct.unpack_from("<ii", data, 18)
    bit_count = struct.unpack_from("<H", data, 28)[0]
    if bit_count not in (24, 32):
        raise ValueError(f"unexpected BMP bit depth: {bit_count}")
    height = abs(signed_height)
    stride = ((width * bit_count + 31) // 32) * 4
    rows = []
    for y in range(height):
        source_y = y if signed_height < 0 else height - y - 1
        row = data[offset + source_y * stride: offset + source_y * stride + stride]
        pixels = bytearray()
        for x in range(width):
            start = x * (bit_count // 8)
            blue, green, red = row[start:start + 3]
            pixels.extend((red, green, blue))
        rows.append(bytes(pixels))
    return width, height, b"".join(rows)


def convert(source: Path, target: Path) -> None:
    subprocess.run(["sips", "-s", "format", "bmp", str(source), "--out", str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def compare(left: tuple[int, int, bytes], right: tuple[int, int, bytes], mask_height: int) -> dict[str, float | int | bool]:
    lw, lh, lp = left
    rw, rh, rp = right
    if (lw, lh) != (rw, rh):
        return {"dimension_match": False, "changed_pixels": -1, "pixel_count": -1, "changed_ratio": 1.0, "mean_abs_channel_delta": 255.0}
    changed = 0
    delta = 0
    considered = 0
    for y in range(lh):
        if y < mask_height:
            continue
        for x in range(lw):
            index = (y * lw + x) * 3
            triplet = [abs(lp[index + c] - rp[index + c]) for c in range(3)]
            delta += sum(triplet)
            considered += 1
            if max(triplet) > 24:
                changed += 1
    return {
        "dimension_match": True,
        "changed_pixels": changed,
        "pixel_count": considered,
        "changed_ratio": changed / considered if considered else 1.0,
        "mean_abs_channel_delta": delta / (considered * 3) if considered else 255.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--temp-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected = Path("/private/tmp/lifeos-p3-134-ui-restoration-v1")
    temp = args.temp_root.resolve()
    if temp != expected or not temp.is_dir() or temp.is_symlink():
        raise SystemExit("authorized ordinary temporary root required")
    converted: list[Path] = []
    pairs = []
    try:
        for index, state in enumerate(STATES):
            candidate = args.images / f"visual-candidate-{state}.png"
            reference = args.images / f"visual-reference-{state}.png"
            if not candidate.is_file() or not reference.is_file():
                raise SystemExit(f"missing actual-Tauri capture for {state}")
            left = temp / f"final-visual-{index}-candidate.bmp"
            right = temp / f"final-visual-{index}-reference.bmp"
            convert(candidate, left)
            convert(reference, right)
            converted.extend((left, right))
            metrics = compare(bmp(left), bmp(right), mask_height=32)
            approved_repair = state == "workspace"
            threshold = 1.0 if approved_repair else 0.12
            pairs.append({
                "state": state,
                "fixture": "fixed_non_sensitive_p3_116_fixture",
                "comparison": "fresh_actual_tauri_physical_host_capture",
                "host_capture_note": "host titlebar only is masked; no product layout, Rail, title, card, Global AI, Inspector, or primary-action region is masked",
                "mask_rectangles": [[0, 0, 700, 32]],
                "classification": "approved_700_workspace_narrow_repair" if approved_repair else "same_state",
                "threshold_changed_ratio": threshold,
                **metrics,
                "pass": bool(metrics["dimension_match"] and metrics["changed_ratio"] <= threshold),
            })
    finally:
        for path in converted:
            path.unlink(missing_ok=True)
    result = {
        "task": "LIFEOS-P3-134",
        "kind": "fresh_actual_tauri_masked_pixel_comparison",
        "overall_pass": all(item["pass"] for item in pairs),
        "pairs": pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
