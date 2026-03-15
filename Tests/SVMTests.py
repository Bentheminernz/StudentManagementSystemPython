from Utils.Database import Database
from Utils.ViewModels.StudentViewModel import StudentViewModel

"""
This file contains the unit tests for the StudentViewModel class. These tests cover the basic CRUD operations as well as some edge cases.
"""


def test_student_view_model_initialization():
    """Tests that the StudentViewModel initializes correctly and loads students from the database."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    assert len(vm.students) == 3
    assert vm.students[0].first_name == "Alice"
    assert vm.students[1].first_name == "Bob"
    assert vm.students[2].first_name == "Charlie"
    db.close()


def test_get_student_by_id():
    """Tests that the get_student_by_id method returns the correct student when given a valid ID, and returns None for an invalid ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    student = vm.get_student_by_id(1)
    assert student is not None
    assert student.first_name == "Alice"
    db.close()


def test_add_student():
    """Tests that the add_student method adds a new student to the database and updates the students list."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = StudentViewModel(db)
    vm.add_student("John", "Doe", "johndoe@example.com", "2000-01-01")
    students = vm.students
    assert len(students) == 1
    assert students[0].first_name == "John"
    assert students[0].last_name == "Doe"
    assert students[0].email == "johndoe@example.com"
    assert students[0].date_of_birth == "2000-01-01"
    db.close()


def test_delete_student():
    """Tests that the delete_student method removes a student from the database and updates the students list."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    vm.delete_student(1)
    students = vm.students
    assert len(students) == 2
    assert all(s.id != 1 for s in students)
    db.close()


def test_update_student():
    """Tests that the update_student method updates a student's information in the database and updates the students list."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    vm.update_student(1, "John", "Smith", "johnsmith@example.com", "1999-12-31")
    students = vm.students
    assert len(students) == 3
    updated_student = vm.get_student_by_id(1)
    assert updated_student.first_name == "John"
    assert updated_student.last_name == "Smith"
    assert updated_student.email == "johnsmith@example.com"
    assert updated_student.date_of_birth == "1999-12-31"
    db.close()


# boundary/edge cases
def test_student_view_model_empty_db():
    """Tests that the StudentViewModel initializes correctly when the database is empty and that get_student_by_id returns None."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = StudentViewModel(db)
    assert vm.students == []
    db.close()


def test_get_student_by_id_nonexistent():
    """Tests that the get_student_by_id method returns None for a nonexistent student ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    student = vm.get_student_by_id(9999)
    assert student is None
    db.close()


def test_get_student_by_id_zero():
    """Tests that the get_student_by_id method returns None for a student ID of 0."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    student = vm.get_student_by_id(0)
    assert student is None
    db.close()


def test_add_student_duplicate_email():
    """Tests that the add_student method does not allow adding a student with a duplicate email address."""
    db = Database(db_path=":memory:", seed_defaults=False)
    vm = StudentViewModel(db)
    vm.add_student("John", "Doe", "johndoe@example.com", "2000-01-01")
    vm.add_student("Jane", "Doe", "johndoe@example.com", "2001-01-01")
    assert len(vm.students) == 1
    db.close()


def test_delete_student_nonexistent_id():
    """Tests that the delete_student method does not change the students list when given a nonexistent student ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    vm.delete_student(9999)
    assert len(vm.students) == 3
    db.close()


def test_update_student_nonexistent_id():
    """Tests that the update_student method does not change the students list when given a nonexistent student ID."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    vm.update_student(9999, "Ghost", "User", "ghost@example.com", "2000-01-01")
    assert len(vm.students) == 3
    assert all(s.first_name != "Ghost" for s in vm.students)
    db.close()


def test_delete_all_students():
    """Tests that all students can be deleted from the database and that the students list is updated accordingly."""
    db = Database(db_path=":memory:", seed_defaults=True)
    vm = StudentViewModel(db)
    for student in list(vm.students):
        vm.delete_student(student.id)
    assert vm.students == []
    db.close()
