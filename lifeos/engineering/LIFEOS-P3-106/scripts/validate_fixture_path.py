#!/usr/bin/env python3
import re
import sys

ALLOWED = re.compile(r"^/private/tmp/lifeos-p3-104-p3-106-(app|replay|dangling-final|dangling-journal|dangling-wal|dangling-shm|path|tamper|a11y|visual)-[a-z0-9-]+$")
if len(sys.argv) != 2 or not ALLOWED.fullmatch(sys.argv[1]):
    print("fixture path rejected", file=sys.stderr)
    raise SystemExit(64)
print(sys.argv[1])
