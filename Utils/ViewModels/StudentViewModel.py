from Utils.Database import Database
from Utils.Dataclasses import Student
from typing import List


class StudentViewModel:
    def __init__(self, db: Database):
        self.db = db
        self.students: List[Student] = []
        self.load_students()

    def load_students(self):
        self.students = self.db.get_all_students()

    def get_student_by_id(self, student_id: int) -> Student:
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def add_student(
        self, first_name: str, last_name: str, email: str, date_of_birth: str
    ):
        new_student = self.db.add_student(first_name, last_name, email, date_of_birth)
        if new_student:
            self.students.append(new_student)
        else:
            print("Failed to add student to the database.")

    def delete_student(self, student_id: int):
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
