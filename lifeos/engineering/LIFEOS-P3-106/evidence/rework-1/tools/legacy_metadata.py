#!/usr/bin/env python3
"""Metadata-only access for the legacy forbidden path. Never open or read it."""
import os, stat

LEGACY_PATH = "/private/tmp/lifeos-p3-104-rework-static-results.json"

def snapshot():
    try:
        value = os.lstat(LEGACY_PATH)
        return {"path": LEGACY_PATH, "exists": True, "type": stat.filemode(value.st_mode)[0], "size": value.st_size, "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns}
    except FileNotFoundError:
        return {"path": LEGACY_PATH, "exists": False}
