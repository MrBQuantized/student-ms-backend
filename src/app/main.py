from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from routers import api, pages

from .database import Base, engine, get_db
from .models import Course, Department, Student

# ===============================
# CONFIGURATIONS
# ===============================

# --- Absolute paths — always correct no matter where uvicorn runs from ---
BASE_DIR = Path(__file__).resolve().parents[1]
MEDIA = BASE_DIR / "media"
STATIC = BASE_DIR / "static"
SWAGGER_UI = STATIC / "swagger-ui-bundle"
TEMPLATES = BASE_DIR / "templates"


# --- Instantiate all tables using the async contextmanager ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# --- Cache-Busting + No-Cache Headers ---
class NoCacheStaticFiles(StaticFiles):
    """Static files that tell the browser never to cache them (dev only)"""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


# --- Instantiate FastAPI with lifespan (Disable CDN-based /docs)---
app = FastAPI(
    title="Student Management System API",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Static files (CSS, JS, Images) ---
app.mount("/static", NoCacheStaticFiles(directory=STATIC), name="static")

# --- Media files (uploads) ---
app.mount("/media", NoCacheStaticFiles(directory=MEDIA), name="media")

# --- Jinja2 Templates ---
templates = Jinja2Templates(directory=TEMPLATES)

# --- Register routers ---
app.include_router(api.router, prefix="/api")
app.include_router(pages.router, prefix="/pages")


# ===============================
# EXCEPTION HANDLING
# ===============================


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again"
    )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.,",
        },
    )
