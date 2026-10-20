from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import (
    Course,
    CourseCreate,
    CourseResponse,
    get_db,
)

router = APIRouter()

# ================================
# POST
# ================================


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate, db: Annotated[AsyncSession, Depends(get_db)]
):

    course_data = course.model_dump()

    # Awaiting the Scalar call
    existing_course = await db.scalar(
        select(Course).where(Course.code == course_data["code"])
    )

    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course already exists",
        )

    new_course = Course(**course_data)

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course, attribute_names=["department"])

    return new_course


# ================================
# GET
# ================================
# -------- All Courses ----------
@router.get("", response_model=list[CourseResponse])
async def list_courses(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(Course).options(selectinload(Course.department)))

    courses = result.all()

    if not courses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No courses found"
        )

    return courses


# -------- One Course ----------
@router.get("{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    course = await db.scalar(
        select(Course)
        .options(selectinload(Course.department))
        .where(Course.course_id == course_id)
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    return course


# ================================
# PUT
# ================================


# ================================
# DELETE
# ================================
@router.delete("{course_id}", response_model=CourseResponse)
async def remove_course(course_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    course = (
        await db.scalar(select(Course).where(Course.course_id == course_id))
    ).all()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    await db.delete(course)
    await db.commit()
