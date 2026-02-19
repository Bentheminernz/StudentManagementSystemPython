import random
import sqlite3
from Utils.Dataclasses import Student, Class, Teacher


class Database:
    def __init__(self, db_path: str = "app_data.db", seed_defaults: bool = True):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        if seed_defaults:
            self._seed_defaults()

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def _create_tables(self):
        """Creates the necessary tables for the application if they do not already exist."""
        self.conn.executescript("""
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

            CREATE TABLE IF NOT EXISTS assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                information TEXT NOT NULL,
                due_date DATE NOT NULL,
                class_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS grade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                assignment_id INTEGER NOT NULL,
                grade REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
                FOREIGN KEY (assignment_id) REFERENCES assignment(id) ON DELETE CASCADE,
                UNIQUE (student_id, assignment_id)
            );

            CREATE TABLE IF NOT EXISTS class_student (
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                PRIMARY KEY (class_id, student_id),
                FOREIGN KEY (class_id) REFERENCES class(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

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
            self.conn.executemany(
                """
                INSERT INTO student (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, date('now'));
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

        if self._table_is_empty("assignment"):
            class_rows = self.conn.execute("SELECT id, name FROM class;").fetchall()
            class_ids = {row["name"]: row["id"] for row in class_rows}
            assignments = [
                (
                    "Math Homework 1",
                    "Complete exercises 1-10 on page 50",
                    "date('now','+7 days')",
                    class_ids.get("Math 101"),
                ),
                (
                    "Science Project",
                    "Build a model of the solar system",
                    "date('now','+14 days')",
                    class_ids.get("Science 101"),
                ),
            ]
            for title, info, due_date_expr, class_id in assignments:
                self.conn.execute(
                    f"INSERT INTO assignment (title, information, due_date, class_id) VALUES (?, ?, {due_date_expr}, ?);",
                    (title, info, class_id),
                )

        if self._table_is_empty("grade"):
            student_rows = self.conn.execute("SELECT id FROM student;").fetchall()
            assignment_rows = self.conn.execute("SELECT id FROM assignment;").fetchall()
            grade_rows = []
            for student_row in student_rows:
                for assignment_row in assignment_rows:
                    grade_rows.append(
                        (
                            student_row["id"],
                            assignment_row["id"],
                            round(random.uniform(60, 100), 2),
                        )
                    )
            if grade_rows:
                self.conn.executemany(
                    """
                    INSERT OR IGNORE INTO grade (student_id, assignment_id, grade)
                    VALUES (?, ?, ?);
                    """,
                    grade_rows,
                )

        self.conn.commit()

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

    def add_class(self, name: str, teacher_id: int) -> Class | None:
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
        self, class_id: int, name: str, teacher_id: int
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
            return False, None

    def delete_teacher(self, teacher_id: int) -> bool:
        """Deletes a teacher from the database."""
        self.conn.execute("DELETE FROM teacher WHERE id = ?;", (teacher_id,))
        self.conn.commit()
        return self.get_teacher_by_id(teacher_id) is None
