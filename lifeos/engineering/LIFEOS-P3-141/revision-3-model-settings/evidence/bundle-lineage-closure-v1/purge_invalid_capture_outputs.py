#!/usr/bin/env python3
"""Remove only capture outputs produced before target-window text isolation.

This intentionally enumerates exact evidence files.  It never traverses a
directory and does not contact any temporary runtime root.
"""

from pathlib import Path


EVIDENCE = Path(__file__).resolve().parent
INVALID_OUTPUTS = (
    "gui/compact-capture.json",
    "gui/compact-pid-exit.txt",
    "gui/compact-viewport-receipt.json",
    "gui/desktop-capture.json",
    "gui/desktop-pid-exit.txt",
    "gui/desktop-settings.png",
    "gui/desktop-viewport-receipt.json",
)


def main() -> None:
    removed: list[str] = []
    already_absent: list[str] = []
    for relative in INVALID_OUTPUTS:
        target = EVIDENCE / relative
        try:
            target.lstat()
        except FileNotFoundError:
            already_absent.append(relative)
            continue
        if target.is_dir():
            raise RuntimeError(f"refusing directory target: {target}")
        target.unlink()
        removed.append(relative)
    print({"removed": removed, "already_absent": already_absent})


if __name__ == "__main__":
    main()
