import random
import sqlite3
from Utils.Dataclasses import Student, Class, Teacher, Grade, GradeEnum


"""
This file contains the Database class, which is the manager for all interactions with the SQLite database.
It handles all the CRUD (Create, Read, Update, Delete) operations for students, classes, teachers, and grades.
It also has the logic for initializing the database, creating tables, and seeding default data if the tables are empty (and the seed_defaults flag is set to True).
"""


class Database:
    def __init__(self, db_path: str = "app_data.db", seed_defaults: bool = True):
        """Initializes the instance, makes a db connection, creates tables if they don't exist and seeds default data if the tables are empty and seed_defaults is True."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        if seed_defaults:
            self._seed_defaults()

    def close(self) -> None:
        """simple method to close the database connection when we're done with it."""
        if self.conn:
            self.conn.close()

    def _create_tables(self):
        """Creates the necessary tables for the application if they do not already exist."""
        self.conn.executescript("""
            -- This is SQL code, it creates the tables for our database with the appropriate columns and constraints.
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                date_of_birth DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                                
            CREATE TABLE IF NOT EXISTS student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                date_of_birth DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS teacher (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                date_of_birth DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS class (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS grade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                grade TEXT NOT NULL CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE,
                UNIQUE (student_id, class_id)
            );

            CREATE TABLE IF NOT EXISTS class_student (
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                PRIMARY KEY (class_id, student_id),
                FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()  # Saves the transaction to the db file

    def _table_is_empty(self, table_name: str) -> bool:
        """Checks if a given table is empty."""
        cursor = self.conn.execute(f"SELECT COUNT(*) AS count FROM {table_name};")
        row = cursor.fetchone()
        return row["count"] == 0

    def _seed_defaults(self):
        """Seeds the database with default data if the tables are empty."""
        if self._table_is_empty("admin"):
            self.conn.execute(
                """
                INSERT INTO admin (first_name, last_name, email, password, date_of_birth)
                VALUES (?, ?, ?, ?, date('now'));
                """,
                ("Admin", "User", "admin@example.com", "test"),
            )

        if self._table_is_empty("student"):
            default_students = [
                ("Alice", "Smith", "alicesmith@example.com"),
                ("Bob", "Johnson", "bobjohnson@example.com"),
                ("Charlie", "Brown", "charliebrown@example.com"),
            ]
            self.conn.executemany(  # executemany is like a for loop for execute, it runs the same SQL command with different parameters for each tuple in the list
                """
                INSERT INTO student (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, date('now')); -- the question marks are placeholders for the parameters in the tuple
                """,
                default_students,
            )

        if self._table_is_empty("teacher"):
            default_teachers = [
                ("Emily", "Davis", "e.davis@example.com"),
                ("Michael", "Wilson", "m.wilson@example.com"),
                ("Sarah", "Miller", "s.miller@example.com"),
            ]
            self.conn.executemany(
                """
                INSERT INTO teacher (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, date('now'));
                """,
                default_teachers,
            )

        if self._table_is_empty("class"):
            teacher_rows = self.conn.execute(
                "SELECT id, first_name FROM teacher;"
            ).fetchall()
            teacher_ids = {row["first_name"]: row["id"] for row in teacher_rows}
            default_classes = [
                (
                    "Math 101",
                    teacher_ids.get("John") or next(iter(teacher_ids.values()), None),
                ),
                ("Science 101", teacher_ids.get("Emily")),
            ]
            for name, teacher_id in default_classes:
                self.conn.execute(
                    "INSERT INTO class (name, teacher_id) VALUES (?, ?);",
                    (name, teacher_id),
                )

            class_rows = self.conn.execute("SELECT id FROM class;").fetchall()
            student_rows = self.conn.execute("SELECT id FROM student;").fetchall()
            class_student_pairs = [
                (class_row["id"], student_row["id"])
                for class_row in class_rows
                for student_row in student_rows
            ]
            if class_student_pairs:
                self.conn.executemany(
                    "INSERT OR IGNORE INTO class_student (class_id, student_id) VALUES (?, ?);",
                    class_student_pairs,
                )

        if self._table_is_empty("grade"):
            student_rows = self.conn.execute("SELECT id FROM student;").fetchall()
            class_rows = self.conn.execute("SELECT id FROM class;").fetchall()
            grade_rows = []
            for student_row in student_rows:
                for class_row in class_rows:
                    grade_rows.append(
                        (
                            student_row["id"],
                            class_row["id"],
                            random.choice(list(GradeEnum)).value,
                        )
                    )
            if grade_rows:
                self.conn.executemany(
                    """
                    INSERT OR IGNORE INTO grade (student_id, class_id, grade)
                    VALUES (?, ?, ?);
                    """,
                    grade_rows,
                )

        self.conn.commit()

    """
    Below is the basic CRUD operations for students, classes, teachers, and grades, as well as some helper methods.
    """

    # Student Methods
    def get_all_students(self) -> list[Student]:
        """Retrieves all students from the database."""
        cursor = self.conn.execute("SELECT * FROM student;")
        return [Student.from_row(row) for row in cursor.fetchall()]

    def get_student_by_id(self, student_id: int) -> Student | None:
        """Retrieves a student by their ID."""
        cursor = self.conn.execute("SELECT * FROM student WHERE id = ?;", (student_id,))
        row = cursor.fetchone()
        return Student.from_row(row) if row else None

    def add_student(
        self, first_name: str, last_name: str, email: str, date_of_birth: str
    ) -> Student | None:
        """Adds a new student to the database."""
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO student (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, ?);
                """,
                (first_name, last_name, email, date_of_birth),
            )
            self.conn.commit()
            return self.get_student_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return None

    def update_student(
        self,
        student_id: int,
        first_name: str,
        last_name: str,
        email: str,
        date_of_birth: str,
    ) -> tuple[bool, Student | None]:
        """Updates an existing student's information."""
        try:
            self.conn.execute(
                """
                UPDATE student
                SET first_name = ?, last_name = ?, email = ?, date_of_birth = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (first_name, last_name, email, date_of_birth, student_id),
            )
            self.conn.commit()
            return True, self.get_student_by_id(student_id)
        except sqlite3.IntegrityError:
            return False, None

    def delete_student(self, student_id: int) -> bool:
        """Deletes a student from the database."""
        self.conn.execute("DELETE FROM student WHERE id = ?;", (student_id,))
        self.conn.commit()
        return self.get_student_by_id(student_id) is None

    # class methods
    def get_all_classes(self) -> list[Class]:
        """Retrieves all classes from the database."""
        cursor = self.conn.execute("SELECT * FROM class;")
        return [Class.from_row(row) for row in cursor.fetchall()]

    def get_class_by_id(self, class_id: int) -> Class | None:
        """Retrieves a class by its ID."""
        cursor = self.conn.execute("SELECT * FROM class WHERE id = ?;", (class_id,))
        row = cursor.fetchone()
        return Class.from_row(row) if row else None

    def add_class(self, name: str, teacher_id: int | None) -> Class | None:
        """Adds a new class to the database."""
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO class (name, teacher_id)
                VALUES (?, ?);
                """,
                (name, teacher_id),
            )
            self.conn.commit()
            return self.get_class_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            print(f"Failed to add class '{name}' with teacher ID {teacher_id}.")
            return None

    def update_class(
        self, class_id: int, name: str, teacher_id: int | None
    ) -> tuple[bool, Class | None]:
        """Updates an existing class's information."""
        try:
            self.conn.execute(
                """
                UPDATE class
                SET name = ?, teacher_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (name, teacher_id, class_id),
            )
            self.conn.commit()
            return True, self.get_class_by_id(class_id)
        except sqlite3.IntegrityError:
            return False, None

    def delete_class(self, class_id: int) -> bool:
        """Deletes a class from the database."""
        self.conn.execute("DELETE FROM class WHERE id = ?;", (class_id,))
        self.conn.commit()
        return self.get_class_by_id(class_id) is None

    def get_students_by_class_id(self, class_id: int) -> list[Student]:
        """Retrieves all students enrolled in a given class."""
        cursor = self.conn.execute(
            """
            SELECT s.* FROM student s
            JOIN class_student cs ON s.id = cs.student_id
            WHERE cs.class_id = ?;
            """,
            (class_id,),
        )
        return [Student.from_row(row) for row in cursor.fetchall()]

    def get_classes_by_student_id(self, student_id: int) -> list[Class]:
        """Retrieves all classes a student is enrolled in."""
        cursor = self.conn.execute(
            """
            SELECT c.* FROM class c
            JOIN class_student cs ON c.id = cs.class_id
            WHERE cs.student_id = ?
            ORDER BY c.name;
            """,
            (student_id,),
        )
        return [Class.from_row(row) for row in cursor.fetchall()]

    def set_students_for_class(self, class_id: int, student_ids: list[int]) -> bool:
        """Replaces all enrolled students for a class with the provided list."""
        try:
            self.conn.execute(
                "DELETE FROM class_student WHERE class_id = ?;", (class_id,)
            )
            if student_ids:
                self.conn.executemany(
                    "INSERT OR IGNORE INTO class_student (class_id, student_id) VALUES (?, ?);",
                    [(class_id, sid) for sid in student_ids],
                )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Failed to set students for class {class_id}: {e}")
            self.conn.rollback()
            return False

    # Grade Methods
    def get_all_grades(self) -> list[Grade]:
        """Retrieves all class-level grades from the database."""
        cursor = self.conn.execute("SELECT * FROM grade;")
        return [Grade.from_row(row) for row in cursor.fetchall()]

    def get_grade_for_student_in_class(
        self, student_id: int, class_id: int
    ) -> Grade | None:
        """Retrieves the grade for a specific student in a specific class."""
        cursor = self.conn.execute(
            "SELECT * FROM grade WHERE student_id = ? AND class_id = ?;",
            (student_id, class_id),
        )
        row = cursor.fetchone()
        return Grade.from_row(row) if row else None

    def get_grades_for_student(self, student_id: int) -> list[Grade]:
        """Retrieves all class grades for a specific student."""
        cursor = self.conn.execute(
            "SELECT * FROM grade WHERE student_id = ? ORDER BY class_id;",
            (student_id,),
        )
        return [Grade.from_row(row) for row in cursor.fetchall()]

    def set_grade_for_student_in_class(
        self, student_id: int, class_id: int, grade_value: GradeEnum | str
    ) -> tuple[bool, Grade | None]:
        """Creates or updates a student's letter grade for a class."""
        if isinstance(grade_value, GradeEnum):
            normalized_grade = grade_value
        elif isinstance(grade_value, str):
            candidate = grade_value.strip().upper()
            if not candidate:
                return False, None
            try:
                normalized_grade = GradeEnum(candidate)
            except ValueError:
                return False, None
        else:
            return False, None

        enrolled = self.conn.execute(
            "SELECT 1 FROM class_student WHERE class_id = ? AND student_id = ?;",
            (class_id, student_id),
        ).fetchone()
        if enrolled is None:
            return False, None

        try:
            self.conn.execute(
                """
                INSERT INTO grade (student_id, class_id, grade)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, class_id) DO UPDATE SET
                    grade = excluded.grade,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (student_id, class_id, normalized_grade.value),
            )
            self.conn.commit()
            return True, self.get_grade_for_student_in_class(student_id, class_id)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    # Teacher Method
    def get_all_teachers(self) -> list[Teacher]:
        """Retrieves all teachers from the database."""
        cursor = self.conn.execute("SELECT * FROM teacher;")
        return [Teacher.from_row(row) for row in cursor.fetchall()]

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """Retrieves a teacher by their ID."""
        cursor = self.conn.execute("SELECT * FROM teacher WHERE id = ?;", (teacher_id,))
        row = cursor.fetchone()
        return Teacher.from_row(row) if row else None

    def add_teacher(
        self, first_name: str, last_name: str, email: str
    ) -> Teacher | None:
        """Adds a new teacher to the database."""
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO teacher (first_name, last_name, email)
                VALUES (?, ?, ?);
                """,
                (first_name, last_name, email),
            )
            self.conn.commit()
            return self.get_teacher_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return None

    def update_teacher(
        self, teacher_id: int, first_name: str, last_name: str, email: str
    ) -> tuple[bool, Teacher | None]:
        """Updates an existing teacher's information."""
        try:
            self.conn.execute(
                """
                UPDATE teacher
                SET first_name = ?, last_name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (first_name, last_name, email, teacher_id),
            )
            self.conn.commit()
            return True, self.get_teacher_by_id(teacher_id)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    def delete_teacher(self, teacher_id: int) -> bool:
        """Deletes a teacher from the database."""
        self.conn.execute("DELETE FROM teacher WHERE id = ?;", (teacher_id,))
        self.conn.commit()
        return self.get_teacher_by_id(teacher_id) is None
