from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# =================================
# Gender
# =================================
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


# =================================
# Grade
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


# =================================
# Department
# =================================
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    students: Mapped[list[Student]] = relationship(
        "Student", back_populates="department"
    )

    # Relationship with Course
    courses: Mapped[list[Course]] = relationship("Course", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, name='{self.name}', code='{self.code}')>"


# =================================
# Student
# =================================,
class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("email", name="uq_student_email"),
        CheckConstraint(
            "gender IS NULL OR gender IN ('male', 'female')", name="ck_student_gender"
        ),
        CheckConstraint(
            "level IS NULL OR level BETWEEN 100 AND 700", name="ck_student_level"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    date_of_birth: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Gender] = mapped_column(
        SQLEnum(
            Gender,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            name="gender",
        ),
        nullable=False,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    image_file: Mapped[str] = mapped_column(String(200), nullable=True)

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # department_name: Mapped[str] = mapped_column(
    #     ForeignKey("departments.name", ondelete="RESTRICT"),
    #     nullable=False,
    # )
    department: Mapped[Department] = relationship(
        "Department", back_populates="students"
    )

    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    @property
    def image_url(self):
        if self.image_file:
            return f"/media/images/{self.image_file}"
        return "/static/images/default.jpg"

    def __repr__(self) -> str:
        return f"<Student {self.student_id} - {self.first_name} - {self.last_name}>"


# =================================
# Course
# =================================
class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (CheckConstraint("units > 0", name="ck_units_positive"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    units: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=False
    )

    department: Mapped[Department | None] = relationship(
        "Department", back_populates="courses"
    )

    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self):
        return f"<Course {self.code} - {self.title}>"


# =================================
# Enrollment
# =================================
class Enrollment(Base):
    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
        CheckConstraint(
            "grade IS NULL OR grade IN ('A+','A','B+','B','C+','C','D+','D','E','F')",
            name="ck_enrollments_grade",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    grade: Mapped[GradeEnum | None] = mapped_column(String(2), nullable=True)

    # Relationship with Student and Course
    student: Mapped[Student] = relationship(
        "Student", back_populates="enrollments", passive_deletes=True
    )
    course: Mapped[Course] = relationship(
        "Course", back_populates="enrollments", passive_deletes=True
    )

    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Enrollment student={self.student_id} course={self.course_id}>"
