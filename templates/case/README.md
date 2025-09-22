# Case: <entity-id> - <short-slug>

- Entity ID: <entity-id>
- Slug: <short-slug>
- Created (UTC, ISO 8601): <timestamp>

## Summary
Short description of the case.

## Actors
- Entity:
- Individuals/Teams:
- Other parties:

## Timeline
List dated events with references. Create entries in `cases/<entity-id>-<short-slug>/timeline/` as `YYYY-MM-DD-<slug>.md`. (Legacy global `timeline/` is still accepted by validation.)

## Sources
- File:
  - Location:
  - SHA-256:
  - Provenance (durable link / content hash / on-chain ref):
  - Notes:

## Checksums
(Optional) Run `make checksums` to update `SHA256SUMS.txt` manifests when needed (e.g., for regulator-ready bundles).

## Redactions
If any redactions are made, include a cover note using `templates/forms/cover_note_redactions.md`.
