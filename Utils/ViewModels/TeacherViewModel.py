from Utils.Database import Database
from Utils.Dataclasses import Teacher
from typing import List


"""
The TeacherViewModel is responsible for managing the state and operations related to teachers in the application.
I'm using view models as it takes the logic away from the UI, and it can be used between multiple different pages if needed.
"""


class TeacherViewModel:
    def __init__(self, db: Database):
        """Initializes the TeacherViewModel with a reference to the database and loads the initial list of teachers."""
        self.db = db
        self.teachers: List[Teacher] = []
        self.load_teachers()

    def load_teachers(self):
        """Loads the list of teachers from the database and stores it in the `teachers` variable."""
        self.teachers = self.db.get_all_teachers()

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """Helper method to find a teacher in the `teachers` list by their ID."""
        for teacher in self.teachers:
            if teacher.id == teacher_id:
                return teacher
        return None

    def add_teacher(self, first_name: str, last_name: str, email: str):
        """Adds a new teacher to the database and updates the `teachers` list."""
        new_teacher = self.db.add_teacher(first_name, last_name, email)
        if new_teacher:
            self.teachers.append(new_teacher)
        else:
            print("Failed to add teacher to the database.")

    def delete_teacher(self, teacher_id: int):
        """Deletes a teacher from the database and updates the `teachers` list."""
        success = self.db.delete_teacher(teacher_id)
        if success:
            self.teachers = [t for t in self.teachers if t.id != teacher_id]
        else:
            print("Failed to delete teacher from the database.")

    def update_teacher(
        self, teacher_id: int, first_name: str, last_name: str, email: str
    ):
        """Updates a teacher in the database and updates the `teachers` list."""
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
