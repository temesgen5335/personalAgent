# Agent Rules — non-negotiables for the Personal Job Agent

These are hard constraints. Treat them like the architecture rules they are.

## Safety & integrity
- **R1 — Never fabricate CV content.** Tailoring reframes, reorders, and emphasizes
  *real* experience to a job description. It never invents skills, titles, dates,
  or employers. Every CVVariant traces to `base_cv_id`.
- **R2 — No submission without explicit per-job approval.** `applications.approved_at`
  is set ONLY by an explicit user approval action in Telegram. Tier 1 (email) and
  Tier 2 (ATS form-fill) both stop at the HITL gate and show the user exactly what
  will be sent before sending. No full auto-submit in v1.
- **R3 — Don't fight anti-bot defenses.** On CAPTCHA / hard block, hand the user a
  deep link and mark the application for manual completion. Never solve CAPTCHAs.

## Data
- **R4 — Never discard source data.** Every adapter stores the full source payload
  in `JobPosting.raw`. Normalized fields are additive, not lossy.
- **R5 — Dedup by logical identity.** Same role from multiple sources collapses to
  one `dedup_hash` (company+title+location). Sources annotate; they don't duplicate.
- **R6 — Store is the SSoT.** All runtime state lives in the store. The future
  dashboard and the bot read the same tables.

## Sources
- **R7 — APIs over scraping.** Prefer official/public APIs (RemoteOK, Remotive,
  Greenhouse/Lever/Ashby). Use the aggregator (SerpApi/Apify) for
  Indeed/LinkedIn/Glassdoor/JobRight. Direct Playwright scraping is last resort only.
- **R8 — Conservative request rates.** Especially Telethon (your user account) and
  any scraping. Rate-limit and back off; a banned account is a dead source.

## Secrets
- **R9 — Secrets only in `.env` / environment.** Never commit credentials. Telethon
  `.session` files are gitignored and never leave the VPS.

## Process
- **R10 — Never `git commit` without explicit user approval.** Surface the draft
  message and changed files; wait.
