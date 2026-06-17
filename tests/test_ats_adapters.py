"""Tests for the Remotive + ATS (Greenhouse/Lever/Ashby) adapters.

httpx.MockTransport routes per-host so one handler serves whichever API is hit.
"""

import html

import httpx

from jobagent.core.schemas import ApplyMethod, Source
from jobagent.ingestion.adapters.ashby import AshbyAdapter
from jobagent.ingestion.adapters.greenhouse import GreenhouseAdapter
from jobagent.ingestion.adapters.lever import LeverAdapter
from jobagent.ingestion.adapters.remotive import RemotiveAdapter


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_remotive_normalizes():
    feed = {"job-count": 1, "jobs": [{
        "id": 7, "title": "AI Engineer", "company_name": "Globex",
        "candidate_required_location": "Worldwide", "salary": "$120k-$150k",
        "description": "<p>Build models</p>", "url": "https://remotive.com/x",
        "publication_date": "2026-01-15T10:00:00", "tags": ["ai", "python"],
    }]}
    adapter = RemotiveAdapter(client=_client(lambda r: httpx.Response(200, json=feed)))
    jobs = list(adapter.fetch())
    assert len(jobs) == 1
    j = jobs[0]
    assert j.source == Source.remotive.value
    assert j.title == "AI Engineer"
    assert j.description == "Build models"
    assert j.salary_text == "$120k-$150k"
    assert j.posted_at is not None


def test_greenhouse_unescapes_and_marks_ats_form():
    content = html.escape("<p>Join <b>us</b></p>")  # GH double-encodes content
    feed = {"jobs": [{
        "id": 55, "title": "Backend Engineer", "location": {"name": "Remote - US"},
        "content": content, "absolute_url": "https://boards.greenhouse.io/acme/55",
        "updated_at": "2026-02-01T00:00:00Z",
    }]}
    adapter = GreenhouseAdapter(["acme"], client=_client(lambda r: httpx.Response(200, json=feed)))
    jobs = list(adapter.fetch())
    assert len(jobs) == 1
    j = jobs[0]
    assert j.company == "acme"
    assert j.is_remote is True               # "remote" in location
    assert j.apply_method == ApplyMethod.ats_form.value
    assert j.description == "Join us"        # unescaped + stripped


def test_greenhouse_skips_bad_slug_keeps_good():
    good = {"jobs": [{"id": 1, "title": "Eng", "location": {"name": "NYC"},
                      "content": "x", "absolute_url": "u"}]}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=good) if "good" in request.url.path else httpx.Response(404)

    adapter = GreenhouseAdapter(["bad", "good"], client=_client(handler))
    jobs = list(adapter.fetch())
    assert len(jobs) == 1  # bad slug skipped, good slug yielded


def test_lever_parses_ms_epoch_and_categories():
    postings = [{
        "id": "abc", "text": "Staff Engineer",
        "categories": {"location": "Remote", "team": "Platform", "commitment": "Full-time"},
        "descriptionPlain": "Do platform things.", "hostedUrl": "https://jobs.lever.co/x/abc",
        "applyUrl": "https://jobs.lever.co/x/abc/apply", "createdAt": 1_700_000_000_000,
    }]
    adapter = LeverAdapter(["netflix"], client=_client(lambda r: httpx.Response(200, json=postings)))
    jobs = list(adapter.fetch())
    j = jobs[0]
    assert j.title == "Staff Engineer"
    assert j.is_remote is True
    assert j.apply_url.endswith("/apply")
    assert j.posted_at is not None
    assert "Platform" in j.tags


def test_ashby_uses_isremote_flag():
    feed = {"jobs": [{
        "id": "z1", "title": "ML Engineer", "location": "San Francisco", "isRemote": True,
        "employmentType": "FullTime", "descriptionPlain": "Train models.",
        "applyUrl": "https://jobs.ashbyhq.com/ramp/z1", "jobUrl": "https://jobs.ashbyhq.com/ramp/z1",
        "publishedAt": "2026-03-01T12:00:00Z",
        "compensation": {"compensationTierSummary": "$180K – $220K"},
    }]}
    adapter = AshbyAdapter(["ramp"], client=_client(lambda r: httpx.Response(200, json=feed)))
    j = list(adapter.fetch())[0]
    assert j.is_remote is True
    assert j.salary_text == "$180K – $220K"
    assert j.apply_method == ApplyMethod.ats_form.value


def test_ats_adapters_disabled_without_slugs():
    assert GreenhouseAdapter([]).enabled is False
    assert LeverAdapter([]).enabled is False
    assert AshbyAdapter([]).enabled is False
