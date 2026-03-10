from Utils.Database import Database
from Utils.Dataclasses import Student
from typing import List


"""
The StudentViewModel is responsible for managing the state and operations related to students in the application.
I'm using view models as it takes the logic away from the UI, and it can be used between multiple different pages if needed.
"""


class StudentViewModel:
    def __init__(self, db: Database):
        """Initializes the StudentViewModel with a reference to the database and loads the initial list of students."""
        self.db = db
        self.students: List[Student] = []
        self.load_students()

    def load_students(self):
        """Loads the list of students from the database and stores it in the `students` variable."""
        self.students = self.db.get_all_students()

    def get_student_by_id(self, student_id: int) -> Student:
        """Helper method to find a student in the `students` list by their ID."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def add_student(
        self, first_name: str, last_name: str, email: str, date_of_birth: str
    ):
        """Adds a new student to the database and updates the `students` list."""
        new_student = self.db.add_student(first_name, last_name, email, date_of_birth)
        if new_student:
            self.students.append(new_student)
        else:
            print("Failed to add student to the database.")

    def delete_student(self, student_id: int):
        """Deletes a student from the database and updates the `students` list."""
        success = self.db.delete_student(student_id)
        if success:
            self.students = [s for s in self.students if s.id != student_id]
        else:
            print("Failed to delete student from the database.")

    def update_student(
        self,
        student_id: int,
        first_name: str,
        last_name: str,
        email: str,
        date_of_birth: str,
    ):
        """Updates a student in the database and updates the `students` list."""
        success, student = self.db.update_student(
            student_id, first_name, last_name, email, date_of_birth
        )
        if success:
            for i, s in enumerate(self.students):
                if s.id == student_id:
                    self.students[i] = student
                    break
        else:
            print("Failed to update student in the database.")
