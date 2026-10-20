from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import (
    Department,
    Student,
    StudentCreate,
    StudentPut,
    StudentResponse,
    StudentUpdate,
    get_db,
)
from app.core.security import hash_password

router = APIRouter()


# --- Generate Student ID ---
async def generate_student_id(
    department_id: int, db: Annotated[AsyncSession, Depends(get_db)]
) -> str:

    # Fetch the department to get its code
    result = await db.execute(select(Department).where(Department.id == department_id))
    dept = result.scalar_one_or_none()

    if not dept or not dept.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department not found or missing code",
        )

    year = datetime.now().year
    prefix = f"{year}-{dept.code}-"

    # Find the highest existing number for this year+dept
    result = await db.execute(
        select(func.max(Student.student_id)).where(
            Student.student_id.like(f"{prefix}%")
        )
    )

    last_serial = result.scalar_one_or_none()
    next_serial = int(last_serial.split("-")[-1]) + 1 if last_serial else 1

    return f"{prefix}{next_serial:04d}"


# ================================
# POST
# ================================
@router.post(
    "/new",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_student(
    student: StudentCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    # 1. Dump payload (student_id is no longer in it)
    student_data = student.model_dump(exclude={"password"})

    # 2. Generate the structured ID server-side
    new_student_id = await generate_student_id(student.department_id, db)

    # 3. Check for existing email

    existing_email = await db.scalar(
        select(Student).where(Student.email == student_data["email"])
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 4. Create the model instance
    new_student = Student(
        **student_data,
        student_id=new_student_id,
        hashed_password=hash_password(student.password),
    )

    # 5. Add & commit
    db.add(new_student)
    try:
        await db.commit()
    except IntegrityError:
        # Fallback: if two requests raced, retry once
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="ID collision, please retry"
        )

    await db.refresh(new_student, attribute_names=["department"])
    return new_student


# ================================
# GET
# ================================
# All Students
@router.get("", response_model=list[StudentResponse])
async def all_students(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(Student).options(selectinload(Student.department)))

    students = result.all()

    return students


@router.get(
    "/{id}",
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


# ================================
# PATCH
# ================================
@router.patch("/{id}", response_model=StudentResponse)
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


# ================================
# PUT
# ================================
@router.put("/{id}", response_model=StudentCreate)
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


# ================================
# DELETE
# ================================
# Delete Student
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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
