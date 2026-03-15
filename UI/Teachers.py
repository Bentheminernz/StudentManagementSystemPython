from tkinter import ttk
from Utils.Dataclasses import Teacher
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
            self.teacher_listbox.delete(item)

        for teacher in self.controller.teacher_vm.teachers:
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
        selected = self.teacher_listbox.selection()
        if not selected:
            return
        teacher_id = self.teacher_listbox.item(selected[0])["values"][0]
        self._delete_teacher_by_id(teacher_id)

    def _delete_teacher_by_id(self, teacher_id: int):
        """Deletes a teacher by ID and refreshes dependent teacher/class state."""
        self.controller.teacher_vm.delete_teacher(teacher_id)
        self.controller.teacher_vm.load_teachers()
        self.controller.class_vm.load_classes()

        if getattr(self, "_editing_teacher_id", None) == teacher_id:
            self._editing_teacher_id = None

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
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not first_name or not last_name or not email:
            self.add_error_label.configure(
                text="First name, last name, and email are required."
            )
            return

        teacher = self.controller.db.add_teacher(first_name, last_name, email)
        if teacher:
            self.add_error_label.configure(text="")
            self.first_name_entry.delete(0, "end")
            self.last_name_entry.delete(0, "end")
            self.email_entry.delete(0, "end")

            self.controller.teacher_vm.load_teachers()
            self._refresh_list()
            self.show_frame("list")
        else:
            self.add_error_label.configure(
                text="Failed to add teacher. Email may already exist."
            )

    def _show_edit_frame(self):
        """Shows the edit form for the currently selected teacher."""
        selected = self.teacher_listbox.selection()
        if not selected:
            return
        teacher_id = self.teacher_listbox.item(selected[0])["values"][0]
        self._show_edit_frame_for_teacher(teacher_id)

    def _show_edit_frame_for_teacher(self, teacher_id: int):
        """Shows edit form for a specific teacher ID."""
        teacher = self.controller.teacher_vm.get_teacher_by_id(teacher_id)
        if teacher:
            self._editing_teacher_id = teacher_id
            frame = self.frames["edit"]
            for widget in frame.winfo_children():
                widget.destroy()
            self._build_edit_frame(teacher, frame)
            self.show_frame("edit")
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
        teacher_id = getattr(self, "_editing_teacher_id", None)
        if teacher_id is None:
            selected = self.teacher_listbox.selection()
            if not selected:
                return
            teacher_id = self.teacher_listbox.item(selected[0])["values"][0]

        first_name = self.edit_first_name_entry.get().strip()
        last_name = self.edit_last_name_entry.get().strip()
        email = self.edit_email_entry.get().strip()

        if not first_name or not last_name or not email:
            self.edit_error_label.configure(
                text="First name, last name, and email are required."
            )
            return

        success, _teacher = self.controller.db.update_teacher(
            teacher_id,
            first_name,
            last_name,
            email,
        )
        if success:
            self.edit_error_label.configure(text="")
            self.controller.teacher_vm.load_teachers()
            self._refresh_list()
            self.show_frame("list")
        else:
            self.edit_error_label.configure(
                text="Failed to update teacher. Email may already exist."
            )

    def _on_double_click(self, event):
        """Shows a teacher detail view when a list row is double-clicked."""
        row = self.teacher_listbox.identify_row(event.y)
        if not row:
            return

        self.teacher_listbox.selection_set(row)
        teacher_id = self.teacher_listbox.item(row)["values"][0]
        teacher = self.controller.teacher_vm.get_teacher_by_id(teacher_id)
        if not teacher:
            return

        frame = self.frames["detail"]
        for widget in frame.winfo_children():
            widget.destroy()
        self._build_detail_frame(teacher, frame)
        self.show_frame("detail")

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
        for col in columns:
            class_list.column(col, anchor=tk.W, width=col_widths[col])
            class_list.heading(col, text=col, anchor=tk.W)
        class_list.pack(pady=5, padx=20, fill="both", expand=True)

        self.controller.class_vm.load_classes()
        taught_classes = [
            cls
            for cls in self.controller.class_vm.classes
            if cls.teacher_id == teacher.id
        ]

        for taught_class in taught_classes:
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
