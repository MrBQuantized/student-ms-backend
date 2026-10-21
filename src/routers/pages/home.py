from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# from sqlalchemy.exc import IntegrityError

# from sqlalchemy.orm import selectinload

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES = BASE_DIR / "templates"


# --- Jinja2 templates ---
templates = Jinja2Templates(directory=TEMPLATES)


router = APIRouter()


@router.get("/", include_in_schema=False)
@router.get("", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "title": "Home Page",
        },
    )
