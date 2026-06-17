"""Tests for the Telegram channel reader. Only the pure `parse_message` and the
`enabled` gate are tested — no Telethon import, no network, no credentials."""

from datetime import datetime, timezone

from jobagent.core.schemas import ApplyMethod, Source
from jobagent.ingestion.adapters.telegram import TelegramAdapter, parse_message


def test_parse_job_with_email():
    text = "Senior AI Engineer\nRemote, full-time.\nApply: jobs@acme.example"
    job = parse_message(text, "@ai_jobs", msg_id=42, date=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert job is not None
    assert job.source == Source.telegram.value
    assert job.title == "Senior AI Engineer"
    assert job.is_remote is True
    assert job.apply_method == ApplyMethod.email.value
    assert job.apply_email == "jobs@acme.example"
    assert job.url == "https://t.me/ai_jobs/42"  # message permalink
    assert job.source_job_id == "ai_jobs:42"
    assert job.raw["text"] == text  # full message preserved


def test_parse_job_with_url_only():
    text = "Backend Developer position. Apply here https://acme.example/careers/123"
    job = parse_message(text, "https://t.me/remote_jobs", msg_id=7)
    assert job is not None
    assert job.apply_method == ApplyMethod.external_link.value
    assert job.apply_url == "https://acme.example/careers/123"
    assert job.url == "https://t.me/remote_jobs/7"


def test_non_job_chatter_returns_none():
    assert parse_message("gm everyone 🌞", "@chat") is None
    assert parse_message("", "@chat") is None
    assert parse_message(None, "@chat") is None


def test_keyword_only_post_is_kept_even_without_link():
    job = parse_message("We are hiring a Platform Engineer. DM for details.", "@jobs", msg_id=9)
    assert job is not None
    assert job.apply_method == ApplyMethod.unknown.value


def test_title_truncated_and_first_line_used():
    long_first = "X" * 200
    job = parse_message(f"{long_first}\napply: a@b.co", "@j", msg_id=1)
    assert len(job.title) == 140


def test_enabled_requires_creds_and_channels():
    assert TelegramAdapter(None, "", [], ).enabled is False
    assert TelegramAdapter(123, "hash", []).enabled is False          # no channels
    assert TelegramAdapter(123, "hash", ["@x"]).enabled is True
