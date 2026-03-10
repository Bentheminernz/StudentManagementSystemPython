from typing import Self
from enum import Enum
from dataclasses import dataclass
import sqlite3

"""
In this file, we define the dataclasses for our application:
- Admin
- Student
- Teacher
- Class
- Grade

Each dataclass has a `from_row` class method that takes a sqlite3.Row and then turns it into an instance of the dataclass.

It also has the GradeEnum, which is an enum for the possible grades a student can receive in a class. Means we can only set grades to A, B, C, D, or F.
"""


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

    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

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

    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


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


class GradeEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class Grade:
    id: int
    student_id: int
    class_id: int
    grade: GradeEnum
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Self:
        return cls(
            id=row["id"],
            student_id=row["student_id"],
            class_id=row["class_id"],
            grade=GradeEnum(row["grade"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
