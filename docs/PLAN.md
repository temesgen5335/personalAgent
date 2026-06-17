# Build Plan

Each phase is independently shippable. You get real value at Phase 2 (daily ranked
digest in Telegram) before any auto-apply exists.

Decisions locked in:
- **Auto-apply**: Tier 1 (email) + Tier 2 (HITL ATS form-fill). No full auto-submit.
- **Hosting/LLM**: VPS + OpenRouter API.
- **Sources**: Telegram channels, RemoteOK, Remotive, Greenhouse/Lever/Ashby,
  aggregator for Indeed/LinkedIn/Glassdoor/JobRight, Playwright fallback.

---

## Phase 0 — Foundations ✅ (this scaffold)
- [x] Repo + git, package layout under `src/jobagent/`
- [x] Core schemas: `JobPosting`, `Match`, `Application`, `CVVariant`, `Event`
- [x] SQLite store + `schema.sql` + `init_db.py`
- [x] Config via pydantic-settings + `.env.example`
- [x] Base ingestion adapter interface
- [x] Smoke tests + hard rules (`.agent/rules.md`)
- [ ] VPS: install Hermes Agent, `hermes setup` → OpenRouter, `hermes gateway install`
      (run `scripts/vps_setup.sh` on the box)

## Phase 1 — Ingestion adapters → store
- [ ] Adapter run loop: fetch → dedup → upsert → log events
- [ ] RemoteOK adapter (free JSON) — prove the pipeline end to end
- [ ] Remotive adapter (free JSON)
- [ ] Greenhouse / Lever / Ashby adapters (config-driven company slug list)
- [ ] Telegram channel reader (Telethon, first-run login, session file)
- [ ] Aggregator adapter (SerpApi Google Jobs → Indeed/LinkedIn/Glassdoor/JobRight)
- [ ] Playwright fallback adapter (last resort, per-board)
- [ ] Wire fetch loop to Hermes cron
- **Exit:** scheduled pulls populate the store from all live sources; deduped; idempotent.

## Phase 2 — Matching + Telegram digest *(first payoff)*
- [ ] Ingest CV + preferences into a structured profile (+ Hermes memory)
- [ ] `match_score` MCP tool: embedding prefilter + LLM judge → score/rationale/gaps
- [ ] Telegram bot (Bot API): `/start`, `/preferences`, `/jobs`, `/status`, owner-locked
- [ ] Daily ranked digest + per-job match cards
- **Exit:** every morning, a ranked filtered digest arrives in Telegram.

## Phase 3 — Application assets (Tier 1)
- [ ] `cv_tailor` MCP tool (reframes real experience only — R1)
- [ ] `cover_letter` + `email_draft` tools
- [ ] Bot flow: tap job → review assets → approve → send email (SMTP/Gmail)
- [ ] Log to `applications` + `events`; stamp `approved_at`
- **Exit:** apply to email-based postings end-to-end with one approval.

## Phase 4 — HITL form-fill (Tier 2)
- [ ] `apply_executor`: Playwright fill for Greenhouse/Lever/Ashby layouts
- [ ] Pause + screenshot before submit → Telegram approval → submit
- [ ] CAPTCHA / hard-block → hand back deep link (R3)
- **Exit:** one-approval assisted submission on the three ATS platforms.

## Phase 5 — Tracking dashboard
- [ ] Next.js read-only dashboard over the same store
- [ ] Funnel, status, history, source analytics
- **Exit:** web view; Telegram stays primary.

---

## Risk register
- **Telegram ToS**: Telethon user-account reading is a gray area — keep rates low,
  consider a dedicated account. (R8)
- **ATS ToS / anti-bot**: Tier 2 carries account risk; HITL + no CAPTCHA-solving. (R2, R3)
- **CV integrity**: never fabricate. (R1)
- **Aggregator cost**: SerpApi ~$50/mo; cap query volume.
