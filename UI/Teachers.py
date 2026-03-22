from tkinter import ttk
from Utils.Dataclasses import Teacher
from Utils.Validation import ValidationError, validate_email, validate_person_name
import tkinter as tk
import customtkinter as ctk
import sys


"""
The Teachers frame is responsible for displaying the list of teachers,
allowing CRUD operations, and showing classes taught by a selected teacher.
"""


class Teachers(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        """Initializes the Teachers frame and sets up sub-frames."""
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

    def on_show(self):
        """Refreshes teacher data whenever this page is displayed."""
        self.controller.teacher_vm.load_teachers()
        self._refresh_list()

    def _validate_teacher_inputs(
        self, first_name: str, last_name: str, email: str
    ) -> tuple[str, str, str]:
        """Normalizes and validates add/edit teacher form inputs."""
        validated_first_name = validate_person_name(first_name, field_name="First name")
        validated_last_name = validate_person_name(last_name, field_name="Last name")
        validated_email = validate_email(email)
        return validated_first_name, validated_last_name, validated_email

    def _build_list_frame(self, frame: ctk.CTkFrame):
        """Builds the list frame with teacher records and context actions."""
        ctk.CTkLabel(frame, text="Teachers").pack(pady=(20, 5))

        columns = (
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Created At",
            "Updated At",
        )
        self.teacher_listbox = ttk.Treeview(
            frame, columns=columns, show="headings", height=15
        )
        col_widths = {
            "ID": 25,
            "First Name": 120,
            "Last Name": 120,
            "Email": 240,
            "Created At": 140,
            "Updated At": 140,
        }

        for col in columns:
            self.teacher_listbox.column(col, anchor=tk.W, width=col_widths[col])
            self.teacher_listbox.heading(col, text=col, anchor=tk.W)
        self.teacher_listbox.pack(pady=10, padx=20, fill="both", expand=True)

        menu = tk.Menu(self.teacher_listbox, tearoff=0)
        menu.add_command(label="Edit", command=self._show_edit_frame)
        menu.add_command(label="Delete", command=self._delete_teacher)

        def show_context_menu(event):
            """Shows the context menu when the user right-clicks on a teacher."""
            row = self.teacher_listbox.identify_row(event.y)
            if row:
                self.teacher_listbox.selection_set(row)
                menu.tk_popup(event.x_root, event.y_root)

        # Darwin (macOS) uses Button-2 for right-click, while Windows/Linux use Button-3.
        if sys.platform == "darwin":
            self.teacher_listbox.bind("<Button-2>", show_context_menu)
            self.teacher_listbox.bind(
                "<Control-Button-1>", show_context_menu
            )  # Also bind Ctrl+Click for macOS right-click
        else:
            self.teacher_listbox.bind("<Button-3>", show_context_menu)

        self.teacher_listbox.bind("<Double-1>", self._on_double_click)

        ctk.CTkButton(
            frame, text="Add Teacher", command=lambda: self.show_frame("add")
        ).pack(pady=10)

        self._refresh_list()

    def _refresh_list(self):
        """Refreshes the teacher list from the in-memory teacher view model state."""
        for item in self.teacher_listbox.get_children():
            self.teacher_listbox.delete(
                item
            )  # clear existing list items before repopulating to avoid duplicates

        for teacher in self.controller.teacher_vm.teachers:  # for teacher in the teacher view model's teacher list, insert a new row into the listbox with that teacher's data
            self.teacher_listbox.insert(
                "",
                "end",
                values=(
                    teacher.id,
                    teacher.first_name,
                    teacher.last_name,
                    teacher.email,
                    teacher.created_at,
                    teacher.updated_at,
                ),
            )

    def _delete_teacher(self):
        """Deletes the selected teacher and returns to the list view."""
        selected = (
            self.teacher_listbox.selection()
        )  # gets currently selected teacher in the list
        if not selected:
            return
        teacher_id = self.teacher_listbox.item(selected[0])["values"][
            0
        ]  # get the id of the selected teacher
        self._delete_teacher_by_id(
            teacher_id
        )  # and delete the teacher by id, which also refreshes the list and class state and returns to the list view

    def _delete_teacher_by_id(self, teacher_id: int):
        """Deletes a teacher by ID and refreshes dependent teacher/class state."""
        self.controller.teacher_vm.delete_teacher(teacher_id)
        self.controller.teacher_vm.load_teachers()
        self.controller.class_vm.load_classes()

        if (
            getattr(self, "_editing_teacher_id", None) == teacher_id
        ):  # if currently editing teacher is the one that was just deleted, clear the editing teacher id from the instance to avoid stale reference
            self._editing_teacher_id = None

        # refresh and back to list
        self._refresh_list()
        self.show_frame("list")

    def _build_add_frame(self, frame: ctk.CTkFrame):
        """Builds the add teacher form."""
        ctk.CTkLabel(frame, text="Add Teacher").pack(pady=(20, 10))

        self.first_name_entry = ctk.CTkEntry(frame, placeholder_text="First Name")
        self.first_name_entry.pack(pady=5, padx=20, fill="x")

        self.last_name_entry = ctk.CTkEntry(frame, placeholder_text="Last Name")
        self.last_name_entry.pack(pady=5, padx=20, fill="x")

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email")
        self.email_entry.pack(pady=5, padx=20, fill="x")

        self.add_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.add_error_label.pack(pady=5)

        ctk.CTkButton(frame, text="Save", command=self._save_teacher).pack(pady=5)
        ctk.CTkButton(
            frame, text="Back", fg_color="gray", command=lambda: self.show_frame("list")
        ).pack(pady=5)

    def _save_teacher(self):
        """Saves a new teacher and refreshes list state on success."""
        try:
            first_name, last_name, email = (
                self._validate_teacher_inputs(  # validates the form inputs
                    self.first_name_entry.get(),
                    self.last_name_entry.get(),
                    self.email_entry.get(),
                )
            )
        except ValidationError as exc:
            self.add_error_label.configure(
                text=str(exc)
            )  # if there is a validation error, show it in the form
            return

        teacher = self.controller.db.add_teacher(
            first_name, last_name, email
        )  # attempt to add the teacher to the db
        if teacher:  # if added successfully, clear the form and refresh the list
            self.add_error_label.configure(text="")
            self.first_name_entry.delete(0, "end")
            self.last_name_entry.delete(0, "end")
            self.email_entry.delete(0, "end")

            self.controller.teacher_vm.load_teachers()
            self._refresh_list()
            self.show_frame("list")
        else:
            # otherwise show an error (hardcoded email uniqueness constraint error since that's the only failure case for add_teacher)
            self.add_error_label.configure(
                text="Failed to add teacher. Email may already exist."
            )

    def _show_edit_frame(self):
        """Shows the edit form for the currently selected teacher."""
        selected = (
            self.teacher_listbox.selection()
        )  # gets currently selected teacher in the list
        if not selected:
            return  # if not selection, do nothing
        teacher_id = self.teacher_listbox.item(selected[0])["values"][
            0
        ]  # otherwise get the id of the selected teacher
        self._show_edit_frame_for_teacher(
            teacher_id
        )  # and show the edit form for that teacher id

    def _show_edit_frame_for_teacher(self, teacher_id: int):
        """Shows edit form for a specific teacher ID."""
        teacher = self.controller.teacher_vm.get_teacher_by_id(
            teacher_id
        )  # get the teacher object for the specified id
        if teacher:
            self._editing_teacher_id = teacher_id  # store the currently editing teacher id in the instance for reference when saving edits
            frame = self.frames["edit"]  # get the edit frame
            for widget in frame.winfo_children():  # clear the edit frame of any existing widgets (important when editing multiple teachers in a row to avoid widget stacking)
                widget.destroy()
            self._build_edit_frame(
                teacher, frame
            )  # build the edit form for the specified teacher
            self.show_frame("edit")  # show the edit frame
        else:
            print("Selected teacher not found.")

    def _build_edit_frame(self, teacher: Teacher, frame: ctk.CTkFrame):
        """Builds the edit teacher form prefilled with teacher values."""
        ctk.CTkLabel(frame, text="Edit Teacher").pack(pady=(20, 10))

        self.edit_first_name_entry = ctk.CTkEntry(frame, placeholder_text="First Name")
        self.edit_first_name_entry.pack(pady=5, padx=20, fill="x")

        self.edit_last_name_entry = ctk.CTkEntry(frame, placeholder_text="Last Name")
        self.edit_last_name_entry.pack(pady=5, padx=20, fill="x")

        self.edit_email_entry = ctk.CTkEntry(frame, placeholder_text="Email")
        self.edit_email_entry.pack(pady=5, padx=20, fill="x")

        self.edit_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.edit_error_label.pack(pady=5)

        self.edit_first_name_entry.insert(0, teacher.first_name)
        self.edit_last_name_entry.insert(0, teacher.last_name)
        self.edit_email_entry.insert(0, teacher.email)

        ctk.CTkButton(frame, text="Save", command=self._update_teacher).pack(pady=5)
        ctk.CTkButton(
            frame, text="Back", fg_color="gray", command=lambda: self.show_frame("list")
        ).pack(pady=5)

    def _update_teacher(self):
        """Updates the selected teacher and refreshes dependent state on success."""
        teacher_id = getattr(
            self, "_editing_teacher_id", None
        )  # get the currently editing teacher id from the instance (set when opening the edit form)
        if teacher_id is None:  # if no teacher id
            selected = (
                self.teacher_listbox.selection()
            )  # attempt to get selected teacher
            if not selected:
                return  # do nothing if no selection
            teacher_id = self.teacher_listbox.item(
                selected[0]
            )[
                "values"
            ][
                0
            ]  # otherwise get the teacher id from the selected teacher in the list as a fallback

        try:
            first_name, last_name, email = (
                self._validate_teacher_inputs(  # validate the form inputs
                    self.edit_first_name_entry.get(),
                    self.edit_last_name_entry.get(),
                    self.edit_email_entry.get(),
                )
            )
        except ValidationError as exc:
            # if there is a validation error, show it in the form and do not attempt to update the teacher
            self.edit_error_label.configure(text=str(exc))
            return

        success, _teacher = (
            self.controller.db.update_teacher(  # attempt to update the teacher in the db with the new values
                teacher_id,
                first_name,
                last_name,
                email,
            )
        )
        if success:
            self.edit_error_label.configure(
                text=""
            )  # if update successful, clear any existing error message in the form
            self.controller.teacher_vm.load_teachers()  # load the updated teacher list into the teacher view model
            self._refresh_list()  # refresh the teacher list in the list frame to reflect any changes from the update
            self.show_frame("list")  # return to the list frame
        else:
            # if update failed, show an error (hardcoded email uniqueness constraint error since that's the only failure case for update_teacher)
            self.edit_error_label.configure(
                text="Failed to update teacher. Email may already exist."
            )

    def _on_double_click(self, event):
        """Shows a teacher detail view when a list row is double-clicked."""
        row = self.teacher_listbox.identify_row(
            event.y
        )  # get the row that was double-clicked
        if not row:
            return  # if no row identified, do nothing

        self.teacher_listbox.selection_set(
            row
        )  # set the selected row in the listbox to the double-clicked row
        teacher_id = self.teacher_listbox.item(row)["values"][
            0
        ]  # get the teacher id from the selected row's values
        teacher = self.controller.teacher_vm.get_teacher_by_id(
            teacher_id
        )  # get the teacher object for the specified id
        if not teacher:
            return  # if no teacher found for the id, do nothing

        frame = self.frames["detail"]  # get the detail frame
        for (
            widget
        ) in frame.winfo_children():  # clear the detail frame of any existing widgets
            widget.destroy()
        self._build_detail_frame(
            teacher, frame
        )  # build the teacher detail view for the specified teacher
        self.show_frame("detail")  # show the detail frame

    def _build_detail_frame(self, teacher: Teacher, frame: ctk.CTkFrame):
        """Builds teacher detail view, including classes taught by that teacher."""
        ctk.CTkLabel(
            frame,
            text=teacher.name(),
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 2))
        ctk.CTkLabel(frame, text=f"Teacher ID: {teacher.id}").pack(pady=(0, 2))
        ctk.CTkLabel(frame, text=f"Email: {teacher.email}").pack(pady=(0, 2))
        ctk.CTkLabel(
            frame,
            text=f"Date of Birth: {teacher.date_of_birth if teacher.date_of_birth else 'N/A'}",
        ).pack(pady=(0, 2))
        ctk.CTkLabel(
            frame,
            text=f"Created: {teacher.created_at}  |  Updated: {teacher.updated_at}",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Classes Taught").pack(pady=(5, 2))

        columns = ("Class ID", "Class Name", "Students", "Updated At")
        class_list = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        col_widths = {
            "Class ID": 70,
            "Class Name": 220,
            "Students": 80,
            "Updated At": 180,
        }
        for col in columns:  # for column in columns, set the column width and heading text for the class list treeview
            class_list.column(col, anchor=tk.W, width=col_widths[col])
            class_list.heading(col, text=col, anchor=tk.W)
        class_list.pack(pady=5, padx=20, fill="both", expand=True)

        self.controller.class_vm.load_classes()
        taught_classes = [  # for each class, filter to only include classes where the teacher_id matches the current teacher's id to get the list of classes taught by this teacher
            cls
            for cls in self.controller.class_vm.classes
            if cls.teacher_id == teacher.id
        ]

        for taught_class in taught_classes:  # for each class taught by this teacher, get the count of students in that class and insert a new row into the class list treeview with the class data
            student_count = len(
                self.controller.db.get_students_by_class_id(taught_class.id)
            )
            class_list.insert(
                "",
                "end",
                values=(
                    taught_class.id,
                    taught_class.name,
                    student_count,
                    taught_class.updated_at,
                ),
            )

        if not taught_classes:
            ctk.CTkLabel(
                frame,
                text="This teacher is not assigned to any classes.",
                text_color="gray",
            ).pack(pady=(0, 5))

        button_row = ctk.CTkFrame(frame, fg_color="transparent")
        button_row.pack(pady=10)

        ctk.CTkButton(
            button_row,
            text="Edit Teacher",
            command=lambda tid=teacher.id: self._show_edit_frame_for_teacher(tid),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="Delete Teacher",
            fg_color="#c0392b",
            hover_color="#a93226",
            command=lambda tid=teacher.id: self._delete_teacher_by_id(tid),
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(side="left", padx=5)
