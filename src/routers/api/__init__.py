from fastapi import APIRouter

from .courses import router as courses_router
from .departments import router as departments_router
from .enrollments import router as enrollments_router
from .students import router as students_router

router = APIRouter()

router.include_router(students_router, prefix="/students", tags=["api-students"])
router.include_router(courses_router, prefix="/courses", tags=["api-courses"])
router.include_router(
    departments_router, prefix="/departments", tags=["api-departments"]
)
router.include_router(
    enrollments_router, prefix="/enrollments", tags=["api-enrollments"]
)
