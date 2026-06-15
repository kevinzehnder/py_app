"""Routes for the server-rendered frontend.

Pages render without auth (open demo). To protect a page later, add the
existing auth dependency, e.g.:

    from app.auth.dependencies import CurrentUser

    @router.get("/")
    def dashboard(request: Request, user: CurrentUser) -> HTMLResponse:
        ...

Note: the existing auth is JWT-in-header (API style). Server-rendered pages
would need a cookie session to use it — out of scope here.
"""

import datetime
from pathlib import Path

import fastapi
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings

WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = fastapi.APIRouter(prefix="/web", tags=["web"])


def _base_context() -> dict:
    """Context shared by every page (app name, current year)."""
    return {
        "app_name": get_settings().APP_NAME,
        "year": datetime.date.today().year,
    }


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        _base_context(),
    )
