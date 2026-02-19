from Utils.Database import Database
from Utils.Dataclasses import Class
from typing import List


class ClassViewModel:
    def __init__(self, db: Database):
        self.db = db
        self.classes: List[Class] = []
        self.load_classes()

    def load_classes(self):
        self.classes = self.db.get_all_classes()

    def get_class_by_id(self, class_id: int) -> Class | None:
        for cls in self.classes:
            if cls.id == class_id:
                return cls
        return None

    def add_class(self, name: str, teacher_id: int):
        new_class = self.db.add_class(name, teacher_id)
        if new_class:
            self.classes.append(new_class)
        else:
            print("Failed to add class to the database.")

    def delete_class(self, class_id: int):
        success = self.db.delete_class(class_id)
        if success:
            self.classes = [c for c in self.classes if c.id != class_id]
        else:
            print("Failed to delete class from the database.")

    def update_class(self, class_id: int, name: str, teacher_id: int):
        success, cls = self.db.update_class(class_id, name, teacher_id)
        if success:
            for i, c in enumerate(self.classes):
                if c.id == class_id:
                    self.classes[i] = cls
                    break
        else:
            print("Failed to update class in the database.")
