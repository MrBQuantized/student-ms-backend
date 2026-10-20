import pytest
from pydantic import ValidationError

from app.schemas import DepartmentCreate


def test_valid_dept_code():
    department = DepartmentCreate(name="Mathematics", code="MTH")

    assert department.code == "MTH"


@pytest.mark.parametrize(
    "dept_code",
    [
        "MTh",
        "MaTH",
        "MATH",
        "math",
        "Math",
        "",
    ],
)
def test_invalid_dept_code(dept_code):
    with pytest.raises(ValidationError):
        DepartmentCreate(code=dept_code)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
