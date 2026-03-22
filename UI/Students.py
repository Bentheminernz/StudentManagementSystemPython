from tkinter import ttk
from Utils.Dataclasses import Student
from Utils.Validation import (
    ValidationError,
    validate_date_of_birth,
    validate_email,
    validate_person_name,
)
import tkinter as tk
import customtkinter as ctk
import sys


"""
The Students frame is responsible for displaying the list of students, and allowing the user to add, edit, and delete students.
It also allows the user to view the details of a student, including their enrolled classes and grades
"""


class Students(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        """Initializes the Students frame, creates the list and add frames, and sets up the context menu for editing and deleting students."""
        super().__init__(parent)
        self.controller = controller
        self.frames: dict[str, ctk.CTkFrame] = {}

        for name, builder in (
            ("list", self._build_list_frame),
            ("add", self._build_add_frame),
        ):
            frame = ctk.CTkFrame(self)
            frame.place(relwidth=1, relheight=1)
            builder(frame)
            self.frames[name] = frame

        for name in ("edit", "detail"):
            frame = ctk.CTkFrame(self)
            frame.place(relwidth=1, relheight=1)
            self.frames[name] = frame

        self.show_frame("list")

    def show_frame(self, name: str):
        """Brings the specified frame to the front to make it visible."""
        self.frames[name].lift()

    def _validate_student_inputs(
        self, first_name: str, last_name: str, email: str, date_of_birth: str
    ) -> tuple[str, str, str, str]:
        """Normalizes and validates add/edit student form inputs."""
        validated_first_name = validate_person_name(first_name, field_name="First name")
        validated_last_name = validate_person_name(last_name, field_name="Last name")
        validated_email = validate_email(email)
        validated_date_of_birth = validate_date_of_birth(date_of_birth)
        return (
            validated_first_name,
            validated_last_name,
            validated_email,
            validated_date_of_birth,
        )

    def _build_list_frame(self, frame: ctk.CTkFrame):
        """Builds the list frame, which displays the list of students and allows the user to add, edit, and delete students."""
        ctk.CTkLabel(frame, text="Students").pack(pady=(20, 5))

        columns = (  # The columns for the student list
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Date of Birth",
            "Created At",
            "Updated At",
        )
        # creates the treeview for student list from columns above
        self.student_listbox = ttk.Treeview(
            frame, columns=columns, show="headings", height=15
        )
        col_widths = {  # predefined widths for each column to make it look nicer
            "ID": 25,
            "First Name": 120,
            "Last Name": 120,
            "Email": 200,
            "Date of Birth": 110,
            "Created At": 140,
            "Updated At": 140,
        }

        # for each column, set the width and heading text
        for col in columns:
            self.student_listbox.column(col, anchor=tk.W, width=col_widths[col])
            self.student_listbox.heading(col, text=col, anchor=tk.W)
        self.student_listbox.pack(pady=10, padx=20, fill="both", expand=True)

        # creates the context menu for editing and deleting students
        menu = tk.Menu(self.student_listbox, tearoff=0)

        # adds the commands
        menu.add_command(label="Edit", command=lambda: self._show_edit_frame())
        menu.add_command(label="Delete", command=self._delete_student)

        def show_context_menu(event):
            """Shows the context menu when the user right clicks on a student in the list."""
            row = self.student_listbox.identify_row(event.y)
            if row:
                self.student_listbox.selection_set(row)
                menu.tk_popup(event.x_root, event.y_root)

        # On Darwin (macOS), the right click is Button-2, on Windows it's Button-3, (hopefully this works on Linux too)
        if sys.platform == "darwin":
            self.student_listbox.bind("<Button-2>", show_context_menu)
            self.student_listbox.bind(
                "<Control-Button-1>", show_context_menu
            )  # also bind ctrl+click for right-click on macOS
        else:
            self.student_listbox.bind("<Button-3>", show_context_menu)

        self.student_listbox.bind("<Double-1>", self._on_double_click)

        # button that shows add student frame
        ctk.CTkButton(
            frame, text="Add Student", command=lambda: self.show_frame("add")
        ).pack(pady=10)

        # refresh the student list to show the current students in the database
        self._refresh_list()

    def _delete_student(self):
        """Deletes the selected student from the database and refreshes the list."""
        selected = self.student_listbox.selection()
        if not selected:
            return
        student_id = self.student_listbox.item(selected[0])["values"][0]
        self._delete_student_by_id(student_id)

    def _delete_student_by_id(self, student_id: int):
        """Deletes the student with the specified ID from the database and refreshes the list."""
        self.controller.student_vm.delete_student(student_id)
        if getattr(self, "_editing_student_id", None) == student_id:
            self._editing_student_id = None
        self._refresh_list()
        self.show_frame("list")

    def _refresh_list(self):
        """Refreshes the student list by clearing the current list and repopulating it with the students from the database."""
        for item in self.student_listbox.get_children():
            self.student_listbox.delete(item)

        for student in self.controller.student_vm.students:
            self.student_listbox.insert(
                "",
                "end",
                values=(
                    student.id,
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.date_of_birth,
                    student.created_at,
                    student.updated_at,
                ),
            )

    def _build_add_frame(self, frame: ctk.CTkFrame):
        """builds the add student frame, which allows the user to enter the details for a new student and save it to the database."""
        ctk.CTkLabel(frame, text="Add Student").pack(pady=(20, 10))

        # creates the entry fields for the student details
        self.first_name_entry = ctk.CTkEntry(frame, placeholder_text="First Name")
        self.first_name_entry.pack(pady=5, padx=20, fill="x")

        self.last_name_entry = ctk.CTkEntry(frame, placeholder_text="Last Name")
        self.last_name_entry.pack(pady=5, padx=20, fill="x")

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email")
        self.email_entry.pack(pady=5, padx=20, fill="x")

        self.dob_entry = ctk.CTkEntry(
            frame, placeholder_text="Date of Birth (YYYY-MM-DD)"
        )
        self.dob_entry.pack(pady=5, padx=20, fill="x")

        self.add_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.add_error_label.pack(pady=5)

        # button to save the new student to the database
        ctk.CTkButton(frame, text="Save", command=self._save_student).pack(pady=5)
        ctk.CTkButton(
            frame, text="Back", fg_color="gray", command=lambda: self.show_frame("list")
        ).pack(pady=5)

    def _show_edit_frame(self):
        """Shows the edit student frame for the selected student, allowing the user to edit the student's details and save the changes to the database."""
        selected = self.student_listbox.selection()
        if not selected:
            return
        student_id = self.student_listbox.item(selected[0])["values"][0]
        self._show_edit_frame_for_student(student_id)

    def _show_edit_frame_for_student(self, student_id: int):
        """Shows the edit student frame for the specified student ID, allowing the user to edit the student's details and save the changes to the database."""
        student = self.controller.student_vm.get_student_by_id(student_id)
        if student:
            self._editing_student_id = student_id
            frame = self.frames["edit"]
            for widget in frame.winfo_children():
                widget.destroy()
            self._build_edit_frame(student, frame)
            self.show_frame("edit")
        else:
            print("Selected student not found.")

    def _on_double_click(self, event):
        """Handles the double click event on a student in the list, showing the detail frame for the selected student."""
        row = self.student_listbox.identify_row(event.y)
        if not row:
            return
        self.student_listbox.selection_set(row)
        student_id = self.student_listbox.item(row)["values"][0]

        student = self.controller.student_vm.get_student_by_id(student_id)
        if not student:
            return

        frame = self.frames["detail"]
        for widget in frame.winfo_children():
            widget.destroy()
        self._build_detail_frame(student, frame)
        self.show_frame("detail")

    def _build_detail_frame(self, student: Student, frame: ctk.CTkFrame):
        """Builds the detail frame for a student, showing their details, enrolled classes, and grades."""
        # creates labels for the student details at the top of the frame
        ctk.CTkLabel(
            frame,
            text=student.name(),
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 2))
        ctk.CTkLabel(frame, text=f"Student ID: {student.id}").pack(pady=(0, 2))
        ctk.CTkLabel(frame, text=f"Email: {student.email}").pack(pady=(0, 2))
        ctk.CTkLabel(frame, text=f"Date of Birth: {student.date_of_birth}").pack(
            pady=(0, 2)
        )
        ctk.CTkLabel(
            frame,
            text=f"Created: {student.created_at}  |  Updated: {student.updated_at}",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Enrolled Classes and Grades").pack(pady=(5, 2))

        # creates a treeview to show the enrolled classes and grades for the student
        columns = ("Class ID", "Class", "Teacher", "Grade")
        class_list = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        col_widths = {
            "Class ID": 60,
            "Class": 180,
            "Teacher": 180,
            "Grade": 70,
        }
        for col in columns:
            class_list.column(col, anchor=tk.W, width=col_widths[col])
            class_list.heading(col, text=col, anchor=tk.W)
        class_list.pack(pady=5, padx=20, fill="both", expand=True)

        # for each class the student is enrolled in, get the teacher and grade, and add it to the treeview
        enrolled_classes = self.controller.db.get_classes_by_student_id(student.id)
        for enrolled_class in enrolled_classes:
            teacher = self.controller.teacher_vm.get_teacher_by_id(
                enrolled_class.teacher_id
            )
            grade = self.controller.db.get_grade_for_student_in_class(
                student.id, enrolled_class.id
            )
            class_list.insert(
                "",
                "end",
                values=(
                    enrolled_class.id,
                    enrolled_class.name,
                    teacher.name() if teacher else "None",
                    grade.grade.value if grade else "",
                ),
            )

        # if the student is not enrolled in any classes, show a message indicating that
        if not enrolled_classes:
            ctk.CTkLabel(
                frame,
                text="This student is not enrolled in any classes.",
                text_color="gray",
            ).pack(pady=(0, 5))

        # creates a row of buttons for editing, deleting, and going back to the list
        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.pack(pady=10)

        ctk.CTkButton(
            button_row,
            text="Edit Student",
            command=lambda sid=student.id: self._show_edit_frame_for_student(sid),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="Delete Student",
            fg_color="#c0392b",
            hover_color="#a93226",
            command=lambda sid=student.id: self._delete_student_by_id(sid),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(side="left", padx=5)

    def _build_edit_frame(self, student: Student, frame: ctk.CTkFrame):
        """Builds the edit student frame, which allows the user to edit the details of a student and save the changes to the database."""
        ctk.CTkLabel(frame, text="Edit Student").pack(pady=(20, 10))

        # creates the entry fields for the student details, and pre-populates them with the current details of the student
        self.edit_first_name_entry = ctk.CTkEntry(frame, placeholder_text="First Name")
        self.edit_first_name_entry.pack(pady=5, padx=20, fill="x")

        self.edit_last_name_entry = ctk.CTkEntry(frame, placeholder_text="Last Name")
        self.edit_last_name_entry.pack(pady=5, padx=20, fill="x")

        self.edit_email_entry = ctk.CTkEntry(frame, placeholder_text="Email")
        self.edit_email_entry.pack(pady=5, padx=20, fill="x")

        self.edit_dob_entry = ctk.CTkEntry(
            frame, placeholder_text="Date of Birth (YYYY-MM-DD)"
        )
        self.edit_dob_entry.pack(pady=5, padx=20, fill="x")

        self.edit_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.edit_error_label.pack(pady=5)

        self.edit_first_name_entry.insert(0, student.first_name)
        self.edit_last_name_entry.insert(0, student.last_name)
        self.edit_email_entry.insert(0, student.email)
        self.edit_dob_entry.insert(0, student.date_of_birth)

        ctk.CTkButton(frame, text="Save", command=self._update_student).pack(pady=5)
        ctk.CTkButton(
            frame, text="Back", fg_color="gray", command=lambda: self.show_frame("list")
        ).pack(pady=5)

    def _update_student(self):
        """Updates the student in the database with the details entered in the edit frame, and refreshes the list to show the updated details."""
        student_id = getattr(self, "_editing_student_id", None)
        if student_id is None:
            selected = self.student_listbox.selection()

            if not selected:
                return
            student_id = self.student_listbox.item(selected[0])["values"][0]

        try:
            first_name, last_name, email, date_of_birth = self._validate_student_inputs(
                self.edit_first_name_entry.get(),
                self.edit_last_name_entry.get(),
                self.edit_email_entry.get(),
                self.edit_dob_entry.get(),
            )
        except ValidationError as exc:
            self.edit_error_label.configure(text=str(exc))
            return

        success, _student = self.controller.db.update_student(
            student_id, first_name, last_name, email, date_of_birth
        )
        if success:
            self.edit_error_label.configure(text="")
            self.controller.student_vm.students = self.controller.db.get_all_students()
            self._refresh_list()
            self.show_frame("list")
        else:
            self.edit_error_label.configure(
                text="Failed to update student. Email may already exist."
            )

    def _save_student(self):
        """Saves the new student to the database with the details entered in the add frame, and refreshes the list to show the new student."""
        try:
            first_name, last_name, email, date_of_birth = self._validate_student_inputs(
                self.first_name_entry.get(),
                self.last_name_entry.get(),
                self.email_entry.get(),
                self.dob_entry.get(),
            )
        except ValidationError as exc:
            self.add_error_label.configure(text=str(exc))
            return

        student = self.controller.db.add_student(
            first_name,
            last_name,
            email,
            date_of_birth,
        )
        if student:
            self.add_error_label.configure(text="")
            self.first_name_entry.delete(0, "end")
            self.last_name_entry.delete(0, "end")
            self.email_entry.delete(0, "end")
            self.dob_entry.delete(0, "end")
            self.controller.student_vm.students = self.controller.db.get_all_students()
            self._refresh_list()
            self.show_frame("list")
        else:
            self.add_error_label.configure(
                text="Email is already registered. Please use a different email."
            )
