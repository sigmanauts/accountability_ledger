# Scripts Guide

This directory contains helper scripts for scaffolding cases, validating repository structure, computing checksums, and packaging regulator-ready bundles.

## Canonical workflows (recommended)

- Scaffold a new case (choose one):
  - Makefile (recommended): `make new-case ENTITY_ID=htx SLUG=notice-of-intent`
  - Shell script: `bash scripts/new_case.sh -c scripts/case.config` (or provide flags)

- Validate repository:
  - Makefile: `make validate`
  - Shell wrapper: `bash scripts/finalize.sh` (runs validation under the hood)

- Compute/refresh checksums:
  - Makefile: `make checksums`
  - Python: `python3 scripts/compute_checksums.py`

- Package a MAS‑ready zip (optional):
  - Makefile: `make package-mas CASE=cases/htx-notice-of-intent`
  - Shell wrapper: `bash scripts/finalize.sh --package cases/htx-notice-of-intent`
  - Include checksums during packaging: add `--with-checksums`

Notes:
- Use UTC ISO 8601 timestamps (e.g., `2025-09-18T00:00:00Z`).
- Before opening a PR, run `make validate` to catch structure/metadata issues.
- All commits must include DCO sign-off (`git commit -s`).

## Script reference

### new_case.sh (shell scaffolder)
- Purpose: Scaffold a new case directory and an initial timeline entry from a config file or flags.
- Usage:
  - Config file: `bash scripts/new_case.sh -c scripts/case.config`
  - Flags: `bash scripts/new_case.sh -e entity-id -s slug -d "2025-01-01T00:00:00Z" -a "actor1,actor2" -C "Claim" [-C "..."] [-R "type|Label|Value"] [-n notice.md]`
- Output:
  - `cases/{entity}-{slug}/README.md` (case skeleton)
  - `cases/{entity}-{slug}/timeline/YYYY-MM-DD-{slug}.md` (front matter populated; canonical location)
  - Optionally copies a notice letter into the case directory when `-n` is provided.
- Notes:
  - Entity/slug must match `[a-z0-9-]+`.
  - References `type` in `{url,hash,onchain,file}`.

### new_case.py (Python scaffolder)
- Purpose: Programmatic/Makefile-friendly equivalent scaffolder.
- Usage:
  - `make new-case ENTITY_ID=foo SLUG=bar`
  - Direct: `ENTITY_ID=foo SLUG=bar python3 scripts/new_case.py`
  - CLI: `python3 scripts/new_case.py --entity foo --slug bar`
- Output:
  - `cases/{entity}-{slug}/` with case skeleton.

### finalize.sh (shell wrapper)
- Purpose: Convenience wrapper that runs validation and (optionally) packages a MAS-ready zip.
- Usage:
  - Validate only: `bash scripts/finalize.sh`
  - Validate + package: `bash scripts/finalize.sh --package cases/{entity}-{slug}`
  - With checksums: add `--with-checksums` to compute per-directory `SHA256SUMS.txt` before packaging.
- Internals:
  - Calls `scripts/validate_repo.py` (with or without `--with-checksums`)
  - Calls `scripts/package_mas.py` when `--package` is supplied

### validate_repo.py (validator)
- Purpose: Validate repository structure and metadata.
- Checks:
  - Case folder naming: `cases/{entity}-{slug}` (lowercase, hyphenated)
  - Timeline filenames and front matter (date/actors/claims); date matches filename prefix and is ISO 8601
  - Optional: checksum manifests `SHA256SUMS.txt` when `--with-checksums` is used
- Usage:
  - `python3 scripts/validate_repo.py`
  - `python3 scripts/validate_repo.py --with-checksums`

### compute_checksums.py (checksum manager)
- Purpose: Maintain per-directory `SHA256SUMS.txt` manifests across tracked trees (`evidence/`, `cases/`, `timeline/`, `analysis/`, `mas_package/`).
- Usage:
  - Write/update: `python3 scripts/compute_checksums.py` (or `make checksums`)
  - Verify only: `python3 scripts/compute_checksums.py --check`

### package_mas.py (packager)
- Purpose: Create `mas_package/<case>-<UTC>.zip` bundles with a `manifest.json` for audit.
- Usage:
  - `python3 scripts/package_mas.py --case cases/{entity}-{slug}`
  - Makefile target: `make package-mas CASE=cases/{entity}-{slug}`

### case.config.example (config template)
- Purpose: Minimal editable config for `new_case.sh`.
- Usage:
  - `cp scripts/case.config.example scripts/case.config` and edit values
  - Then run `bash scripts/new_case.sh -c scripts/case.config`

## Makefile targets (mapping)

- `make new-case ENTITY_ID=foo SLUG=bar` → `scripts/new_case.py`
- `make validate` → `scripts/validate_repo.py`
- `make checksums` → `scripts/compute_checksums.py`
- `make package-mas CASE=cases/foo-bar` → `scripts/package_mas.py`

## Deprecations / legacy

- No scripts are deprecated at this time. Both shell (`new_case.sh`, `finalize.sh`) and Makefile/Python flows are supported.
- For consistency with CI and team workflows, prefer Makefile targets where convenient. Shell scripts remain available for environments without Make installed.

## Tips

- Timeline location: canonical path is `cases/{entity}-{slug}/timeline/YYYY-MM-DD-{slug}.md`. The legacy global `timeline/` at repo root is still validated for back-compat.
- Keep evidence under the appropriate case directory and reference files in timeline entries via `references` front matter.
- Use `make validate` locally before opening a PR; CI also runs validation and DCO checks.
- Consider running packaging with checksums for regulator-facing bundles.
