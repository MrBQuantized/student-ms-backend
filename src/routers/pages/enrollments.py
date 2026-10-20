from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
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
