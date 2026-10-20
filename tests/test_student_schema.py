import pytest
from pydantic import ValidationError

from app.schemas import CourseCreate, DepartmentCreate

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
