from Utils.Database import Database
from Utils.Dataclasses import GradeEnum


def test_database_initialization():
    db = Database(db_path=":memory:", seed_defaults=True)
    students = db.get_all_students()
    assert len(students) == 3
    assert students[0].first_name == "Alice"
    assert students[1].first_name == "Bob"
    assert students[2].first_name == "Charlie"
    db.close()


def test_add_student():
    db = Database(db_path=":memory:", seed_defaults=False)

    student = db.add_student("John", "Doe", "john.doe@example.com", "2000-01-01")
    assert student is not None
    assert student.first_name == "John"
    assert student.last_name == "Doe"
    assert student.email == "john.doe@example.com"

    db.close()


def test_get_student_by_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(1)
    assert student is not None
    assert student.first_name == "Alice"
    db.close()


def test_update_student():
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
    db = Database(db_path=":memory:", seed_defaults=True)
    classes = db.get_all_classes()
    assert len(classes) == 2
    assert classes[0].name == "Math 101"
    assert classes[1].name == "Science 101"
    db.close()


def test_get_class_by_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id(1)
    assert cls is not None
    assert cls.name == "Math 101"
    assert cls.teacher_id == 1
    db.close()


def test_add_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("History 101", 1)
    assert cls is not None
    assert cls.name == "History 101"
    assert cls.teacher_id == 1
    db.close()


def test_update_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    success, cls = db.update_class(1, "Advanced Math 101", 2)
    assert success
    assert cls is not None
    cls = db.get_class_by_id(1)
    assert cls.name == "Advanced Math 101"
    assert cls.teacher_id == 2
    db.close()


def test_delete_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.delete_class(1)
    assert success
    cls = db.get_class_by_id(1)
    assert cls is None
    db.close()


# boundary/edge cases
def test_get_all_students_empty_db():
    db = Database(db_path=":memory:", seed_defaults=False)
    students = db.get_all_students()
    assert students == []
    db.close()


def test_get_student_by_id_nonexistent():
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(9999)
    assert student is None
    db.close()


def test_get_student_by_id_zero():
    db = Database(db_path=":memory:", seed_defaults=True)
    student = db.get_student_by_id(0)
    assert student is None
    db.close()


def test_add_student_duplicate_email():
    db = Database(db_path=":memory:", seed_defaults=False)
    db.add_student("John", "Doe", "john.doe@example.com", "2000-01-01")
    duplicate = db.add_student("Jane", "Doe", "john.doe@example.com", "2001-01-01")
    assert duplicate is None
    db.close()


def test_update_student_nonexistent_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    success, student = db.update_student(
        9999, "Ghost", "User", "ghost@example.com", "2000-01-01"
    )
    assert success is True
    assert student is None
    db.close()


def test_update_student_duplicate_email():
    db = Database(db_path=":memory:", seed_defaults=True)
    bob = db.get_student_by_id(2)
    success, student = db.update_student(1, "Alice", "Smith", bob.email, "2000-01-01")
    assert success is False
    assert student is None
    db.close()


def test_delete_student_nonexistent_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    result = db.delete_student(9999)
    assert result is True
    assert len(db.get_all_students()) == 3
    db.close()


def test_get_all_classes_empty_db():
    db = Database(db_path=":memory:", seed_defaults=False)
    classes = db.get_all_classes()
    assert classes == []
    db.close()


def test_get_class_by_id_nonexistent():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id(9999)
    assert cls is None
    db.close()


def test_get_class_by_id_invalid_type():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.get_class_by_id("invalid")
    assert cls is None
    db.close()


def test_delete_class_nonexistent_id():
    db = Database(db_path=":memory:", seed_defaults=True)
    result = db.delete_class(9999)
    assert result is True
    assert len(db.get_all_classes()) == 2
    db.close()


def test_get_students_by_class_id_no_enrolments():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("Empty Class", 1)
    students = db.get_students_by_class_id(cls.id)
    assert students == []
    db.close()


def test_set_students_for_class_empty_list_removes_all():
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.set_students_for_class(1, [])
    assert success is True
    assert db.get_students_by_class_id(1) == []
    db.close()


def test_set_students_for_class_nonexistent_class():
    db = Database(db_path=":memory:", seed_defaults=True)
    success = db.set_students_for_class(9999, [1, 2])
    assert success is False
    db.close()


def test_get_classes_by_student_id_returns_enrolled_classes():
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
    db = Database(db_path=":memory:", seed_defaults=True)
    first_success, _ = db.set_grade_for_student_in_class(1, 1, GradeEnum.B)
    second_success, updated = db.set_grade_for_student_in_class(1, 1, GradeEnum.A)
    assert first_success is True
    assert second_success is True
    assert updated is not None
    assert updated.grade == GradeEnum.A
    db.close()


def test_set_grade_fails_when_student_not_enrolled():
    db = Database(db_path=":memory:", seed_defaults=True)
    cls = db.add_class("History 101", 1)
    assert cls is not None
    success, grade = db.set_grade_for_student_in_class(1, cls.id, GradeEnum.A)
    assert success is False
    assert grade is None
    db.close()


def test_set_grade_fails_for_invalid_grade_value():
    db = Database(db_path=":memory:", seed_defaults=True)
    success, grade = db.set_grade_for_student_in_class(1, 1, "Z")
    assert success is False
    assert grade is None
    db.close()


def test_get_grades_for_student_returns_class_grades():
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
