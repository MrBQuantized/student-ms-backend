import pytest
from pydantic import ValidationError

from app.schemas import EnrollmentBase, EnrollmentUpdate, GradeEnum


# =================================
# Invalid Grade
# =================================
@pytest.mark.parametrize(
    "grade",
    ["E", "G", "Z", "a", "100", ""],
)
def test_invalid_grade_requirement(grade):

    with pytest.raises(ValidationError):
        EnrollmentUpdate(grade=grade)


# =================================
# Status and Grade
# =================================
def test_completed_enrollment_requires_grade():
    with pytest.raises(ValidationError):
        EnrollmentBase(student_id=1, course_id=1, status="complete", grade=None)


def test_completed_enrollment_with_grade():
    enrollment = EnrollmentBase(
        student_id=1, course_id=1, status="complete", grade="A+"
    )

    assert enrollment.grade == GradeEnum.A_PLUS


def test_active_enrollment_without_grade():
    enrollment = EnrollmentBase(student_id=1, course_id=1, status="active", grade=None)

    assert enrollment.grade is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
