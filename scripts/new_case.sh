#!/usr/bin/env bash
set -euo pipefail

# Scaffold a new case and timeline entry from simple inputs.
# Usage:
#   scripts/new_case.sh -c scripts/case.config
#   scripts/new_case.sh -e entity-id -s slug -d "2025-01-01T00:00:00Z" -a "actor1,actor2" -C "Main claim" [-C "Another claim"] [-R "url|Label|https://..."] [-n path/to/notice.md]
#
# Config file example (scripts/case.config.example):
#   ENTITY_ID="example-entity"
#   SLUG="sample"
#   DATE="2025-01-01T00:00:00Z"
#   ACTORS="ergo-foundation,huobi"
#   CLAIMS=("Notice of intent to commence legal proceedings" "Attempted bribery and extortion")
#   REFS=("url|Public tweet|https://twitter.com/..." "file|Notice letter|cases/example-entity-sample/notice_of_intent.md")
#   NOTICE_LETTER="path/to/notice.md"
#
# Notes:
# - ACTORS is comma-separated string.
# - CLAIMS and REFS can be arrays in config or provided via repeated -C / -R flags.

CONFIG=""
ENTITY_ID=""
SLUG=""
DATE_ISO=""
ACTORS=""
NOTICE_LETTER=""
declare -a CLAIMS=()
declare -a REFS=()

usage() {
  cat >&2 <<EOF
Usage:
  $0 -c scripts/case.config
  $0 -e entity-id -s slug -d "2025-01-01T00:00:00Z" -a "actor1,actor2" -C "Main claim" [-C "..."] [-R "type|Label|Value"] [-n notice.md]

Options:
  -c  Path to config file (shell syntax)
  -e  Entity ID (lowercase, hyphenated)
  -s  Short slug (lowercase, hyphenated)
  -d  ISO 8601 UTC date/time (e.g., 2025-01-01T00:00:00Z)
  -a  Actors (comma-separated)
  -C  Claim (repeatable)
  -R  Reference "type|Label|Value" repeatable, type in {url,hash,onchain,file}
  -n  Path to notice letter file to copy into the case directory
  -h  Help
EOF
}

# Parse CLI
while getopts ":c:e:s:d:a:C:R:n:h" opt; do
  case "$opt" in
    c) CONFIG="$OPTARG" ;;
    e) ENTITY_ID="$OPTARG" ;;
    s) SLUG="$OPTARG" ;;
    d) DATE_ISO="$OPTARG" ;;
    a) ACTORS="$OPTARG" ;;
    C) CLAIMS+=("$OPTARG") ;;
    R) REFS+=("$OPTARG") ;;
    n) NOTICE_LETTER="$OPTARG" ;;
    h) usage; exit 0 ;;
    \?) echo "Unknown option: -$OPTARG" >&2; usage; exit 2 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage; exit 2 ;;
  esac
done

# Load config if provided
if [[ -n "${CONFIG}" ]]; then
  # shellcheck disable=SC1090
  source "${CONFIG}"
  # Allow config to set variables if not overridden by flags
  ENTITY_ID="${ENTITY_ID:-${ENTITY_ID:-${ENTITY_ID}}}"
  SLUG="${SLUG:-${SLUG:-${SLUG}}}"
  DATE_ISO="${DATE_ISO:-${DATE:-${DATE_ISO:-}}}"
  ACTORS="${ACTORS:-${ACTORS:-}}"
  # Config may define arrays CLAIMS and REFS. If flags also supplied, append them.
  if [[ ${#CLAIMS[@]} -eq 0 && -n "${CLAIMS-}" ]]; then
    : # already populated by config as array
  fi
  if [[ ${#REFS[@]} -eq 0 && -n "${REFS-}" ]]; then
    : # already populated by config as array
  fi
  if [[ -n "${NOTICE_LETTER-}" && -z "${NOTICE_LETTER}" ]]; then
    NOTICE_LETTER="${NOTICE_LETTER}"
  fi
fi

# Interactive prompts if still missing
if [[ -z "${ENTITY_ID}" ]]; then
  read -r -p "Entity ID (lowercase, hyphenated): " ENTITY_ID
fi
if [[ -z "${SLUG}" ]]; then
  read -r -p "Case slug (lowercase, hyphenated): " SLUG
fi
if [[ -z "${DATE_ISO}" ]]; then
  read -r -p "Event date/time (ISO 8601 UTC, e.g., 2025-01-01T00:00:00Z): " DATE_ISO
fi
if [[ -z "${ACTORS}" ]]; then
  read -r -p "Actors (comma-separated): " ACTORS
fi
if [[ ${#CLAIMS[@]} -eq 0 ]]; then
  read -r -p "Claim (short sentence): " one_claim || true
  if [[ -n "${one_claim:-}" ]]; then CLAIMS+=("${one_claim}"); fi
fi

# Basic validation
if ! [[ "${ENTITY_ID}" =~ ^[a-z0-9-]+$ ]]; then
  echo "Invalid ENTITY_ID '${ENTITY_ID}' (expected [a-z0-9-]+)" >&2; exit 2
fi
if ! [[ "${SLUG}" =~ ^[a-z0-9-]+$ ]]; then
  echo "Invalid SLUG '${SLUG}' (expected [a-z0-9-]+)" >&2; exit 2
fi
if ! [[ "${DATE_ISO}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
  echo "Warning: DATE '${DATE_ISO}' not in strict ISO 8601 Zulu format (YYYY-MM-DDTHH:MM:SSZ)." >&2
fi

# Prepare paths
CASE_DIR="cases/${ENTITY_ID}-${SLUG}"
TIMEDATE="${DATE_ISO%%T*}"   # YYYY-MM-DD
TIMELINE_FILE="timeline/${TIMEDATE}-${SLUG}.md"

mkdir -p "${CASE_DIR}/evidence" "${CASE_DIR}/notes" "timeline"

# Write case README (from template with substitutions)
cat > "${CASE_DIR}/README.md" <<EOF
# Case: ${ENTITY_ID} - ${SLUG}

- Entity ID: ${ENTITY_ID}
- Slug: ${SLUG}
- Created (UTC, ISO 8601): ${DATE_ISO}

## Summary
Short description of the case.

## Actors
- ${ENTITY_ID}
EOF

# Add optional additional actors (beyond entity)
IFS=',' read -r -a _actors <<<"${ACTORS}"
for act in "${_actors[@]}"; do
  act_trim="$(echo "$act" | awk '{$1=$1};1')"
  if [[ -n "${act_trim}" && "${act_trim}" != "${ENTITY_ID}" ]]; then
    echo "- ${act_trim}" >> "${CASE_DIR}/README.md"
  fi
done

cat >> "${CASE_DIR}/README.md" <<'EOF'

## Timeline
List dated events with references. Create entries in `timeline/` as `YYYY-MM-DD-<slug>.md`.

## Sources
- File:
  - Location:
  - SHA-256:
  - Provenance (durable link / content hash / on-chain ref):
  - Notes:

## Checksums
(Optional) Run packaging script to include hashes for regulator bundles.

## Redactions
If any redactions are made, include a cover note using `templates/forms/cover_note_redactions.md`.
EOF

# Copy notice letter if provided
if [[ -n "${NOTICE_LETTER}" ]]; then
  dest="${CASE_DIR}/notice_of_intent$(printf "%s" "${NOTICE_LETTER##*.}" | awk '{if ($0!="") print "."$0; else print "";}')"
  cp -f "${NOTICE_LETTER}" "${dest}"
  echo "Copied notice letter to ${dest}"
fi

# Build timeline YAML
{
  echo "---"
  echo "date: ${DATE_ISO}"
  echo "actors:"
  for act in "${_actors[@]}"; do
    act_trim="$(echo "$act" | awk '{$1=$1};1')"
    [[ -n "${act_trim}" ]] && echo "  - ${act_trim}"
  done
  echo "claims:"
  if [[ ${#CLAIMS[@]} -gt 0 ]]; then
    for c in "${CLAIMS[@]}"; do
      echo "  - ${c}"
    done
  else
    echo "  - ${ENTITY_ID} case ${SLUG} created."
  fi
  if [[ ${#REFS[@]} -gt 0 ]]; then
    echo "references:"
    for r in "${REFS[@]}"; do
      IFS='|' read -r rtype rlabel rvalue <<<"${r}"
      echo "  - type: ${rtype}"
      if [[ -n "${rlabel:-}" ]]; then echo "    label: ${rlabel}"; fi
      echo "    value: ${rvalue}"
    done
  fi
  echo "---"
  echo
  echo "Initial timeline entry scaffolded."
} > "${TIMELINE_FILE}"

echo "Created case at ${CASE_DIR}"
echo "Created timeline entry ${TIMELINE_FILE}"
echo
echo "Next steps:"
echo "  - Edit ${CASE_DIR}/README.md to add summary and sources."
echo "  - Attach any supporting files under ${CASE_DIR}/evidence/."
echo "  - Optionally run scripts/finalize.sh --package ${CASE_DIR} to build a MAS-ready zip."
