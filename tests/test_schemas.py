"""Phase 0 smoke tests: schemas validate, dedup is stable, store round-trips."""

from jobagent.core.schemas import (
    ApplicationStatus,
    JobPosting,
    Match,
    Source,
)
from jobagent.store import Store


def test_dedup_hash_stable_and_source_independent():
    a = JobPosting(source=Source.remoteok, title="AI Engineer", company="Acme", location="Remote")
    b = JobPosting(source=Source.telegram, title="ai  engineer", company="ACME", location="remote")
    # Same role from two sources collapses to one logical job.
    assert a.dedup_hash() == b.dedup_hash()

    c = JobPosting(source=Source.remoteok, title="Backend Engineer", company="Acme")
    assert a.dedup_hash() != c.dedup_hash()


def test_store_roundtrip(tmp_path):
    store = Store(str(tmp_path / "t.db"))
    store.init_schema()

    job = JobPosting(
        source=Source.remotive, title="ML Engineer", company="Globex", is_remote=True
    )
    assert store.is_new_job(job) is True
    job_id = store.upsert_job(job)
    assert store.is_new_job(job) is False

    store.upsert_match(Match(job_id=job_id, score=0.87, rationale="strong fit"))
    top = store.get_top_matches(limit=5, min_score=0.5)
    assert len(top) == 1
    assert top[0]["title"] == "ML Engineer"
    assert top[0]["score"] == 0.87
    store.close()


def test_application_status_enum():
    assert ApplicationStatus.awaiting_approval.value == "awaiting_approval"
