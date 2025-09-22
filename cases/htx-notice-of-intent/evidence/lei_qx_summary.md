# Evidence Summary: HTX <> ERG (Telegram export "Lei_qx")

- Case: htx - notice-of-intent
- Entity ID: htx
- Compiled by: Ergo Foundation
- Date (UTC, ISO 8601): 2025-09-16T15:52:28Z–2025-09-16T16:00:47Z

## Sources
- [ ] File:
  - Type (html):
  - SHA-256:
  - Provenance (durable link, content hash, or on-chain ref): Local export from Telegram (group “HTX <> ERG”)
  - Location: cases/htx-notice-of-intent/evidence/Lei_qx/messages.html
  - Notes: Visual rendering of the chat; timestamps in export denote UTC-05:00 in tooltips.

- [ ] File:
  - Type (json):
  - SHA-256:
  - Provenance (durable link, content hash, or on-chain ref): Local export from Telegram (group “HTX <> ERG”)
  - Location: cases/htx-notice-of-intent/evidence/Lei_qx/result.json
  - Notes: Structured message log with message ids (1–17) and ISO-like timestamps (local time).

- [ ] File:
  - Type (image/jpeg):
  - SHA-256:
  - Provenance (durable link, content hash, or on-chain ref): Local export from Telegram (photo attachment)
  - Location: cases/htx-notice-of-intent/evidence/Lei_qx/photos/photo_1@16-09-2025_10-59-12.jpg
  - Notes: Photo posted by “Lei_HTX Listing 🚀 @DC” at 10:59:12 (UTC-05:00).

## Observations
Key excerpts (by `result.json` ids):
- 6 (10:57:34): “Sry for the delisting issue you need to speak with our rm team”
- 7 (10:58:58): “Jon reached out for help”
- 12 (10:59:36, reply to id 7): “so you offered us to pay 100k to keep listing? wasn’t sure if that was legit”
- 13 (10:59:58): “That’s the marketing campaign proposal”
- 14 (11:00:05): “Not a service fee boss”
- 16 (11:00:25): “Please speak with Jacky about this”
- 17 (11:00:47): Service: “removed Lei_HTX Listing 🚀 @DC”

Relevance to claims in notice_of_intent.md:
- Attempted quid‑pro‑quo/paid “marketing campaign” positioned to influence listing/ST outcome (ids 12–14).
- Use of unofficial chat channel and refusal to add escalation; removal of participant (ids 6–8, 16–17).
- Context of delisting/ST contemporaneous with payment proposal discussion.

## Cross-Checks
- Firo public statement (third-party): cases/htx-notice-of-intent/evidence/firo_statement.md
  - URL: https://x.com/firoorg/status/1968007528731775485
  - Allegations: paid “marketing” to remove ST tag; delisting despite meeting requirements; forfeited deposits.
- Internal reference: cases/htx-notice-of-intent/notice_of_intent.md
  - Sections: “Attempted Bribery and Extortion”; “Support and communications failures”.
- Timeline entry: timeline/2025-09-16-htx-lei-qx-chat.md

Notes:
- For durability, consider archiving the HTML/JSON and capturing SHA‑256 via `bash scripts/finalize.sh --with-checksums --package cases/htx-notice-of-intent`, then populate the SHA‑256 fields above.
