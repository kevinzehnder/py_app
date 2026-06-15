"""Pipeline job store + web route tests (no LLM / network)."""

from __future__ import annotations

import pytest


@pytest.fixture
def tmp_jobs(tmp_path, monkeypatch):
    """Point the job store at a temp dir for the duration of a test."""
    from app.pipeline import jobs

    monkeypatch.setattr(jobs, "jobs_root", lambda: tmp_path)
    return jobs


def test_job_store_roundtrip(tmp_jobs) -> None:
    job = tmp_jobs.create_job()
    tmp_jobs.add_source_file(job, "note.txt", b"hello")
    job.data.kaufobjekt.gemeinde = "Neuenhof"
    tmp_jobs.save_job(job)

    again = tmp_jobs.get_job(job.id)
    assert again.data.kaufobjekt.gemeinde == "Neuenhof"
    assert again.source_files == ["note.txt"]
    assert any(j.id == job.id for j in tmp_jobs.list_jobs())


def test_pipeline_index_page(client) -> None:
    response = client.get("/web/pipeline/")
    assert response.status_code == 200
    assert "Kaufvertrag Pipeline" in response.text


def test_validate_yaml_mode_updates_data(client, tmp_jobs) -> None:
    job = tmp_jobs.create_job()
    yaml_text = "kaufobjekt:\n  gemeinde: Neuenhof\n  grundstueck_nr: '119'\n"

    response = client.post(
        f"/web/pipeline/{job.id}/validate",
        data={"editor_mode": "yaml", "raw_yaml": yaml_text},
    )
    assert response.status_code == 200

    saved = tmp_jobs.get_job(job.id)
    assert saved.data.kaufobjekt.gemeinde == "Neuenhof"
    assert saved.data.kaufobjekt.grundstueck_nr == "119"
    assert saved.status == "validated"


def test_validate_form_mode_overlays_primary_fields(client, tmp_jobs) -> None:
    job = tmp_jobs.create_job()

    response = client.post(
        f"/web/pipeline/{job.id}/validate",
        data={
            "editor_mode": "form",
            "kv.kaufpreis.betrag": "500000",
            "kv.verkaeufer.typ": "einzel",
            "kv.verkaeufer.einzel.name": "Muster",
        },
    )
    assert response.status_code == 200

    saved = tmp_jobs.get_job(job.id)
    assert saved.data.kaufpreis.betrag == "500000"
    assert saved.data.verkaeufer.typ == "einzel"
    assert saved.data.verkaeufer.einzel.name == "Muster"
