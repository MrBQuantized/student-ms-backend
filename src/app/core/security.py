from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import PasswordUpdate, Student, get_db

router = APIRouter()

# Configure the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Turn a plaintext password into a secure hashed password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# Password Update
@router.patch("{student_id}/password", status_code=status.HTTP_204_NO_CONTENT)
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
