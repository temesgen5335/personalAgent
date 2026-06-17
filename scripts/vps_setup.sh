#!/usr/bin/env bash
# Provision the VPS: install Hermes Agent, point it at OpenRouter, run as a daemon.
# Run ON THE VPS, not locally. Idempotent-ish; re-running re-checks each step.
set -euo pipefail

echo "==> Installing Hermes Agent (NousResearch)"
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

echo "==> Configure LLM provider interactively (choose OpenRouter, paste OPENROUTER_API_KEY)"
hermes setup

echo "==> Register Hermes as a systemd daemon for autonomous/scheduled operation"
hermes gateway install

cat <<'NOTE'

Next steps (manual, once Hermes is up):
  1. Clone this repo onto the VPS and install:  uv pip install -e ".[telegram,mcp,apply,llm]"
  2. Copy .env.example -> .env and fill credentials (OpenRouter, Telegram x2, SerpApi, SMTP).
  3. python scripts/init_db.py
  4. First-run Telethon login (creates the .session file) — Phase 1.
  5. Register the MCP tool servers with Hermes and add cron entries for ingestion — Phase 1/2.

Hermes memory + skills live in ~/.hermes/ on this box.
NOTE
