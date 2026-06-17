"""Telegram channel reader (Telethon / MTProto — logs in as YOUR user account).

This is NOT the bot you talk to (that's bot/, Bot API). This reads job-posting
channels you follow. Telethon is an optional dep ([telegram] extra) and is imported
lazily inside fetch(), so this module — and the pure `parse_message` parser — import
fine without it. First-run login is interactive: see scripts/telegram_login.py.

Channel messages are freeform text, so parsing is heuristic: we keep messages that
look like postings (have an apply link/email or job keywords) and let Phase 2
matching do relevance filtering. Full message text is preserved in `raw`/description.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime

from jobagent.core.schemas import ApplyMethod, JobPosting, Source
from jobagent.ingestion.base import BaseAdapter

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_JOB_KEYWORDS = (
    "hiring", "apply", "position", "vacancy", "job opening", "we're looking",
    "we are looking", "role", "remote", "engineer", "developer", "full-time",
    "full time", "contract", "salary", "responsibilities", "requirements",
)


def _channel_username(channel: str) -> str | None:
    c = (channel or "").strip()
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if c.startswith(prefix):
            c = c[len(prefix):]
            break
    c = c.lstrip("@").split("/")[0]
    return c or None


def parse_message(
    text: str | None,
    channel: str,
    msg_id: int | None = None,
    date: datetime | None = None,
) -> JobPosting | None:
    """Turn one channel message into a JobPosting, or None if it's not a posting."""
    text = (text or "").strip()
    if not text:
        return None

    emails = _EMAIL_RE.findall(text)
    urls = _URL_RE.findall(text)
    lower = text.lower()
    looks_like_job = bool(emails or urls) or any(k in lower for k in _JOB_KEYWORDS)
    if not looks_like_job:
        return None

    title = next((ln.strip() for ln in text.splitlines() if ln.strip()), "(untitled)")
    title = title[:140]

    apply_email = emails[0] if emails else None
    apply_url = urls[0] if urls else None
    if apply_email:
        apply_method = ApplyMethod.email
    elif apply_url:
        apply_method = ApplyMethod.external_link
    else:
        apply_method = ApplyMethod.unknown

    username = _channel_username(channel)
    msg_url = (
        f"https://t.me/{username}/{msg_id}"
        if username and msg_id and not username.isdigit()
        else None
    )

    return JobPosting(
        source=Source.telegram,
        source_job_id=f"{username or channel}:{msg_id}" if msg_id else None,
        title=title,
        location="Remote" if "remote" in lower else None,
        is_remote="remote" in lower,
        description=text,
        apply_method=apply_method,
        apply_url=apply_url,
        apply_email=apply_email,
        url=msg_url or apply_url,
        posted_at=date,
        raw={"channel": channel, "msg_id": msg_id, "text": text},
    )


class TelegramAdapter(BaseAdapter):
    source = Source.telegram

    def __init__(
        self,
        api_id: int | None,
        api_hash: str,
        channels: list[str],
        session: str = "data/telegram",
        limit: int = 50,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.channels = channels
        self.session = session
        self.limit = limit

    @property
    def enabled(self) -> bool:
        return bool(self.api_id and self.api_hash and self.channels)

    def fetch(self) -> Iterable[JobPosting]:
        # Lazy import: telethon is an optional extra, only needed at run time.
        from telethon.sync import TelegramClient  # type: ignore

        with TelegramClient(self.session, self.api_id, self.api_hash) as client:
            for channel in self.channels:
                try:
                    messages = client.get_messages(channel, limit=self.limit)
                except Exception:  # noqa: BLE001 — one bad channel must not kill the rest
                    continue
                for msg in messages:
                    job = parse_message(
                        getattr(msg, "message", None) or getattr(msg, "text", None),
                        channel,
                        getattr(msg, "id", None),
                        getattr(msg, "date", None),
                    )
                    if job:
                        yield job
