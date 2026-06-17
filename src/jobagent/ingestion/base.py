"""Base ingestion adapter. Every source (RemoteOK, Telegram, aggregator, ...)
subclasses this and yields normalized JobPosting objects. Nothing downstream
knows or cares which source a job came from."""

from __future__ import annotations

import abc
from collections.abc import Iterable

from jobagent.core.schemas import JobPosting, Source


class BaseAdapter(abc.ABC):
    """Contract for a job source.

    Implementations should be resilient: a single bad posting must not abort the
    whole run. Network/auth config comes from jobagent.config.get_settings().
    """

    source: Source

    @abc.abstractmethod
    def fetch(self) -> Iterable[JobPosting]:
        """Yield normalized postings. Pull-only; persistence is the caller's job."""
        raise NotImplementedError

    @property
    def enabled(self) -> bool:
        """Override to gate an adapter on required credentials being present."""
        return True
