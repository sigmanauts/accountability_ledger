#!/usr/bin/env bash
set -euo pipefail

# Finalize workflow:
# - Basic validation (naming + timeline front matter)
# - Optional: write per-directory SHA256SUMS.txt manifests
# - Optional: package a case to mas_package/<case>-<UTC>.zip (includes manifest.json)
#
# Usage:
#   scripts/finalize.sh
#   scripts/finalize.sh --with-checksums
#   scripts/finalize.sh --package cases/<entity-id>-<slug>
#   scripts/finalize.sh --with-checksums --package cases/<entity-id>-<slug>

WITH_CHECKSUMS=0
PACKAGE_CASE=""

usage() {
  cat >&2 <<EOF
Usage:
  $0 [--with-checksums] [--package cases/<entity-id>-<slug>]

Options:
  --with-checksums   Write per-directory SHA256SUMS.txt manifests before packaging (optional)
  --package PATH     Package the given case directory to mas_package/<case>-<UTC>.zip

Examples:
  $0
  $0 --with-checksums
  $0 --package cases/example-entity-sample
  $0 --with-checksums --package cases/example-entity-sample
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-checksums) WITH_CHECKSUMS=1; shift ;;
    --package) PACKAGE_CASE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

have_python() { command -v python3 >/dev/null 2>&1; }

# 1) Optional checksums
if [[ "${WITH_CHECKSUMS}" -eq 1 ]]; then
  echo "[finalize] Writing per-directory SHA256SUMS.txt manifests..."
  if have_python; then
    python3 scripts/compute_checksums.py
  else
    echo "python3 not found; cannot compute checksums." >&2
    exit 2
  fi
fi

# 2) Validate repository (naming + timeline front matter)
echo "[finalize] Validating repository..."
if have_python; then
  if [[ "${WITH_CHECKSUMS}" -eq 1 ]]; then
    python3 scripts/validate_repo.py --with-checksums
  else
    python3 scripts/validate_repo.py
  fi
else
  echo "python3 not found; cannot validate repository." >&2
  exit 2
fi

# 3) Optional packaging
if [[ -n "${PACKAGE_CASE}" ]]; then
  if [[ ! -d "${PACKAGE_CASE}" ]]; then
    echo "[finalize] Case path not found: ${PACKAGE_CASE}" >&2
    exit 2
  fi
  echo "[finalize] Packaging case ${PACKAGE_CASE}..."
  if have_python; then
    python3 scripts/package_mas.py --case "${PACKAGE_CASE}"
  else
    echo "python3 not found; cannot package case." >&2
    exit 2
  fi
fi

echo "[finalize] Done."
