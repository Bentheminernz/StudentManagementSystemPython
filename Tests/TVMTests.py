from Utils.Database import Database
from Utils.ViewModels.TeacherViewModel import TeacherViewModel

"""
This file contains the unit tests for the TeacherViewModel class. These tests cover the basic CRUD operations as well as some edge cases.
"""


def test_teacher_view_model_initialization():
    """Tests that the TeacherViewModel initializes correctly and loads teachers from the database."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    assert len(vm.teachers) == 3
    assert vm.teachers[0].first_name == "Emily"
    assert vm.teachers[1].first_name == "Michael"
    assert vm.teachers[2].first_name == "Sarah"
    db.close()


def test_get_teacher_by_id():
    """Tests that the get_teacher_by_id method returns the correct teacher when given a valid ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    teacher = vm.get_teacher_by_id(1)
    assert teacher is not None
    assert teacher.first_name == "Emily"
    db.close()


def test_add_teacher():
    """Tests that add_teacher inserts a teacher and updates the local list."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = TeacherViewModel(db)
    vm.add_teacher("John", "Doe", "johndoe@example.com")
    teachers = vm.teachers
    assert len(teachers) == 1
    assert teachers[0].first_name == "John"
    assert teachers[0].last_name == "Doe"
    assert teachers[0].email == "johndoe@example.com"
    db.close()


def test_delete_teacher():
    """Tests that delete_teacher removes a teacher and updates the local list."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    vm.delete_teacher(1)
    teachers = vm.teachers
    assert len(teachers) == 2
    assert all(t.id != 1 for t in teachers)
    db.close()


def test_update_teacher():
    """Tests that update_teacher updates teacher details in the DB and view model list."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    vm.update_teacher(1, "John", "Smith", "johnsmith@example.com")
    teachers = vm.teachers
    assert len(teachers) == 3
    updated_teacher = vm.get_teacher_by_id(1)
    assert updated_teacher is not None
    assert updated_teacher.first_name == "John"
    assert updated_teacher.last_name == "Smith"
    assert updated_teacher.email == "johnsmith@example.com"
    db.close()


# boundary/edge cases
def test_teacher_view_model_empty_db():
    """Tests that TeacherViewModel handles an empty database correctly."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = TeacherViewModel(db)
    assert vm.teachers == []
    db.close()


def test_get_teacher_by_id_nonexistent():
    """Tests that get_teacher_by_id returns None for a nonexistent teacher ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    teacher = vm.get_teacher_by_id(9999)
    assert teacher is None
    db.close()


def test_get_teacher_by_id_zero():
    """Tests that get_teacher_by_id returns None for teacher ID 0."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    teacher = vm.get_teacher_by_id(0)
    assert teacher is None
    db.close()


def test_add_teacher_duplicate_email():
    """Tests that add_teacher does not add a second teacher with a duplicate email."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = TeacherViewModel(db)
    vm.add_teacher("John", "Doe", "johndoe@example.com")
    vm.add_teacher("Jane", "Doe", "johndoe@example.com")
    assert len(vm.teachers) == 1
    db.close()


def test_delete_teacher_nonexistent_id():
    """Tests that deleting a nonexistent teacher ID leaves the list unchanged."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    vm.delete_teacher(9999)
    assert len(vm.teachers) == 3
    db.close()


def test_update_teacher_nonexistent_id():
    """Tests that updating a nonexistent teacher ID leaves the list unchanged."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    vm.update_teacher(9999, "Ghost", "User", "ghost@example.com")
    assert len(vm.teachers) == 3
    assert all(t.first_name != "Ghost" for t in vm.teachers)
    db.close()


def test_update_teacher_duplicate_email():
    """Tests that update_teacher fails when trying to use another teacher's email."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    second_teacher = vm.get_teacher_by_id(2)
    assert second_teacher is not None

    vm.update_teacher(1, "Emily", "Davis", second_teacher.email)
    teacher_one = vm.get_teacher_by_id(1)
    assert teacher_one is not None
    assert teacher_one.email == "e.davis@example.com"
    db.close()


def test_delete_all_teachers():
    """Tests that all teachers can be deleted and the local list becomes empty."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = TeacherViewModel(db)
    for teacher in list(vm.teachers):
        vm.delete_teacher(teacher.id)
    assert vm.teachers == []
    db.close()
