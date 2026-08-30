#!/bin/sh
set -eu

temp_root="/private/tmp/lifeos-p3-141-controlled-pilot-v1"
case "$temp_root" in
  /private/tmp/lifeos-p3-141-controlled-pilot-v1) ;;
  *) echo "unexpected cleanup target" >&2; exit 64 ;;
esac
rm -rf -- "$temp_root"
if [ -e "$temp_root" ]; then
  echo "cleanup verification failed" >&2
  exit 1
fi
printf '%s\n' "P3-141 temp root removed exactly"
