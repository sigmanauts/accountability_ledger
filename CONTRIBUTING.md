# Contributing Guide

Thank you for contributing to Accountability Ledger. This repository is designed as an audit-friendly evidence ledger.

## Scope and Standards

- Source files: PDF or plain text (txt, md, eml, msg, csv, json).
- Checksums: Optional; generated during packaging via `scripts/finalize.sh --with-checksums` when a regulator-ready bundle is needed.
- Timestamps: UTC in ISO 8601 format (e.g., 2025-09-18T11:45:00Z).
- Entity IDs: lowercase, hyphenated, pattern: `[a-z0-9-]+`.
- Timeline filenames: `timeline/YYYY-MM-DD-{slug}.md` (slug: `[a-z0-9-]+`).

## Submission Workflow

1. Open an Issue using the “Case” template with a short summary and list of sources.
2. Create a case via `scripts/new_case.sh` using a config file or flags.
   - Config: `cp scripts/case.config.example scripts/case.config` (edit values)
   - Run: `bash scripts/new_case.sh -c scripts/case.config`
3. Run basic validation:
   - `bash scripts/finalize.sh`
4. Open a Pull Request linking the issue.
5. Optional: prepare a regulator-ready package (and checksums if needed):
   - `bash scripts/finalize.sh --package cases/{entity-id}-{slug}`
   - add `--with-checksums` to write `SHA256SUMS.txt` before packaging

## Redactions

- If redactions are necessary, include a cover note (use `templates/forms/cover_note_redactions.md`).
- Redacted files should use a `-redacted` suffix in the filename.
- Do not include unredacted sensitive content in the repository.

## Developer Certificate of Origin (DCO)

All commits must be signed off.

- Add this line to each commit message:

  Signed-off-by: Your Name <you@example.com>

- Or use Git’s flag:

  git commit -s -m "Your message"

PRs without “Signed-off-by:” in commits may be rejected.

## Naming Rules

- Case folder: `cases/{entity-id}-{short-slug}` (e.g., `cases/acme-exchange-withdrawal-halt`)
- Timeline entry: `timeline/YYYY-MM-DD-{slug}.md`
- Avoid spaces, uppercase, and special characters.

## Checksums

- The repository maintains per-directory manifests named `SHA256SUMS.txt`.
- Use `make checksums` to (re)generate manifests after adding or changing files.
- Use `make validate` to verify manifests and other standards before opening a PR.
- You can also compute a hash directly: `sha256sum` (Linux) or `shasum -a 256` (macOS).

Why checksums beyond Git?
- Out-of-band verification: Auditors or regulators can verify file integrity without Git tooling—compare a file’s SHA-256 against `SHA256SUMS.txt`.
- Stable across transports: Zips/emails/copies preserve the hash; recipients can confirm they received the exact bytes referenced in summaries or affidavits.
- LFS-aware: With Git LFS, Git stores pointers; our manifests record hashes for the actual binary evidence users handle.
- Chain-of-custody: Hashes provide objective fingerprints tying claims to specific file bytes, surfacing silent re-exports/metadata changes.

Format per line:

```
<sha256>  <relative_filename>
```

Manual verification examples:
- macOS: `shasum -a 256 path/to/file.pdf`
- Linux: `sha256sum path/to/file.pdf`
Compare the output to the corresponding entry in `SHA256SUMS.txt` within that file’s directory.

## Detailed local workflow

1) Create a case:
- `make new-case ENTITY_ID=my-exchange SLUG=withdrawal-halts`

2) Add materials:
- Put files under `cases/my-exchange-withdrawal-halts/` (or `evidence/` if generic).
- Add a timeline entry `timeline/YYYY-MM-DD-withdrawal-halts.md` with YAML front matter (date, actors, claims, references).

3) Compute/verify checksums:
- `make checksums`  (updates or creates `SHA256SUMS.txt` per directory)

4) Validate repository:
- `make validate`  (naming rules, timeline front matter, checksum manifests)

5) Open a PR:
- Link the Issue, include DCO sign-off (`git commit -s`), complete the PR checklist.

6) Package for MAS (optional/on request):
- `make package-mas CASE=cases/my-exchange-withdrawal-halts`  (creates `mas_package/<case>-<UTC>.zip` with `manifest.json`)

## Licensing

- Code: MIT (see LICENSE)
- Documentation and files: CC BY 4.0 (see LICENSE-docs)

## Communication

- Use GitHub Issues for discussion and triage.
- Tag maintainers on urgent matters.
