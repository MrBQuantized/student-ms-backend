import pytest
from sqlalchemy.exc import IntegrityError

from ..src.app.models import (
    Enrollment,
)


def test_cascade_student_delete(db, student):
    student_id = student.id
    db.delete(student)
    db.commit()
    assert db.query(Enrollment).filter_by(student_id=student_id).count() == 0


def test_department_restrict(db, department_with_students):
    with pytest.raises(IntegrityError):
        db.delete(department_with_students)
        db.commit()


def test_course_department_set_null(db, course, department):
    course.department = department
    db.commit()
    db.delete(department)
    db.commit()
    db.refresh(course)
    assert course.department_id is None


def test_duplicate_enrollment_rejected(db):
    e1 = Enrollment(student_id=1, course_id=1)
    e2 = Enrollment(student_id=1, course_id=1)
    db.add_all([e1, e2])
    with pytest.raises(IntegrityError):
        db.commit()


def test_invalid_grade_rejected(db):
    e = Enrollment(student_id=1, course_id=2, grade="ZZ")
    db.add(e)
    with pytest.raises(IntegrityError):
        db.commit()
