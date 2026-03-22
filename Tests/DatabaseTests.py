from Utils.Database import Database
from Utils.Dataclasses import GradeEnum


"""These tests cover the core database operations for managing students, teachers, classes, and grades. They include both standard CRUD operations and edge cases to ensure robustness of the Database class.
"""


def test_database_initialization():
    """Seeds defaults and verifies initial student records are created."""
    db = Database(db_path=":memory:", seed_defaults=True)
    students = db.get_all_students()
    assert len(students) == 3
    assert students[0].first_name == "Alice"
    assert students[1].first_name == "Bob"
    assert students[2].first_name == "Charlie"
    db.close()


def test_add_student():
    """Adds a student and verifies persisted values."""
    db = Database(db_path=":memory:", seed_defaults=False)

    student = db.add_student("John", "Doe", "john.doe@example.com", "2000-01-01")
    assert student is not None
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert student.email == "john.doe@example.com"

    db.close()


def test_get_student_by_id():
    """Returns a student for a valid student ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(1)
    assert student is not None
    assert student.first_name == "Alice"
    db.close()


def test_update_student():
    """Updates student fields and verifies the changes are persisted."""
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.update_student(
        1, "John", "Smith", "john.smith@example.com", "2000-01-01"
    )
    assert student[0]
    assert student[1] is not None
    student = db.get_student_by_id(1)
    assert student.first_name == "John"
    assert student.last_name == "Smith"
    assert student.email == "john.smith@example.com"
    assert student.date_of_birth == "2000-01-01"
    db.close()


def test_get_all_classes():
    """Returns all seeded classes."""
    db = Database(db_path=":memory:", seed_defaults=True)
    classes = db.get_all_classes()
    assert len(classes) == 2
    assert classes[0].name == "Math 101"
    assert classes[1].name == "Science 101"
    db.close()


def test_get_class_by_id():
    """Returns a class for a valid class ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id(1)
    assert cls is not None
    assert cls.name == "Math 101"
    assert cls.teacher_id == 1
    db.close()


def test_add_class():
    """Adds a class and verifies values."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("History 101", 1)
    assert cls is not None
    assert cls.name == "History 101"
    assert cls.teacher_id == 1
    db.close()


def test_update_class():
    """Updates class details and verifies the persisted result."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success, cls = db.update_class(1, "Advanced Math 101", 2)
    assert success
    assert cls is not None
    cls = db.get_class_by_id(1)
    assert cls.name == "Advanced Math 101"
    assert cls.teacher_id == 2
    db.close()


def test_delete_class():
    """Deletes a class and confirms it is no longer retrievable."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.delete_class(1)
    assert success
    cls = db.get_class_by_id(1)
    assert cls is None
    db.close()


# boundary/edge cases
def test_get_all_students_empty_db():
    """Returns an empty list when no students exist."""
    db = Database(db_path=":memory:", seed_defaults=False)
    students = db.get_all_students()
    assert students == []
    db.close()


def test_get_student_by_id_nonexistent():
    """Returns None for a nonexistent student ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(9999)
    assert student is None
    db.close()


def test_get_student_by_id_zero():
    """Returns None for student ID 0."""
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(0)
    assert student is None
    db.close()


def test_add_student_duplicate_email():
    """Rejects duplicate student emails with a None result."""
    db = Database(db_path=":memory:", seed_defaults=False)
    db.add_student("John", "Doe", "john.doe@example.com", "2000-01-01")
    duplicate = db.add_student("Jane", "Doe", "john.doe@example.com", "2001-01-01")
    assert duplicate is None
    db.close()


def test_add_student_leap_day_on_non_leap_year():
    """Rejects February 29 on a non-leap year."""
    db = Database(db_path=":memory:", seed_defaults=False)
    student = db.add_student("Leap", "Year", "leap.year@example.com", "2001-02-29")
    assert student is None
    db.close()


def test_update_student_nonexistent_id():
    """Updating a missing student returns a failed status with no payload."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success, student = db.update_student(
        9999, "Ghost", "User", "ghost@example.com", "2000-01-01"
    )
    assert success is False
    assert student is None
    db.close()


def test_update_student_duplicate_email():
    """Rejects student email updates that violate uniqueness."""
    db = Database(db_path=":memory:", seed_defaults=True)
    bob = db.get_student_by_id(2)
    success, student = db.update_student(1, "Alice", "Smith", bob.email, "2000-01-01")
    assert success is False
    assert student is None
    db.close()


def test_delete_student_nonexistent_id():
    """Deleting a missing student returns False and leaves data unchanged."""
    db = Database(db_path=":memory:", seed_defaults=True)
    result = db.delete_student(9999)
    assert result is False
    assert len(db.get_all_students()) == 3
    db.close()


def test_get_all_classes_empty_db():
    """Returns an empty class list when none exist."""
    db = Database(db_path=":memory:", seed_defaults=False)
    classes = db.get_all_classes()
    assert classes == []
    db.close()


def test_get_class_by_id_nonexistent():
    """Returns None for a nonexistent class ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id(9999)
    assert cls is None
    db.close()


def test_get_class_by_id_invalid_type():
    """Returns None when class lookup uses an invalid ID type."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id("invalid")
    assert cls is None
    db.close()


def test_delete_class_nonexistent_id():
    """Deleting a missing class returns False and leaves data unchanged."""
    db = Database(db_path=":memory:", seed_defaults=True)
    result = db.delete_class(9999)
    assert result is False
    assert len(db.get_all_classes()) == 2
    db.close()


def test_add_student_rejects_stupidly_long_name():
    """Rejects student names beyond the configured maximum length."""
    db = Database(db_path=":memory:", seed_defaults=False)
    long_name = "A" * 81
    student = db.add_student(long_name, "Doe", "john.doe@example.com", "2000-01-01")
    assert student is None
    assert db.get_all_students() == []
    db.close()


def test_add_student_accepts_unicode_and_numeric_name_content():
    """Accepts Unicode and numeric characters in names while still validating boundaries."""
    db = Database(db_path=":memory:", seed_defaults=False)
    student = db.add_student(
        "X AE A-12",
        "Mu\N{LATIN SMALL LETTER E WITH ACUTE}ller9",
        "x.ae@example.com",
        "2000-01-01",
    )
    assert student is not None
    assert student.first_name == "X AE A-12"
    assert student.last_name == "Mu\N{LATIN SMALL LETTER E WITH ACUTE}ller9"
    db.close()


def test_add_student_rejects_future_date_of_birth():
    """Rejects dates of birth in the future."""
    db = Database(db_path=":memory:", seed_defaults=False)
    student = db.add_student("John", "Doe", "john.doe@example.com", "2999-01-01")
    assert student is None
    db.close()


def test_add_teacher_email_is_case_normalized_for_uniqueness():
    """Treats mixed-case duplicate emails as the same logical email."""
    db = Database(db_path=":memory:", seed_defaults=False)
    teacher = db.add_teacher("Jane", "Doe", "Jane.Doe@Example.COM")
    duplicate = db.add_teacher("Janet", "Doe", "jane.doe@example.com")
    assert teacher is not None
    assert teacher.email == "jane.doe@example.com"
    assert duplicate is None
    db.close()


def test_add_class_rejects_stupidly_long_name():
    """Rejects class names beyond the configured maximum length."""
    db = Database(db_path=":memory:", seed_defaults=True)
    long_name = "C" * 121
    cls = db.add_class(long_name, 1)
    assert cls is None
    db.close()


def test_set_students_for_class_rejects_invalid_student_ids():
    """Rejects class enrollment updates containing non-positive IDs."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.set_students_for_class(1, [1, 0, 2])
    assert success is False
    db.close()


def test_delete_student_rejects_invalid_id_boundary():
    """Rejects boundary-invalid IDs (zero or negative)."""
    db = Database(db_path=":memory:", seed_defaults=True)
    assert db.delete_student(0) is False
    assert db.delete_student(-1) is False
    db.close()


def test_get_students_by_class_id_no_enrolments():
    """Returns no students for a class with no enrolments."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("Empty Class", 1)
    students = db.get_students_by_class_id(cls.id)
    assert students == []
    db.close()


def test_set_students_for_class_empty_list_removes_all():
    """Replacing class enrolments with an empty list removes all students."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.set_students_for_class(1, [])
    assert success is True
    assert db.get_students_by_class_id(1) == []
    db.close()


def test_set_students_for_class_nonexistent_class():
    """Returns False when setting enrolments for a missing class."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.set_students_for_class(9999, [1, 2])
    assert success is False
    db.close()


def test_get_classes_by_student_id_returns_enrolled_classes():
    """Returns all classes a student is enrolled in."""
    db = Database(db_path=":memory:", seed_defaults=False)
    student = db.add_student("Ava", "Reed", "ava@example.com", "2005-01-01")
    teacher = db.add_teacher("Paul", "West", "paul@example.com")
    assert student is not None
    assert teacher is not None

    maths = db.add_class("Maths", teacher.id)
    history = db.add_class("History", teacher.id)
    assert maths is not None
    assert history is not None

    assert db.set_students_for_class(maths.id, [student.id]) is True
    assert db.set_students_for_class(history.id, [student.id]) is True

    classes = db.get_classes_by_student_id(student.id)
    class_names = {c.name for c in classes}
    assert class_names == {"Maths", "History"}
    db.close()


def test_set_and_get_grade_for_student_in_class():
    """Creates a class grade and verifies it can be retrieved."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success, grade = db.set_grade_for_student_in_class(1, 1, GradeEnum.A)
    assert success is True
    assert grade is not None
    assert grade.student_id == 1
    assert grade.class_id == 1
    assert grade.grade == GradeEnum.A

    fetched = db.get_grade_for_student_in_class(1, 1)
    assert fetched is not None
    assert fetched.grade == GradeEnum.A
    db.close()


def test_update_existing_grade_for_student_in_class():
    """Updates an existing class grade in place."""
    db = Database(db_path=":memory:", seed_defaults=True)
    first_success, _ = db.set_grade_for_student_in_class(1, 1, GradeEnum.B)
    second_success, updated = db.set_grade_for_student_in_class(1, 1, GradeEnum.A)
    assert first_success is True
    assert second_success is True
    assert updated is not None
    assert updated.grade == GradeEnum.A
    db.close()


def test_set_grade_fails_when_student_not_enrolled():
    """Rejects grade assignment when student is not enrolled in the class."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("History 101", 1)
    assert cls is not None
    success, grade = db.set_grade_for_student_in_class(1, cls.id, GradeEnum.A)
    assert success is False
    assert grade is None
    db.close()


def test_set_grade_with_reason_fails_when_student_not_enrolled():
    """Returns a specific reason when assigning a grade to a non-enrolled student."""
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("History 101", 1)
    assert cls is not None

    success, grade, reason = db.set_grade_for_student_in_class_with_reason(
        1, cls.id, GradeEnum.A
    )

    assert success is False
    assert grade is None
    assert reason == "This student is not enrolled in this class."
    assert db.get_grade_for_student_in_class(1, cls.id) is None
    db.close()


def test_set_grade_fails_for_invalid_grade_value():
    """Rejects invalid grade values outside the GradeEnum set."""
    db = Database(db_path=":memory:", seed_defaults=True)
    success, grade = db.set_grade_for_student_in_class(1, 1, "Z")
    assert success is False
    assert grade is None
    db.close()


def test_get_grades_for_student_returns_class_grades():
    """Returns all class-level grades for a student."""
    db = Database(db_path=":memory:", seed_defaults=False)
    student = db.add_student("Sam", "Taylor", "sam@example.com", "2005-05-01")
    teacher = db.add_teacher("Emma", "Stone", "emma@example.com")
    assert student is not None
    assert teacher is not None
    maths = db.add_class("Maths", teacher.id)
    science = db.add_class("Science", teacher.id)
    assert maths is not None
    assert science is not None

    assert db.set_students_for_class(maths.id, [student.id]) is True
    assert db.set_students_for_class(science.id, [student.id]) is True

    success_math, _ = db.set_grade_for_student_in_class(
        student.id, maths.id, GradeEnum.A
    )
    success_science, _ = db.set_grade_for_student_in_class(
        student.id, science.id, GradeEnum.B
    )
    assert success_math is True
    assert success_science is True

    grades = db.get_grades_for_student(student.id)
    grade_by_class = {g.class_id: g.grade for g in grades}
    assert grade_by_class[maths.id] == GradeEnum.A
    assert grade_by_class[science.id] == GradeEnum.B
    db.close()
