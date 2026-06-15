"""Pipeline orchestration — deterministic glue around pi-tools.

Each step is async; the blocking pi-tools work (docling, AGOBIS, pandoc,
LibreOffice) runs in a worker thread via ``anyio.to_thread.run_sync``. pi-tools
and pydantic-ai are imported lazily so the app boots without the optional ``ai``
extra and failures surface in the UI.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from anyio.to_thread import run_sync

from app.core.config import get_settings
from app.pipeline import jobs
from app.pipeline.jobs import GbaArtifact, Job

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}


# ── ingest ───────────────────────────────────────────────────────────────────


def _read_one(src: Path, out: Path) -> None:
    """Convert one source file to Markdown at ``out`` (document_reader or copy)."""
    if src.suffix.lower() in TEXT_SUFFIXES:
        out.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        return

    from pi_tools import document_reader as dr

    method = get_settings().DOCUMENT_READER_METHOD
    if method == "vlm":
        dr.read_with_vlm(src, out)
    elif method == "llm-server":
        dr.read_with_llm_server(src, out, server_url=get_settings().LLM_SERVER_URL)
    else:
        dr.read_with_ocr(src, out)


def _ingest_sync(job: Job) -> Job:
    if not job.source_files:
        raise ValueError("Job has no source files to ingest.")

    parts: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in job.source_files:
            src = jobs.sources_dir(job.id) / name
            out = Path(tmp) / f"{name}.md"
            _read_one(src, out)
            parts.append(f"<!-- source: {name} -->\n\n{out.read_text(encoding='utf-8')}")

    combined = "\n\n---\n\n".join(parts).strip() + "\n"
    jobs.artifact_path(job.id, jobs.SOURCE_MARKDOWN).write_text(combined, encoding="utf-8")
    job.source_markdown = jobs.SOURCE_MARKDOWN
    job.status = "ingested"
    jobs.save_job(job)
    return job


async def ingest(job: Job) -> Job:
    """Read all uploaded source files into a single ``artifacts/source.md``."""
    return await run_sync(_ingest_sync, job)


# ── extract ──────────────────────────────────────────────────────────────────


async def extract(job: Job) -> Job:
    """Run the LLM extraction over the ingested Markdown into ``job.data``."""
    from app.ai.kaufvertrag import extract_kaufvertrag

    if not job.source_markdown:
        raise ValueError("Job has not been ingested yet.")
    source_md = jobs.artifact_path(job.id, job.source_markdown).read_text(encoding="utf-8")

    job.data = await extract_kaufvertrag(source_md)
    job.status = "extracted"
    jobs.save_job(job)
    return job


# ── GBA ──────────────────────────────────────────────────────────────────────


def _slug(value: str) -> str:
    cleaned = "".join(c if c.isalnum() else "_" for c in value).strip("_")
    return cleaned or "gba"


def _fetch_gba_sync(job: Job, gemeinde: str, nummer: str) -> Job:
    from pi_tools.agobis import AGOBISClient
    from pi_tools.gba_cleanup import cleanup_docx, convert_rtf_to_docx

    settings = get_settings()
    if not settings.AGOBIS_USER or not settings.AGOBIS_PASS:
        raise ValueError("AGOBIS is not configured; set AGOBIS_USER / AGOBIS_PASS")
    session_file = (
        Path(settings.AGOBIS_SESSION_FILE).expanduser() if settings.AGOBIS_SESSION_FILE else None
    )

    base = f"gba_{_slug(gemeinde)}_{_slug(nummer)}"
    rtf_name = f"{base}.rtf"
    docx_name = f"{base}.docx"
    rtf_path = jobs.artifact_path(job.id, rtf_name)
    docx_path = jobs.artifact_path(job.id, docx_name)

    with AGOBISClient(
        username=settings.AGOBIS_USER,
        password=settings.AGOBIS_PASS,
        session_file=session_file,
    ) as client:
        municipality = client.resolve_municipality(gemeinde)
        hits = client.search_hits_by_number(municipality_id=municipality.id, nummer=nummer)
        candidates = [h for h in hits if h.rtf_possible] or hits
        if not candidates:
            raise ValueError(f"No parcel found for {gemeinde} {nummer}.")
        hit = candidates[0]
        rtf_path.write_bytes(client.download_parcel_rtf(grundstueck_id=hit.grundstueck_id))

    with tempfile.TemporaryDirectory() as tmp:
        converted = convert_rtf_to_docx(rtf_path, Path(tmp))
        cleanup_docx(converted, docx_path, remove_footers=True)

    job.gba = [g for g in job.gba if not (g.gemeinde == gemeinde and g.nummer == nummer)]
    job.gba.append(
        GbaArtifact(
            gemeinde=gemeinde,
            nummer=nummer,
            grundstueck_id=hit.grundstueck_id,
            rtf=rtf_name,
            docx=docx_name,
        )
    )
    jobs.save_job(job)
    return job


async def fetch_gba(job: Job, gemeinde: str, nummer: str) -> Job:
    """Fetch + clean the Grundbuchauszug for one parcel into the job artifacts."""
    return await run_sync(_fetch_gba_sync, job, gemeinde, nummer)


# ── render ───────────────────────────────────────────────────────────────────


def _render_sync(job: Job, to: str) -> Job:
    from pi_tools.document_render import render
    from pi_tools.kaufvertrag import DEFAULT_TEMPLATE, add_frontmatter, fill_template

    data = job.data.model_dump()
    body = fill_template(DEFAULT_TEMPLATE, data)
    markdown = add_frontmatter(body, data, "contract")

    md_path = jobs.artifact_path(job.id, "contract.md")
    md_path.write_text(markdown, encoding="utf-8")

    out_name = f"contract.{to}"
    out_path = jobs.artifact_path(job.id, out_name)
    render(md_path, to=to, doc_type="contract", output=str(out_path))

    job.outputs[to] = out_name
    job.status = "rendered"
    jobs.save_job(job)
    return job


async def render_output(job: Job, to: str = "pdf") -> Job:
    """Render the contract to ODT or PDF from ``job.data``."""
    if to not in ("pdf", "odt"):
        raise ValueError("to must be 'pdf' or 'odt'")
    return await run_sync(_render_sync, job, to)
