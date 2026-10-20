import re
from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


# ===================================
# GENDER ENUM
# ===================================
class GenderEnum(str, Enum):
    male = "male"
    female = "female"


# =================================
# GRADE ENUM
# =================================
class GradeEnum(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D_PLUS = "D+"
    D = "D"
    E = "E"
    F = "F"


# ===================================
# DEPARTMENT
# ===================================


# ---------- Base (shared fields only) ----------
class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=30)
    code: str = Field(..., min_length=3)

    @field_validator("code")
    @classmethod
    def validate_dept_code(cls, value: str) -> str:
        pattern = r"^[A-Z]{3}$"
        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid department code. Expected format: MTH")
        return value


# ---------- Create ----------
class DepartmentCreate(DepartmentBase):
    pass


# ---------- Update (all fields optional) ----------
class DepartmentUpdate(BaseModel):
    code: str | None = Field(None, min_length=3, max_length=10)
    name: str | None = Field(None, min_length=2, max_length=30)


# ---------- Response (include id + relations) ----------
class DepartmentResponse(DepartmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ===================================
# STUDENT
# ===================================


# ---------- Base (shared fields only) ----------
class StudentBase(BaseModel):
    # student_id: str = Field(..., min_length=6, max_length=6)
    first_name: str = Field(..., max_length=100)
    middle_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    date_of_birth: date
    gender: GenderEnum
    level: int = Field(
        ...,
        le=500,
    )


# ---------- Create ----------
class StudentCreate(StudentBase):
    password: str = Field(..., min_length=8)
    department_id: int


class StudentPut(BaseModel):
    # student_id: str | None = Field(..., max_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: date
    gender: GenderEnum
    level: int = Field(..., ge=100, le=500)
    department_id: int
    # NO student_id (it's in the URL)
    # NO password (it has its own endpoint: PasswordUpdate)


# ---------- Update (all fields optional) ----------
class StudentUpdate(BaseModel):
    # student_id: str | None = Field(..., min_length=6, max_length=6)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    gender: GenderEnum | None = None
    date_of_birth: date | None = None
    level: int | None = Field(None, ge=100, le=500)
    department_id: int | None = None


# ---------- Response (output) ----------
class StudentResponse(StudentBase):
    student_id: str | None = Field(..., min_length=6, max_length=13)
    is_active: bool = True

    department_id: int
    department: DepartmentResponse | None = None

    model_config = ConfigDict(from_attributes=True)

    image_file: str | None = None
    image_url: str

    created_at: datetime
    updated_at: datetime


# ===================================
# COURSE
# ===================================


# ---------- Base (shared fields only) ----------
class CourseBase(BaseModel):
    title: str = Field(..., min_length=6)
    code: str

    @field_validator("code")
    @classmethod
    def uppercase_title(cls, title: str) -> str:
        return title.upper()

    @field_validator("code")
    @classmethod
    def alpha_numeric_code(cls, value: str) -> str:
        pattern = r"^[A-Z]{3}[0-9]{3}$"
        # Course code must be a string of alphanumeric order
        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid course code. Expected format: MTH101")
        return value


class CourseCreate(CourseBase):
    units: int = Field(..., le=4)
    department_id: int


class CourseResponse(CourseBase):
    id: int

    department_id: int
    department: DepartmentResponse | None = None

    created_at: datetime


# ===================================
# ENROLLMENT
# ===================================


# ---------- Enums ----------
class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETE = "complete"
    DROPPED = "dropped"
    PENDING = "pending"


# ---------- Base (shared fields only) ----------
class EnrollmentBase(BaseModel):
    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)

    enrolled_at: date = Field(default_factory=date.today)
    status: EnrollmentStatus = EnrollmentStatus.ACTIVE

    # Optional — only set when the course is completed
    grade: GradeEnum | None = Field(None, min_length=1)

    @model_validator(mode="after")
    def validate_enrollment(self):
        if self.status == EnrollmentStatus.COMPLETE and self.grade is None:
            raise ValueError("grade is required when the status is 'completed'")
        return self


# ---------- Create ----------
class EnrollmentCreate(EnrollmentBase):
    pass


# ---------- Create ----------
class EnrollmentUpdate(BaseModel):
    status: EnrollmentStatus | None = None
    grade: float | None = Field(None, ge=0, le=100)


# ---------- Nested summaries (for responses) ----------
class StudentSummary(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class CourseSummary(BaseModel):
    id: int
    code: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# ---------- Response ----------
class EnrollmentResponse(EnrollmentBase):
    id: int
    enrolled_at: datetime | None = None

    # Full nested objects, not strings
    student: StudentSummary
    course: CourseSummary

    model_config = ConfigDict(from_attributes=True)


# ===================================
# ASSESSMENT
# ===================================


# ===================================
# PASSWORD
# ===================================


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
