from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

from .database import Base, engine, get_db
from .models import Course, Student
from .schemas import (
    PasswordUpdate,
    StudentCreate,
    StudentPut,
    StudentResponse,
    StudentUpdate,
)

# Define paths
BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND = BASE_DIR / "frontend"
MEDIA = FRONTEND / "media"
STATIC = FRONTEND / "static"
TEMPLATES = FRONTEND / "templates"


# Instantiate all tables using the async contextmanager
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# Instantiate FastAPI with lifespan
app = FastAPI(
    title="Student Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Turn a plaintext password into a secure hashed password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Mount Static and media paths.
app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/media", StaticFiles(directory=MEDIA), name="media")

# Debug paths
print(f"[DEBUG] STATIC = {STATIC}")
print(f"[DEBUG] exists = {STATIC.exists()}")
print(f"[DEBUG] files = {list(STATIC.rglob('*')) if STATIC.exists() else 'N/A'}")

# Define the template path.
templates = Jinja2Templates(directory=TEMPLATES)


# ===============================
# TEMPLATE ROUTES
# ===============================
# --- GET ---


# --- Home ---
# @app.get("/", include_in_schema=False, name="home")
# async def home():
#     return {"message": "Welcome to the Student Management System API!"}


@app.get("/", include_in_schema=False, name="home")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"title": "Home Page"}
    )


# --- Dashboard ---
@app.get("/dashboard", include_in_schema=False, name="dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={"title": "Dashboard"}
    )


# --- Courses ---
@app.get("/courses", include_in_schema=False, name="courses")
async def courses(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    courses = await db.scalars(select(Course)).all()
    return templates.TemplateResponse(
        request=request,
        name="courses.html",
        context={"courses": courses, "title": "Available Courses"},
    )


# --- All Students ---
@app.get("/students", include_in_schema=False, name="students")
async def list_students(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    students = await db.scalars(select(Student)).all()

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={"students": students, "title": "All Students"},
    )


# --- Student ---
@app.get("/students/{id}", include_in_schema=False)
async def student_details(
    id: int, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    student = await db.scalar(select(Student.id).where(Student.id == id))

    if student:
        return templates.TemplateResponse(
            request,
            "student_detail.html",
            {
                "student": student,
                "title": f"{student.first_name} {student.last_name}'s details",
            },
        )


# --- Courses ---


# ===============================
# API ROUTES
# ===============================
# --- POST ---
@app.post(
    "/api/students/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_student(
    student: StudentCreate, db: Annotated[AsyncSession, Depends(get_db)]
):

    student_data = student.model_dump(exclude={"password"})

    # awaiting the scalar call
    existing_student = await db.scalar(
        select(Student).where(Student.id == student_data["id"])
    )
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Student already exists"
        )

    new_student = Student(
        **student_data,
        hashed_password=hash_password(student.password),
    )

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student, attribute_names=["department"])

    return new_student


# --- GET ---
# All Students
@app.get("/api/students", response_model=list[StudentResponse], name="students")
async def all_students(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(Student).options(selectinload(Student.department)))

    students = result.all()

    return students


@app.get(
    "/api/students/{id}",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def get_student(id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    student = await db.scalar(
        select(Student)
        .options(selectinload(Student.department))
        .where(Student.id == id)
    )

    # Validation
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )

    return student


# --- PATCH ---
@app.patch("/api/students/{id}", response_model=StudentResponse)
async def update_student_partial(
    id: int,
    student_data: StudentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    student = await db.scalar(
        select(Student)
        .options(selectinload(Student.department))
        .where(Student.id == id)
    )

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    update_data = student_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)

    return student


# --- PUT ---
@app.put("/api/students/{id}", response_model=StudentCreate)
async def update_student_full(
    id: int,
    student_data: StudentPut,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    student = await db.scalar(select(Student).where(Student.id == id))

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
        )

    student.first_name = student_data.first_name
    student.middle_name = student_data.middle_name
    student.last_name = student_data.last_name

    await db.commit()
    await db.refresh(student)

    return student


# Password Update
@app.patch(
    "/api/students/{student_id}/password", status_code=status.HTTP_204_NO_CONTENT
)
async def change_student_password(
    password: PasswordUpdate,
    student_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # 1. Find the student by the ID in the URL
    student = await db.scalar(select(Student).where(Student.student_id == student_id))

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
        )

    # 2. Verify the current password matches
    if not verify_password(password.current_password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # 3. Hash and store the new password
    student.hashed_password = hash_password(password.new_password)

    # 4. Persist and return nothing  (204 - No Content)
    await db.commit()


# --- DELETE ---
# Delete Student
@app.delete("/api/students/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(select(Student).where(Student.id == id))

    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    await db.delete(student)
    await db.commit()


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
