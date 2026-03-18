import random
import sqlite3
from Utils.Dataclasses import Student, Class, Teacher, Grade, GradeEnum
from Utils.Validation import (
    ValidationError,
    validate_class_name,
    validate_date_of_birth,
    validate_email,
    validate_optional_positive_int,
    validate_person_name,
    validate_positive_int,
    validate_positive_int_list,
)


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
        self.conn.execute(
            "PRAGMA foreign_keys = ON;"
        )  # Enforces foreign key constraints in SQLite (important for cascading deletes and maintaining referential integrity)
        self._create_tables()
        if seed_defaults:
            self._seed_defaults()

    def _record_exists(self, table_name: str, record_id: int) -> bool:
        """Returns True when the requested table contains a row with the given ID."""
        row = self.conn.execute(
            f"SELECT 1 FROM {table_name} WHERE id = ?;", (record_id,)
        ).fetchone()
        return row is not None

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
        # English translation: "Count the number of rows in the specified table"
        cursor = self.conn.execute(f"SELECT COUNT(*) AS count FROM {table_name};")
        row = cursor.fetchone()
        return row["count"] == 0

    def _seed_defaults(self):
        """Seeds the database with default data if the tables are empty."""
        if self._table_is_empty("admin"):
            # English translation: "Insert a default admin user into the admin table with the specified first name, last name, email, password, and date of birth (which is set to the current date)."
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
            # English translation: "For each tuple in default_students, insert a new record in the student table with the first name, last name, email from the tuple, and date of birth set to the current date."
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
            # English translation: "For each tuple in default_teachers, insert a new record in the teacher table with the first name, last name, email from the tuple, and date of birth set to the current date."
            self.conn.executemany(
                """
                INSERT INTO teacher (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, date('now'));
                """,
                default_teachers,
            )

        if self._table_is_empty("class"):
            # English translation: "Select the id and first_name from all records in teacher table"
            teacher_rows = self.conn.execute(
                "SELECT id, first_name FROM teacher;"
            ).fetchall()
            teacher_ids = {
                row["first_name"]: row["id"] for row in teacher_rows
            }  # creates a dictionary mapping a teacher to their id
            default_classes = [
                (
                    "Math 101",
                    teacher_ids.get("John")
                    or next(
                        iter(teacher_ids.values()), None
                    ),  # assigns the class to John if he exists, otherwise the first teacher, or None if there are no teachers (shouldn't hopefully happen)
                ),
                (
                    "Science 101",
                    teacher_ids.get("Emily"),
                ),  # assigns the class to Emily if she exists, otherwise None (which is allowed since teacher_id is nullable)
            ]
            # English translation: "For each tuple in default_classes, insert a new record in the class table with the name and teacher_id from the tuple."
            self.conn.executemany(
                "INSERT INTO class (name, teacher_id) VALUES (?, ?);",
                default_classes,
            )

            # English translations: "Select the id from all records in the class table" and "Select the id from all records in the student table"
            class_rows = self.conn.execute("SELECT id FROM class;").fetchall()
            student_rows = self.conn.execute("SELECT id FROM student;").fetchall()
            class_student_pairs = [  # Creates a list of tuples containing all possible combinations of class IDs and student IDs
                (class_row["id"], student_row["id"])
                for class_row in class_rows
                for student_row in student_rows
            ]
            if class_student_pairs:
                # English translation: "For each tuple in class_student_pairs, insert a new record in the class_student table with the class_id and student_id from the tuple."
                self.conn.executemany(
                    "INSERT OR IGNORE INTO class_student (class_id, student_id) VALUES (?, ?);",
                    class_student_pairs,
                )

        if self._table_is_empty("grade"):
            # English translation: "Select the id from all records in the student table" and "Select the id from all records in the class table"
            student_rows = self.conn.execute("SELECT id FROM student;").fetchall()
            class_rows = self.conn.execute("SELECT id FROM class;").fetchall()
            grade_rows = []
            for student_row in student_rows:
                for class_row in class_rows:
                    grade_rows.append(  # for each combination of student and class IDs, create a tuple with the student ID, class ID, and a random grade value from the GradeEnum
                        (
                            student_row["id"],
                            class_row["id"],
                            random.choice(list(GradeEnum)).value,
                        )
                    )
            if grade_rows:
                # English translation: "For each tuple in grade_rows, insert a new record in the grade table with the student_id, class_id, and grade from the tuple. If a record with the same student_id and class_id already exists, ignore the insertion."
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
        # English translation: "Select all columns from all records in the student table"
        cursor = self.conn.execute("SELECT * FROM student;")
        return [Student.from_row(row) for row in cursor.fetchall()]

    def get_student_by_id(self, student_id: int) -> Student | None:
        """Retrieves a student by their ID."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
        except ValidationError:
            return None

        # English translation: "Select all columns from the student table where the id matches the provided student_id"
        cursor = self.conn.execute(
            "SELECT * FROM student WHERE id = ?;", (validated_student_id,)
        )
        row = cursor.fetchone()
        return Student.from_row(row) if row else None

    def add_student(
        self, first_name: str, last_name: str, email: str, date_of_birth: str
    ) -> Student | None:
        """Adds a new student to the database."""
        try:
            validated_first_name = validate_person_name(
                first_name, field_name="First name"
            )
            validated_last_name = validate_person_name(
                last_name, field_name="Last name"
            )
            validated_email = validate_email(email)
            validated_date_of_birth = validate_date_of_birth(date_of_birth)
        except ValidationError:
            return None

        try:
            # English translation: "Insert a new record into the student table, with provided first name, last name, email, and date of birth."
            cursor = self.conn.execute(
                """
                INSERT INTO student (first_name, last_name, email, date_of_birth)
                VALUES (?, ?, ?, ?);
                """,
                (
                    validated_first_name,
                    validated_last_name,
                    validated_email,
                    validated_date_of_birth,
                ),
            )
            self.conn.commit()
            return self.get_student_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            self.conn.rollback()
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
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
            validated_first_name = validate_person_name(
                first_name, field_name="First name"
            )
            validated_last_name = validate_person_name(
                last_name, field_name="Last name"
            )
            validated_email = validate_email(email)
            validated_date_of_birth = validate_date_of_birth(date_of_birth)
        except ValidationError:
            return False, None

        try:
            # English translation: "Update the record in the student table where the id matches the provided student_id, setting the first name, last name, email, date of birth to the provided values, and updating the updated_at timestamp to the current time."
            cursor = self.conn.execute(
                """
                UPDATE student
                SET first_name = ?, last_name = ?, email = ?, date_of_birth = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (
                    validated_first_name,
                    validated_last_name,
                    validated_email,
                    validated_date_of_birth,
                    validated_student_id,
                ),
            )
            self.conn.commit()
            if cursor.rowcount == 0:
                return False, None
            return True, self.get_student_by_id(validated_student_id)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    def delete_student(self, student_id: int) -> bool:
        """Deletes a student from the database."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
        except ValidationError:
            return False

        # English translation: "Delete the record from the student table where the id matches the provided student_id."
        cursor = self.conn.execute(
            "DELETE FROM student WHERE id = ?;", (validated_student_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    # class methods
    def get_all_classes(self) -> list[Class]:
        """Retrieves all classes from the database."""
        # English translation: "Select all columns from all records in the class table"
        cursor = self.conn.execute("SELECT * FROM class;")
        return [Class.from_row(row) for row in cursor.fetchall()]

    def get_class_by_id(self, class_id: int) -> Class | None:
        """Retrieves a class by its ID."""
        try:
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
        except ValidationError:
            return None

        # English translation: "Select all columns from the class table where the id matches the provided class_id"
        cursor = self.conn.execute(
            "SELECT * FROM class WHERE id = ?;", (validated_class_id,)
        )
        row = cursor.fetchone()
        return Class.from_row(row) if row else None

    def add_class(self, name: str, teacher_id: int | None) -> Class | None:
        """Adds a new class to the database."""
        try:
            validated_name = validate_class_name(name)
            validated_teacher_id = validate_optional_positive_int(
                teacher_id, field_name="Teacher ID"
            )
        except ValidationError:
            return None

        if validated_teacher_id is not None and not self._record_exists(
            "teacher", validated_teacher_id
        ):
            return None

        try:
            # English translation: "Insert a new record into the class table, with the provided name and teacher_id."
            cursor = self.conn.execute(
                """
                INSERT INTO class (name, teacher_id)
                VALUES (?, ?);
                """,
                (validated_name, validated_teacher_id),
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
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
            validated_name = validate_class_name(name)
            validated_teacher_id = validate_optional_positive_int(
                teacher_id, field_name="Teacher ID"
            )
        except ValidationError:
            return False, None

        if validated_teacher_id is not None and not self._record_exists(
            "teacher", validated_teacher_id
        ):
            return False, None

        try:
            # English translation: "Update the record in the class table where the id matches the provided class_id, setting the name and teacher_id to the provided values, and updating the updated_at timestamp to the current time."
            cursor = self.conn.execute(
                """
                UPDATE class
                SET name = ?, teacher_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (validated_name, validated_teacher_id, validated_class_id),
            )
            self.conn.commit()
            if cursor.rowcount == 0:
                return False, None
            return True, self.get_class_by_id(validated_class_id)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    def delete_class(self, class_id: int) -> bool:
        """Deletes a class from the database."""
        try:
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
        except ValidationError:
            return False

        # English translation: "Delete the record from the class table where the id matches the provided class_id."
        cursor = self.conn.execute(
            "DELETE FROM class WHERE id = ?;", (validated_class_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_students_by_class_id(self, class_id: int) -> list[Student]:
        """Retrieves all students enrolled in a given class."""
        try:
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
        except ValidationError:
            return []

        # English translation: "Select all columns from the student table for records where there is a matching record in the class_student table with the provided class_id and the student_id matches the id of the student."
        cursor = self.conn.execute(
            """
            SELECT s.* FROM student s
            JOIN class_student cs ON s.id = cs.student_id
            WHERE cs.class_id = ?;
            """,
            (validated_class_id,),
        )
        return [Student.from_row(row) for row in cursor.fetchall()]

    def get_classes_by_student_id(self, student_id: int) -> list[Class]:
        """Retrieves all classes a student is enrolled in."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
        except ValidationError:
            return []

        # English translation: "Select all columns from the class table for records where there is a matching record in the class_student table with the provided student_id and the class_id matches the id of the class."
        cursor = self.conn.execute(
            """
            SELECT c.* FROM class c
            JOIN class_student cs ON c.id = cs.class_id
            WHERE cs.student_id = ?
            ORDER BY c.name;
            """,
            (validated_student_id,),
        )
        return [Class.from_row(row) for row in cursor.fetchall()]

    def set_students_for_class(self, class_id: int, student_ids: list[int]) -> bool:
        """Replaces all enrolled students for a class with the provided list."""
        try:
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
            validated_student_ids = validate_positive_int_list(
                student_ids, field_name="Student IDs"
            )
        except ValidationError:
            return False

        if not self._record_exists("class", validated_class_id):
            return False

        if validated_student_ids:
            placeholders = ", ".join("?" for _ in validated_student_ids)
            found_rows = self.conn.execute(
                f"SELECT id FROM student WHERE id IN ({placeholders});",
                tuple(validated_student_ids),
            ).fetchall()
            found_ids = {row["id"] for row in found_rows}
            if len(found_ids) != len(validated_student_ids):
                return False

        try:
            # English translation: "Where the class_id of a class_student record matches the given class_id, delete that record."
            self.conn.execute(
                "DELETE FROM class_student WHERE class_id = ?;", (validated_class_id,)
            )
            if validated_student_ids:
                # English translation: "For each student ID in the provided list, insert a new record into class_student with the provided class_id and student_id. If a record with the same class_id and student_id already exists, ignore the insertion."
                self.conn.executemany(
                    "INSERT OR IGNORE INTO class_student (class_id, student_id) VALUES (?, ?);",
                    [(validated_class_id, sid) for sid in validated_student_ids],
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
        # English translation: "Select all columns from all records in the grade table"
        cursor = self.conn.execute("SELECT * FROM grade;")
        return [Grade.from_row(row) for row in cursor.fetchall()]

    def get_grade_for_student_in_class(
        self, student_id: int, class_id: int
    ) -> Grade | None:
        """Retrieves the grade for a specific student in a specific class."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
        except ValidationError:
            return None

        # English translation: "Select all columns from the grade table where the student_id and class_id match the provided values."
        cursor = self.conn.execute(
            "SELECT * FROM grade WHERE student_id = ? AND class_id = ?;",
            (validated_student_id, validated_class_id),
        )
        row = cursor.fetchone()
        return Grade.from_row(row) if row else None

    def get_grades_for_student(self, student_id: int) -> list[Grade]:
        """Retrieves all class grades for a specific student."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
        except ValidationError:
            return []

        # English translation: "Select all columns from the grade table where the student_id matches the provided value, and order the results by class_id."
        cursor = self.conn.execute(
            "SELECT * FROM grade WHERE student_id = ? ORDER BY class_id;",
            (validated_student_id,),
        )
        return [Grade.from_row(row) for row in cursor.fetchall()]

    def set_grade_for_student_in_class(
        self, student_id: int, class_id: int, grade_value: GradeEnum | str
    ) -> tuple[bool, Grade | None]:
        """Creates or updates a student's letter grade for a class."""
        try:
            validated_student_id = validate_positive_int(
                student_id, field_name="Student ID"
            )
            validated_class_id = validate_positive_int(class_id, field_name="Class ID")
        except ValidationError:
            return False, None

        if isinstance(
            grade_value, GradeEnum
        ):  # if the input is already a GradeEnum, we can just use it directly
            normalized_grade = grade_value
        elif isinstance(
            grade_value, str
        ):  # if the input is a string, try turn it into a GradeEnum
            candidate = grade_value.strip().upper()  # removes whitespace and converts to uppercase to allow for more flexible input (e.g. " a " would be accepted and normalized to "A")
            if not candidate:  # if its empty after stripping whitespace, it's not valid
                return False, None
            try:
                normalized_grade = GradeEnum(
                    candidate
                )  # this will raise a ValueError if the candidate string is not a valid GradeEnum value, which we catch and return False
            except ValueError:
                return False, None
        else:
            return False, None

        # English translation: "Check if there is a record in the class_student table where the class_id and student_id match the provided values."
        enrolled = self.conn.execute(
            "SELECT 1 FROM class_student WHERE class_id = ? AND student_id = ?;",
            (validated_class_id, validated_student_id),
        ).fetchone()
        if enrolled is None:
            return False, None

        try:
            # English translation: "Insert a new record into the grade table with the provided student_id, class_id, and grade. If a record with the same student_id and class_id already exists, update that record's grade and updated_at timestamp to the new values."
            self.conn.execute(
                """
                INSERT INTO grade (student_id, class_id, grade)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, class_id) DO UPDATE SET
                    grade = excluded.grade,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (validated_student_id, validated_class_id, normalized_grade.value),
            )
            self.conn.commit()
            return True, self.get_grade_for_student_in_class(
                validated_student_id, validated_class_id
            )
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    # Teacher Method
    def get_all_teachers(self) -> list[Teacher]:
        """Retrieves all teachers from the database."""
        # English translation: "Select all columns from all records in the teacher table"
        cursor = self.conn.execute("SELECT * FROM teacher;")
        return [Teacher.from_row(row) for row in cursor.fetchall()]

    def get_teacher_by_id(self, teacher_id: int) -> Teacher | None:
        """Retrieves a teacher by their ID."""
        try:
            validated_teacher_id = validate_positive_int(
                teacher_id, field_name="Teacher ID"
            )
        except ValidationError:
            return None

        # English translation: "Select all columns from the teacher table where the id matches the provided value."
        cursor = self.conn.execute(
            "SELECT * FROM teacher WHERE id = ?;", (validated_teacher_id,)
        )
        row = cursor.fetchone()
        return Teacher.from_row(row) if row else None

    def add_teacher(
        self, first_name: str, last_name: str, email: str
    ) -> Teacher | None:
        """Adds a new teacher to the database."""
        try:
            validated_first_name = validate_person_name(
                first_name, field_name="First name"
            )
            validated_last_name = validate_person_name(
                last_name, field_name="Last name"
            )
            validated_email = validate_email(email)
        except ValidationError:
            return None

        try:
            # English translation: "Insert a new record into the teacher table with the provide first name, last name, and email."
            cursor = self.conn.execute(
                """
                INSERT INTO teacher (first_name, last_name, email)
                VALUES (?, ?, ?);
                """,
                (validated_first_name, validated_last_name, validated_email),
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
            validated_teacher_id = validate_positive_int(
                teacher_id, field_name="Teacher ID"
            )
            validated_first_name = validate_person_name(
                first_name, field_name="First name"
            )
            validated_last_name = validate_person_name(
                last_name, field_name="Last name"
            )
            validated_email = validate_email(email)
        except ValidationError:
            return False, None

        try:
            # English translation: "Update the record in the teacher table where the id matches the provided teacher_id, setting the first name, last name, and email to the provided values, and updating the updated_at timestamp to the current time."
            cursor = self.conn.execute(
                """
                UPDATE teacher
                SET first_name = ?, last_name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (
                    validated_first_name,
                    validated_last_name,
                    validated_email,
                    validated_teacher_id,
                ),
            )
            self.conn.commit()
            if cursor.rowcount == 0:
                return False, None
            return True, self.get_teacher_by_id(validated_teacher_id)
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, None

    def delete_teacher(self, teacher_id: int) -> bool:
        """Deletes a teacher from the database."""
        try:
            validated_teacher_id = validate_positive_int(
                teacher_id, field_name="Teacher ID"
            )
        except ValidationError:
            return False

        # English translation: "Delete the record from the teacher table where the id matches the provided teacher_id."
        cursor = self.conn.execute(
            "DELETE FROM teacher WHERE id = ?;", (validated_teacher_id,)
        )
        self.conn.commit()
        return cursor.rowcount > 0
