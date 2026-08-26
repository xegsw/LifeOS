#!/usr/bin/env python3
"""Capture only the provided P3-117 app-mode window and create its crop lineage."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parent
CAPTURE_ROOT = TASK_ROOT / "evidence/captures"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"not a PNG with IHDR: {path}")
    return struct.unpack(">II", header[16:24])


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_quad(value: str) -> tuple[int, int, int, int]:
    parts = tuple(int(part) for part in value.split(","))
    if len(parts) != 4 or any(part < 0 for part in parts):
        raise ValueError("expected x,y,width,height with non-negative values")
    return parts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-id", required=True)
    parser.add_argument("--phase", choices=("proof", "clean"), required=True)
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--window-bounds", required=True)
    parser.add_argument("--crop", required=True)
    parser.add_argument("--viewport", required=True)
    parser.add_argument("--dpr", required=True, type=float)
    parser.add_argument("--signature", required=True)
    args = parser.parse_args()

    if not args.capture_id.startswith("P117-"):
        raise RuntimeError("capture id must be task-local P117-*")
    window_bounds = parse_quad(args.window_bounds)
    crop_x, crop_y, crop_w, crop_h = parse_quad(args.crop)
    raw_dir = CAPTURE_ROOT / "raw"
    crop_dir = CAPTURE_ROOT / args.phase
    geometry_dir = CAPTURE_ROOT / "geometry"
    raw_dir.mkdir(parents=True, exist_ok=True)
    crop_dir.mkdir(parents=True, exist_ok=True)
    geometry_dir.mkdir(parents=True, exist_ok=True)
    raw = raw_dir / f"{args.capture_id}-{args.phase}.png"
    cropped = crop_dir / f"{args.capture_id}.png"
    geometry_path = geometry_dir / f"{args.capture_id}.json"
    if raw.exists() or cropped.exists():
        raise RuntimeError(f"refusing to overwrite capture evidence: {args.capture_id}-{args.phase}")

    subprocess.run(["/usr/sbin/screencapture", "-x", "-l", str(args.window_id), str(raw)], check=True)
    raw_w, raw_h = png_size(raw)
    if crop_x + crop_w > raw_w or crop_y + crop_h > raw_h or crop_w == 0 or crop_h == 0:
        raise RuntimeError(f"crop is outside raw window: raw={raw_w}x{raw_h}; crop={args.crop}")
    subprocess.run([
        "/usr/bin/sips", "-c", str(crop_h), str(crop_w), "--cropOffset", str(crop_y), str(crop_x),
        str(raw), "--out", str(cropped),
    ], check=True, stdout=subprocess.DEVNULL)
    crop_size = png_size(cropped)
    if crop_size != (crop_w, crop_h):
        raise RuntimeError(f"crop dimensions mismatch: {crop_size} expected {(crop_w, crop_h)}")

    record = json.loads(geometry_path.read_text(encoding="utf-8")) if geometry_path.exists() else {
        "task": "LIFEOS-P3-117",
        "capture_id": args.capture_id,
        "window_id": str(args.window_id),
        "window_bounds": {"x": window_bounds[0], "y": window_bounds[1], "width": window_bounds[2], "height": window_bounds[3]},
        "viewport_css": args.viewport,
        "dpr": args.dpr,
        "crop": {"x": crop_x, "y": crop_y, "width": crop_w, "height": crop_h},
        "signature": args.signature,
        "phases": {},
    }
    if record["window_id"] != str(args.window_id) or record["signature"] != args.signature:
        raise RuntimeError("capture id cannot join different window or semantic signature")
    record["phases"][args.phase] = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_path": str(raw.relative_to(TASK_ROOT)),
        "raw_sha256": digest(raw),
        "raw_size": {"width": raw_w, "height": raw_h},
        "crop_path": str(cropped.relative_to(TASK_ROOT)),
        "crop_sha256": digest(cropped),
        "crop_size": {"width": crop_size[0], "height": crop_size[1]},
        "source": "macOS screencapture -l unique P3-117 app-mode window",
    }
    write_json(geometry_path, record)
    print(json.dumps({"result": "PASS", "capture_id": args.capture_id, "phase": args.phase, "raw": str(raw), "crop": str(cropped)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
