"""One-time interactive Telethon login. Creates the .session file so the
ingestion adapter can read channels non-interactively afterwards.

Run on the machine that will do the ingesting (your VPS), interactively:
    python scripts/telegram_login.py

Requires the [telegram] extra:  uv pip install -e ".[telegram]"
Needs TELEGRAM_API_ID / TELEGRAM_API_HASH / TELEGRAM_PHONE in .env.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from jobagent.config import get_settings  # noqa: E402


def main() -> None:
    s = get_settings()
    if not (s.telegram_api_id and s.telegram_api_hash):
        sys.exit("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env first (my.telegram.org).")

    from telethon.sync import TelegramClient  # noqa: E402

    Path(s.telegram_session).parent.mkdir(parents=True, exist_ok=True)
    with TelegramClient(s.telegram_session, s.telegram_api_id, s.telegram_api_hash) as client:
        # .start() prompts for the login code (and 2FA password if set).
        client.start(phone=s.telegram_phone or None)
        me = client.get_me()
        print(f"Logged in as {me.username or me.first_name}. Session saved at {s.telegram_session}.session")


if __name__ == "__main__":
    main()
