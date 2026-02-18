from tkinter import ttk
from Utils.Dataclasses import Student
import tkinter as tk
import customtkinter as ctk
import sys


class Students(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
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

        edit_frame = ctk.CTkFrame(self)
        edit_frame.place(relwidth=1, relheight=1)
        self.frames["edit"] = edit_frame

        self.show_frame("list")

    def show_frame(self, name: str):
        self.frames[name].lift()

    def _build_list_frame(self, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Students").pack(pady=(20, 5))

        columns = (
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Date of Birth",
            "Created At",
            "Updated At",
        )
        self.student_listbox = ttk.Treeview(
            frame, columns=columns, show="headings", height=15
        )
        col_widths = {
            "ID": 25,
            "First Name": 120,
            "Last Name": 120,
            "Email": 200,
            "Date of Birth": 110,
            "Created At": 140,
            "Updated At": 140,
        }
        for col in columns:
            self.student_listbox.column(col, anchor=tk.W, width=col_widths[col])
            self.student_listbox.heading(col, text=col, anchor=tk.W)
        self.student_listbox.pack(pady=10, padx=20, fill="both", expand=True)
        menu = tk.Menu(self.student_listbox, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self._show_edit_frame())
        menu.add_command(label="Delete", command=self._delete_student)

        def show_context_menu(event):
            row = self.student_listbox.identify_row(event.y)
            if row:
                self.student_listbox.selection_set(row)
                menu.tk_popup(event.x_root, event.y_root)

        if sys.platform == "darwin":
            self.student_listbox.bind("<Button-2>", show_context_menu)
        else:
            self.student_listbox.bind("<Button-3>", show_context_menu)

        ctk.CTkButton(
            frame, text="Add Student", command=lambda: self.show_frame("add")
        ).pack(pady=10)

        self._refresh_list()

    def _delete_student(self):
        selected = self.student_listbox.selection()
        if not selected:
            return
        student_id = self.student_listbox.item(selected[0])["values"][0]
        self.controller.student_vm.delete_student(student_id)
        self._refresh_list()

    def _refresh_list(self):
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
        ctk.CTkLabel(frame, text="Add Student").pack(pady=(20, 10))

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

        ctk.CTkButton(frame, text="Save", command=self._save_student).pack(pady=5)
        ctk.CTkButton(
            frame, text="Back", fg_color="gray", command=lambda: self.show_frame("list")
        ).pack(pady=5)

    def _show_edit_frame(self):
        selected = self.student_listbox.selection()
        if not selected:
            return
        student_id = self.student_listbox.item(selected[0])["values"][0]
        student = self.controller.student_vm.get_student_by_id(student_id)
        if student:
            frame = self.frames["edit"]
            for widget in frame.winfo_children():
                widget.destroy()
            self._build_edit_frame(student, frame)
            self.show_frame("edit")
        else:
            print("Selected student not found.")

    def _build_edit_frame(self, student: Student, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Edit Student").pack(pady=(20, 10))

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
        selected = self.student_listbox.selection()
        if not selected:
            return
        student_id = self.student_listbox.item(selected[0])["values"][0]
        self.controller.student_vm.update_student(
            student_id,
            self.edit_first_name_entry.get(),
            self.edit_last_name_entry.get(),
            self.edit_email_entry.get(),
            self.edit_dob_entry.get(),
        )
        self.controller.student_vm.students = self.controller.db.get_all_students()
        self._refresh_list()
        self.show_frame("list")

    def _save_student(self):
        student = self.controller.db.add_student(
            self.first_name_entry.get(),
            self.last_name_entry.get(),
            self.email_entry.get(),
            self.dob_entry.get(),
        )
        if student:
            self.controller.student_vm.students = self.controller.db.get_all_students()
            self._refresh_list()
            self.show_frame("list")
        else:
            self.add_error_label.configure(
                text="Failed to add student. Email may already exist."
            )
