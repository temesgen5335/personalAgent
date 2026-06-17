"""Shared adapter helpers — HTML stripping, client construction, slug parsing."""

from __future__ import annotations

import re

import httpx

_TAG_RE = re.compile(r"<[^>]+>")
USER_AGENT = "personal-job-agent/0.1 (+personal use)"


def strip_html(text: str | None) -> str:
    return _TAG_RE.sub("", text or "").strip()


def make_client(client: httpx.Client | None) -> tuple[httpx.Client, bool]:
    """Return (client, owns). If we created it, caller must close it."""
    if client is not None:
        return client, False
    return httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}), True


def split_slugs(raw: str) -> list[str]:
    """'acme, globex ,' -> ['acme', 'globex']"""
    return [s.strip() for s in (raw or "").split(",") if s.strip()]
