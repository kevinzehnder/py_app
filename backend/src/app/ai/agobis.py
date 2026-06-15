"""AGOBIS Grundbuch integration — fetch an RTF Grundbuchauszug for a parcel.

Minimal counterpart to the hello-world task: resolve a municipality, search a
parcel by number, and download its Grundbuchauszug as RTF.

Backed by the sync ``pi_tools.agobis.AGOBISClient``, so the blocking work runs
in a worker thread. Credentials/session come from ``app.core.config`` (the
``AGOBIS_*`` settings).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from anyio.to_thread import run_sync
from pi_tools.agobis import AGOBISClient

from app.core.config import get_settings

# Test default: Neuenhof Liegenschaft 119.
DEFAULT_GEMEINDE = "Neuenhof"
DEFAULT_NUMMER = "119"


@dataclass
class RtfResult:
    """Downloaded Grundbuchauszug plus a little context for the UI/filename."""

    filename: str
    content: bytes
    grundstueck_id: str
    gemeinde: str
    nummer: str | None


def _fetch_sync(gemeinde: str, nummer: str) -> RtfResult:
    settings = get_settings()
    if not settings.AGOBIS_USER or not settings.AGOBIS_PASS:
        raise ValueError("AGOBIS is not configured; set AGOBIS_USER / AGOBIS_PASS")

    session_file = (
        Path(settings.AGOBIS_SESSION_FILE).expanduser()
        if settings.AGOBIS_SESSION_FILE
        else None
    )

    with AGOBISClient(
        username=settings.AGOBIS_USER,
        password=settings.AGOBIS_PASS,
        session_file=session_file,
    ) as client:
        municipality = client.resolve_municipality(gemeinde)
        hits = client.search_hits_by_number(municipality_id=municipality.id, nummer=nummer)
        # Prefer parcels that actually allow RTF export; fall back to any hit.
        candidates = [hit for hit in hits if hit.rtf_possible] or hits
        if not candidates:
            raise ValueError(f"No parcel found for {gemeinde} {nummer}.")

        hit = candidates[0]
        content = client.download_parcel_rtf(grundstueck_id=hit.grundstueck_id)
        return RtfResult(
            filename=f"grundbuchauszug_{gemeinde}_{nummer}.rtf",
            content=content,
            grundstueck_id=hit.grundstueck_id,
            gemeinde=municipality.name,
            nummer=hit.nummer,
        )


async def fetch_grundstueck_rtf(
    gemeinde: str = DEFAULT_GEMEINDE,
    nummer: str = DEFAULT_NUMMER,
) -> RtfResult:
    """Fetch the RTF Grundbuchauszug for a parcel (defaults to Neuenhof 119)."""
    return await run_sync(_fetch_sync, gemeinde, nummer)
