"""Filesystem-backed job store for the Kaufvertrag pipeline.

Layout (root from ``settings.PIPELINE_DATA_DIR``)::

    {root}/{job_id}/
        sources/        uploaded source documents
        artifacts/      source.md, gba_*.rtf/.docx, contract.md, contract.pdf/.odt
        job.json        serialized Job state

A job carries its own ``KaufvertragData`` so the validate/edit step round-trips
through it. Everything is plain JSON + files — no database.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.ai.kaufvertrag import KaufvertragData
from app.core.config import get_settings

JobStatus = Literal["created", "ingested", "extracted", "validated", "rendered"]


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)

JOB_FILE = "job.json"
SOURCES_DIR = "sources"
ARTIFACTS_DIR = "artifacts"
SOURCE_MARKDOWN = "source.md"


class GbaArtifact(BaseModel):
    """A fetched + cleaned Grundbuchauszug for one parcel."""

    gemeinde: str = ""
    nummer: str = ""
    grundstueck_id: str = ""
    rtf: str = ""  # filename under artifacts/
    docx: str = ""  # cleaned DOCX filename under artifacts/


class Job(BaseModel):
    """One pipeline run."""

    id: str
    status: JobStatus = "created"
    created_at: datetime.datetime = Field(default_factory=_now)
    source_files: list[str] = Field(default_factory=list)
    source_markdown: str = ""  # artifacts-relative filename once ingested
    data: KaufvertragData = Field(default_factory=KaufvertragData)
    gba: list[GbaArtifact] = Field(default_factory=list)
    outputs: dict[str, str] = Field(default_factory=dict)  # fmt -> artifacts-relative filename
    error: str = ""  # last step error, surfaced in the UI


# ── paths ────────────────────────────────────────────────────────────────────


def jobs_root() -> Path:
    root = Path(get_settings().PIPELINE_DATA_DIR).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    return root


def job_dir(job_id: str) -> Path:
    return jobs_root() / job_id


def sources_dir(job_id: str) -> Path:
    return job_dir(job_id) / SOURCES_DIR


def artifacts_dir(job_id: str) -> Path:
    return job_dir(job_id) / ARTIFACTS_DIR


def artifact_path(job_id: str, filename: str) -> Path:
    return artifacts_dir(job_id) / filename


# ── store ────────────────────────────────────────────────────────────────────


def create_job() -> Job:
    job = Job(id=uuid4().hex)
    sources_dir(job.id).mkdir(parents=True, exist_ok=True)
    artifacts_dir(job.id).mkdir(parents=True, exist_ok=True)
    save_job(job)
    return job


def save_job(job: Job) -> None:
    (job_dir(job.id)).mkdir(parents=True, exist_ok=True)
    (job_dir(job.id) / JOB_FILE).write_text(
        job.model_dump_json(indent=2), encoding="utf-8"
    )


def get_job(job_id: str) -> Job:
    path = job_dir(job_id) / JOB_FILE
    if not path.exists():
        raise FileNotFoundError(f"No such job: {job_id}")
    return Job.model_validate_json(path.read_text(encoding="utf-8"))


def list_jobs() -> list[Job]:
    jobs: list[Job] = []
    for child in jobs_root().iterdir():
        if not child.is_dir():
            continue
        try:
            jobs.append(get_job(child.name))
        except (FileNotFoundError, ValueError):
            continue
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    return jobs


def add_source_file(job: Job, filename: str, content: bytes) -> Path:
    """Save an uploaded source file and record it on the job (caller saves)."""
    safe = Path(filename).name  # strip any path components
    dest = sources_dir(job.id) / safe
    dest.write_bytes(content)
    if safe not in job.source_files:
        job.source_files.append(safe)
    return dest
