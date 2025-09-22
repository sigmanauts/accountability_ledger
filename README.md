# ⚖️ Accountability Ledger

Open, neutral, and simple. This repo helps projects publish market‑conduct evidence in public, build a timeline anyone can review, and (optionally) assemble a MAS‑ready package.

## TL;DR (60‑second tour)

- 🧾 Evidence goes in `cases/{entity}-{slug}/` (plus a short case README).
- 🗓️ Each event gets a Markdown timeline entry: `cases/{entity}-{slug}/timeline/YYYY-MM-DD-{slug}.md` (canonical) with YAML front matter (date, actors, claims, references). Legacy `timeline/` at repo root is still validated for back-compat.
- 🧰 Two scripts do the heavy lifting:
  - `scripts/new_case.sh` scaffolds a case + timeline from flags or a tiny config file.
  - `scripts/finalize.sh` runs basic validation and can (optionally) package a submission.
- 🔒 Integrity is optional: for regulators, packaging can include a manifest inside the zip. Everyday contributions don’t need checksums.

---

## Quick start

1) Copy and edit the example config
```bash
cp scripts/case.config.example scripts/case.config
# edit values in scripts/case.config
```

2) Create a case and timeline
```bash
bash scripts/new_case.sh -c scripts/case.config
# or use flags:
# bash scripts/new_case.sh -e my-exchange -s notice-of-intent -d "2025-09-18T00:00:00Z" -a "ergo-foundation,my-exchange" -C "Main claim"
```

Alternative (Makefile):
```bash
make new-case ENTITY_ID=my-exchange SLUG=notice-of-intent
```

3) Validate (basic checks)
```bash
bash scripts/finalize.sh
```

Alternative (Makefile):
```bash
make validate
```

4) Open a Pull Request linking your Issue

Optional: package a case (e.g., for MAS)
```bash
bash scripts/finalize.sh --package cases/my-exchange-notice-of-intent
```

---

## How it works (concise)

- Evidence‑first
  - Put primary docs (PDFs, emails, exports) under a case folder: `cases/{entity}-{slug}/`.
  - Add a short case README summarising actors, claims, and sources.

- Structured timeline
  - One file per event: `cases/{entity}-{slug}/timeline/YYYY-MM-DD-{slug}.md` (canonical; legacy global `timeline/` still accepted)
  - Use YAML front matter: `date`, `actors`, `claims`, `references` (URL, file, on‑chain, or content hash).

- Reviewable workflow
  - Open an Issue with a short summary + sources.
  - Submit a PR with DCO sign‑off (`git commit -s`) and the PR checklist.
  - CI runs basic validation (naming + timeline front matter) and checks DCO.

- Optional packaging
  - `scripts/finalize.sh --package cases/{entity}-{slug}` creates `mas_package/<case>-<UTC>.zip` with a `manifest.json` for easy auditing.
  - Checksums are optional and not enforced by CI.

---

## One‑command examples

- New case from config
```bash
bash scripts/new_case.sh -c scripts/case.config
```

- New case via flags
```bash
bash scripts/new_case.sh \
  -e htx \
  -s notice-of-intent \
  -d "2025-09-18T00:00:00Z" \
  -a "ergo-foundation,htx" \
  -C "Notice of intent filed" \
  -R "file|Notice Letter|cases/htx-notice-of-intent/notice_of_intent.md"
```

- Package for MAS
```bash
bash scripts/finalize.sh --package cases/htx-notice-of-intent
```

---

## Repository layout

```
/evidence        primary documents (if not tied to a single case)
/cases           structured folders per entity/case
/cases/{entity}-{slug}/timeline per-case dated entries with YAML front matter (canonical)
/timeline        legacy global location (validated for back-compat)
/analysis        methods and summaries
/mas_package     ready-to-submit bundles
/templates       forms for affidavits, redactions, notices
/scripts         helper scripts (new_case.sh, finalize.sh, etc.)
/schemas         JSON Schemas for optional validation
```

Key scripts and Makefile targets:
- `scripts/new_case.sh` — prompts or reads config to scaffold case + timeline
- `scripts/finalize.sh` — validate; optionally package a zip for submission
- `scripts/case.config.example` — tiny editable config template
- Makefile targets:
  - `make new-case ENTITY_ID=foo SLUG=bar` — scaffolds via `scripts/new_case.py`
  - `make validate` — runs `scripts/validate_repo.py`
  - `make checksums` — runs `scripts/compute_checksums.py`
  - `make package-mas CASE=cases/foo-bar` — runs `scripts/package_mas.py`

See `scripts/README.md` for details and additional tips.

Helpful templates:
- `templates/case/README.md` — case skeleton
- `templates/forms/cover_note_redactions.md` — redactions cover note
- `templates/notice/notice_of_intent.md` — starting point for a notice letter

---

## Contribution in 3 steps

1) Open an Issue using the “Case” template (summary + sources)
2) Add materials using the scripts above (case + timeline + evidence)
3) Open a PR with DCO sign‑off and complete the checklist

Review checklist
- Files match the summary and folder conventions
- Timestamps are UTC ISO 8601
- Links resolve or references (file/hash/on‑chain) are provided
- Avoid protected personal data

---

## Principles

- Politically neutral and open: publish clear evidence and provenance so anyone can review or reuse.
- Welcome patterns: projects who faced similar extortion‑like practices are invited to contribute and document.
- Minimize trust: sunlight first; integrity tooling is optional and used mainly for regulator‑ready packages.
- Proof‑of‑Work ethos: public, verifiable history over private gatekeeping.

---

## Governance

- Issues for discussion/triage
- Pull Requests for changes
- DCO sign‑off required
- CI: basic validation + DCO check

---

## Ethics and legal

- Respect privacy law and court orders
- Avoid defamatory claims
- Use at your own risk
- Documentation and research; not legal advice

---

## License

- Code: MIT (LICENSE)
- Docs/evidence: CC BY 4.0 (LICENSE-docs)
