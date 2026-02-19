from Utils.Database import Database
from Utils.Dataclasses import Teacher
from typing import List


class TeacherViewModel:
    def __init__(self, db: Database):
        self.db = db
        self.teachers: List[Teacher] = []
        self.load_teachers()

    def load_teachers(self):
        self.teachers = self.db.get_all_teachers()

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        for teacher in self.teachers:
            if teacher.id == teacher_id:
                return teacher
        return None

    def add_teacher(self, first_name: str, last_name: str, email: str):
        new_teacher = self.db.add_teacher(first_name, last_name, email)
        if new_teacher:
            self.teachers.append(new_teacher)
        else:
            print("Failed to add teacher to the database.")

    def delete_teacher(self, teacher_id: int):
        success = self.db.delete_teacher(teacher_id)
        if success:
            self.teachers = [t for t in self.teachers if t.id != teacher_id]
        else:
            print("Failed to delete teacher from the database.")

    def update_teacher(
        self, teacher_id: int, first_name: str, last_name: str, email: str
    ):
        success, teacher = self.db.update_teacher(
            teacher_id, first_name, last_name, email
        )
        if success:
            for i, t in enumerate(self.teachers):
                if t.id == teacher_id:
                    self.teachers[i] = teacher
                    break
        else:
            print("Failed to update teacher in the database.")
