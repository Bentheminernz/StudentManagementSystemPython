from Utils.Database import Database


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
