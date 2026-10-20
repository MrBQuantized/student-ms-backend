from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select

# from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import selectinload
from app import (
    Department,
    Gender,
    Student,
    StudentCreate,
    StudentPut,
    StudentResponse,
    StudentUpdate,
    get_db,
)
from app.core.security import hash_password
from routers.api.students import create_student

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES = BASE_DIR / "templates"


# --- Jinja2 templates ---
templates = Jinja2Templates(directory=TEMPLATES)


router = APIRouter()


# ==============================
# GET
# ==============================


# --- GET /students/new ---
# Display an empty form
@router.get("/new", include_in_schema=False)
async def new_student_form(
    request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):

    departments = (await db.scalars(select(Department))).all()

    return templates.TemplateResponse(
        request,
        "student_form.html",
        {
            "student": None,
            "form_action": "/students/new",
            "page_title": "Add Student",
            "departments": departments,
            "gender_options": list(Gender),
            "level_options": [100, 200, 300, 400, 500],
        },
    )


# --- GET /students ---
# Display students page.
@router.get("", include_in_schema=False, name="students")
async def list_students(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    students = (await db.scalars(select(Student))).all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={"students": students, "title": "All Students"},
    )


# --- GET student/{student_id} ---
# Display an existing student's details.
@router.get("/{student_id}", include_in_schema=False)
async def student_details(
    student_id: str, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    student = await db.scalar(select(Student).where(Student.student_id == student_id))

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return templates.TemplateResponse(
        request,
        "student_details.html",
        {
            "student": student,
        },
    )


# --- GET student/{student_id}/edit ---
# Fetch the existing student and prefill
@router.get("/{student_id}", include_in_schema=False)
async def edit_student_form(
    student_id: str, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    student = await db.scalar(select(Student).where(Student.student_id == student_id))

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return templates.TemplateResponse(
        request,
        "student_form.html",
        {
            "student": student,
            "form_action": f"/students/{student_id}/edit",
            "page_title": "Edit Student",
        },
    )


# ==============================
# POST
# ==============================


# --- POST /students/new ---
# Process the form and create a student.
@router.get("/new", include_in_schema=False)
async def create_student_page(
    db: Annotated[AsyncSession, Depends(get_db)],
    first_name: str = Form(...),
    middle_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    department_id: str = Form(...),
    date_of_birth: str = Form(...),
    level: int = Form(...),
    password: str = Form(...),
):
    try:
        data = await StudentCreate(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            gender=gender,
            department_id=department_id,
            level=level,
            password=hash_password,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.errors()
        ) from exc

    student = create_student(data, db)

    return RedirectResponse(
        url=f"/students/{student.id}",
        status_code=303,
    )


# --- POST /students/{student_id}/edit ---
# Process the form and create a student.
@router.get("/{student_id}/edit", include_in_schema=False)
async def update_student(
    db: Annotated[AsyncSession, Depends(get_db)],
    student_id: str,
    first_name: str = Form(...),
    middle_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    gender: str = Form(...),
    department_id: str = Form(...),
    date_of_birth: str = Form(...),
    level: int = Form(...),
    password: str = Form(...),
):
    student = await db.scalar(select(Student).where(Student.student_id == student_id))

    student.first_name = (first_name,)
    student.middle_name = (middle_name,)
    student.last_name = (last_name,)
    student.email = (email,)
    student.date_of_birth = (date_of_birth,)
    student.gender = (gender,)
    student.department_id = (department_id,)
    student.level = (level,)
    student.password = (hash_password,)

    await db.commit()

    return RedirectResponse(
        url=f"/students/{student_id}",
        status_code=303,
    )


# ==============================
# PUT
# ==============================
# ==============================
# DELETE
# ==============================
