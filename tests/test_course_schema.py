import pytest
from pydantic import ValidationError

from app.schemas import CourseCreate


def test_valid_course_code():
    course = CourseCreate(
        title="Linear Algebra",
        code="MTH101",
        units=4,
    )

    assert course.code == "MTH101"


@pytest.mark.parametrize(
    "course_code",
    [
        "MTH10",
        "MTH1001",
        "MT101",
        "mth101",
        "MTHABC",
        "",
    ],
)
def test_invalid_course_code(course_code):
    with pytest.raises(ValidationError):
        CourseCreate(code=course_code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
