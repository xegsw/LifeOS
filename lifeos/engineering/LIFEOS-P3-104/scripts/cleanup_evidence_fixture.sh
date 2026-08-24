#!/bin/sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FIXTURE_ROOT=/private/tmp/lifeos-p3-104-app-evidence
EXPECTED=/private/tmp/lifeos-p3-104-app-evidence
LOG="$PROJECT_ROOT/evidence/cleanup.log"

if [ "$FIXTURE_ROOT" != "$EXPECTED" ] || [ -L "$FIXTURE_ROOT" ]; then
  echo "Refusing cleanup: fixture root is not the exact non-link target." >&2
  exit 2
fi
if [ -d "$FIXTURE_ROOT" ]; then
  rm -rf /private/tmp/lifeos-p3-104-app-evidence
fi
if [ -e "$FIXTURE_ROOT" ] || [ -L "$FIXTURE_ROOT" ]; then
  echo "Cleanup failed: exact fixture remains." >&2
  exit 3
fi
{
  echo "task=LIFEOS-P3-104"
  echo "target=/private/tmp/lifeos-p3-104-app-evidence"
  echo "status=PASS"
  echo "residual=0"
} > "$LOG"

