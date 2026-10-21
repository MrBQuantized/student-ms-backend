from fastapi import APIRouter

from .courses import router as courses_router
from .departments import router as departments_router
from .enrollments import router as enrollments_router
from .home import router as home_router
from .students import router as students_router

router = APIRouter()
router.include_router(home_router, prefix="/home", tags=["pages-home"])
router.include_router(students_router, prefix="/students", tags=["pages-students"])
router.include_router(courses_router, prefix="/courses", tags=["pages-courses"])
router.include_router(
    departments_router, prefix="/departments", tags=["pages-departments"]
)
router.include_router(
    enrollments_router, prefix="/enrollments", tags=["pages-enrollments"]
)
