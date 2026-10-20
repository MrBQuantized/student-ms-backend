from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import Department, DepartmentCreate, DepartmentResponse, get_db

router = APIRouter()

# ================================
# POST
# ================================


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department: DepartmentCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> str:

    dept_data = department.model_dump()

    # Awaiting the Scalar call
    existing_dept = await db.scalar(
        select(Department).where(Department.code == dept_data["code"])
    )

    if existing_dept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department already exists",
        )

    new_dept = Department(**dept_data)

    db.add(new_dept)
    await db.commit()
    await db.refresh(new_dept, attribute_names=["courses", "students"])

    return new_dept


# ================================
# GET
# ================================
# -------- All Departments ----------
@router.get("", response_model=list[DepartmentResponse])
async def list_departments(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(
        select(Department).options(
            selectinload(Department.students),
            selectinload(Department.courses),
        )
    )

    departments = result.all()

    if not departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No department found"
        )

    return departments


# -------- One Department ----------
@router.get("{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    dept = await db.scalar(
        select(Department)
        .options(
            selectinload(Department.students),
            selectinload(Department.courses),
        )
        .where(Department.id == department_id)
    )

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return dept


# ================================
# PUT
# ================================


# ================================
# DELETE
# ================================
@router.delete("{department_id}", response_model=DepartmentResponse)
async def remove_department(
    department_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):

    department = (
        await db.scalar(select(Department).where(Department.id == department_id))
    ).all()

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Department not found"
        )
    await db.delete(department)
    await db.commit()
