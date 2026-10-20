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


# ================================
# GET
# ================================


# ================================
# PUT
# ================================


# ================================
# DELETE
# ================================
