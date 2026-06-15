"""Server-rendered routes for the Kaufvertrag pipeline.

Multi-step flow: upload source docs -> ingest (document_reader) -> LLM extract ->
human validates/edits -> render ODT/PDF. State is filesystem-backed (``app.pipeline``).
HTMX drives partial swaps; pi-tools/pydantic-ai are imported lazily in the service
layer so failures surface as friendly partials instead of import errors.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import fastapi
import yaml
from fastapi import File, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.pipeline import jobs, service
from app.web.router import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = fastapi.APIRouter(prefix="/web/pipeline", tags=["pipeline"])

# Field names exposed as native inputs in the "Form" editor tab (dotted paths,
# prefixed ``kv.`` in the HTML). Everything else is edited via the YAML tab.
PRIMARY_FIELDS = (
    "urkundsperson.name",
    "urkundsperson.kanon",
    "ort",
    "datum",
    "protokoll_nr",
    "verkaeufer.typ",
    "verkaeufer.einzel.vorname",
    "verkaeufer.einzel.name",
    "kaeufer.typ",
    "kaeufer.einzel.vorname",
    "kaeufer.einzel.name",
    "kaufobjekt.gemeinde",
    "kaufobjekt.grundstueck_nr",
    "kaufobjekt.egrid",
    "kaufobjekt.lage",
    "kaufobjekt.flaeche",
    "kaufpreis.betrag",
    "kaufpreis.betrag_ausgeschrieben",
)


def _set_dotted(target: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = target
    for part in parts[:-1]:
        nxt = node.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            node[part] = nxt
        node = nxt
    node[parts[-1]] = value


# ── list / create ────────────────────────────────────────────────────────────


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "pipeline/index.html", {"jobs": jobs.list_jobs()}
    )


@router.post("/", response_class=HTMLResponse)
async def create(request: Request, files: Annotated[list[UploadFile], File()]) -> HTMLResponse:
    job = jobs.create_job()
    for upload in files:
        if not upload.filename:
            continue
        jobs.add_source_file(job, upload.filename, await upload.read())
    jobs.save_job(job)

    # Ingest + extract eagerly; record any failure on the job for the detail view.
    try:
        await service.ingest(job)
        await service.extract(job)
    except Exception as exc:  # noqa: BLE001 — surfaced in the UI
        job.error = str(exc)
        jobs.save_job(job)

    response = HTMLResponse(status_code=204)
    response.headers["HX-Redirect"] = f"/web/pipeline/{job.id}"
    return response


# ── detail ───────────────────────────────────────────────────────────────────


def _detail_context(job: jobs.Job) -> dict[str, Any]:
    return {
        "job": job,
        "data_yaml": yaml.safe_dump(job.data.model_dump(), allow_unicode=True, sort_keys=False),
        "primary_fields": PRIMARY_FIELDS,
        "party_types": ["", "eheleute", "erben", "ag", "einzel"],
    }


@router.get("/{job_id}", response_class=HTMLResponse)
def detail(request: Request, job_id: str) -> HTMLResponse:
    job = _load(job_id)
    return templates.TemplateResponse(request, "pipeline/detail.html", _detail_context(job))


@router.post("/{job_id}/extract", response_class=HTMLResponse)
async def extract(request: Request, job_id: str) -> HTMLResponse:
    job = _load(job_id)
    try:
        await service.extract(job)
        job.error = ""
    except Exception as exc:  # noqa: BLE001
        job.error = str(exc)
        jobs.save_job(job)
    return templates.TemplateResponse(request, "pipeline/_editor.html", _detail_context(job))


@router.post("/{job_id}/validate", response_class=HTMLResponse)
async def validate(request: Request, job_id: str) -> HTMLResponse:
    job = _load(job_id)
    form = await request.form()
    mode = form.get("editor_mode", "form")
    context: dict[str, Any] = {}

    try:
        if mode == "yaml":
            raw = str(form.get("raw_yaml", ""))
            parsed = yaml.safe_load(raw) or {}
            if not isinstance(parsed, dict):
                raise ValueError("YAML must be a mapping at the top level.")
            data_dict = parsed
        else:
            data_dict = job.data.model_dump()
            for key, value in form.items():
                if key.startswith("kv."):
                    _set_dotted(data_dict, key[3:], value)

        from app.ai.kaufvertrag import KaufvertragData

        job.data = KaufvertragData.model_validate(data_dict)
        job.status = "validated"
        job.error = ""
        jobs.save_job(job)
        context["validated"] = True
    except Exception as exc:  # noqa: BLE001 — pydantic/yaml errors shown inline
        context["validation_error"] = str(exc)

    return templates.TemplateResponse(
        request, "pipeline/_editor.html", {**_detail_context(job), **context}
    )


# ── GBA / render / download ──────────────────────────────────────────────────


@router.post("/{job_id}/gba", response_class=HTMLResponse)
async def gba(request: Request, job_id: str) -> HTMLResponse:
    job = _load(job_id)
    form = await request.form()
    gemeinde = str(form.get("gemeinde", "")).strip()
    nummer = str(form.get("nummer", "")).strip()
    context: dict[str, Any] = {"job": job}
    if not gemeinde or not nummer:
        context["gba_error"] = "Gemeinde and Nummer are required."
    else:
        try:
            await service.fetch_gba(job, gemeinde, nummer)
        except Exception as exc:  # noqa: BLE001
            context["gba_error"] = str(exc)
    return templates.TemplateResponse(request, "pipeline/_gba.html", context)


@router.post("/{job_id}/render", response_class=HTMLResponse)
async def render(request: Request, job_id: str, to: str = "pdf") -> HTMLResponse:
    job = _load(job_id)
    context: dict[str, Any] = {"job": job}
    try:
        await service.render_output(job, to)
    except Exception as exc:  # noqa: BLE001
        context["render_error"] = str(exc)
    return templates.TemplateResponse(request, "pipeline/_outputs.html", context)


@router.get("/{job_id}/download/{artifact}")
def download(job_id: str, artifact: str) -> FileResponse:
    _load(job_id)  # existence check
    safe = Path(artifact).name
    path = jobs.artifact_path(job_id, safe)
    if not path.exists():
        raise fastapi.HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path, filename=safe)


# ── helpers ──────────────────────────────────────────────────────────────────


def _load(job_id: str) -> jobs.Job:
    try:
        return jobs.get_job(job_id)
    except FileNotFoundError as exc:
        raise fastapi.HTTPException(status_code=404, detail="Job not found") from exc
