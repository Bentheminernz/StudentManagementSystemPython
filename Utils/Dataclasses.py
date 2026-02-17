from typing import Self
from dataclasses import dataclass
import sqlite3

@dataclass
class Admin:
    id: int
    first_name: str
    last_name: str
    email: str
    password: str
    date_of_birth: str
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            password=row["password"],
            date_of_birth=row["date_of_birth"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

@dataclass
class Student:
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            date_of_birth=row["date_of_birth"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

@dataclass
class Teacher:
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: str
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            date_of_birth=row["date_of_birth"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

@dataclass
class Class:
    id: int
    name: str
    teacher_id: int
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            name=row["name"],
            teacher_id=row["teacher_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

@dataclass
class Assignment:
    id: int
    title: str
    information: str
    due_date: str
    class_id: int
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            title=row["title"],
            information=row["information"],
            due_date=row["due_date"],
            class_id=row["class_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

@dataclass
class Grade:
    id: int
    student_id: int
    assignment_id: int
    grade: float
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            student_id=row["student_id"],
            assignment_id=row["assignment_id"],
            grade=row["grade"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )