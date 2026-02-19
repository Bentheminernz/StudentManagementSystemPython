from tkinter import ttk
from Utils.Dataclasses import Class
import tkinter as tk
import customtkinter as ctk
import sys


class Classes(ctk.CTkFrame):
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

        for name in ("edit", "detail"):
            frame = ctk.CTkFrame(self)
            frame.place(relwidth=1, relheight=1)
            self.frames[name] = frame

        self.show_frame("list")

    def show_frame(self, name: str):
        self.frames[name].lift()

    # ------------------------------------------------------------------ list --

    def _build_list_frame(self, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Classes").pack(pady=(20, 5))

        columns = ("ID", "Name", "Teacher", "Created At", "Updated At")
        self.class_listbox = ttk.Treeview(
            frame, columns=columns, show="headings", height=15
        )
        col_widths = {
            "ID": 25,
            "Name": 150,
            "Teacher": 150,
            "Created At": 140,
            "Updated At": 140,
        }
        for col in columns:
            self.class_listbox.column(col, anchor=tk.W, width=col_widths[col])
            self.class_listbox.heading(col, text=col, anchor=tk.W)
        self.class_listbox.pack(pady=10, padx=20, fill="both", expand=True)

        menu = tk.Menu(self.class_listbox, tearoff=0)
        menu.add_command(label="Edit", command=self._show_edit_frame)
        menu.add_command(label="Delete", command=self._delete_selected_class)

        def show_context_menu(event):
            selected_item = self.class_listbox.identify_row(event.y)
            if selected_item:
                self.class_listbox.selection_set(selected_item)
                menu.tk_popup(event.x_root, event.y_root)

        if sys.platform == "darwin":
            self.class_listbox.bind("<Button-2>", show_context_menu)
        else:
            self.class_listbox.bind("<Button-3>", show_context_menu)

        self.class_listbox.bind("<Double-1>", self._on_double_click)

        ctk.CTkButton(
            frame, text="Add Class", command=lambda: self.show_frame("add")
        ).pack(pady=10)

        self._refresh_list()

    def _refresh_list(self):
        for item in self.class_listbox.get_children():
            self.class_listbox.delete(item)
        for cls in self.controller.class_vm.classes:
            self.class_listbox.insert(
                "",
                "end",
                values=(
                    cls.id,
                    cls.name,
                    self.controller.teacher_vm.get_teacher_by_id(cls.teacher_id).name()
                    if cls.teacher_id
                    else "None",
                    cls.created_at,
                    cls.updated_at,
                ),
            )

    def _delete_selected_class(self):
        selected = self.class_listbox.selection()
        if not selected:
            return
        class_id = self.class_listbox.item(selected[0])["values"][0]
        self.controller.class_vm.delete_class(class_id)
        self._refresh_list()

    # ------------------------------------------------------------------ add --

    def _build_add_frame(self, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Add Class").pack(pady=(20, 10))

        self.add_name_entry = ctk.CTkEntry(frame, placeholder_text="Class Name")
        self.add_name_entry.pack(pady=5, padx=20, fill="x")

        self.add_teacher_combobox = ctk.CTkComboBox(
            frame,
            values=[t.name() for t in self.controller.teacher_vm.teachers],
            state="readonly",
        )
        self.add_teacher_combobox.pack(pady=5, padx=20, fill="x")

        self.add_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.add_error_label.pack(pady=5)

        ctk.CTkButton(frame, text="Save", command=self._save_class).pack(pady=5)
        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=5)

    def _save_class(self):
        name = self.add_name_entry.get().strip()
        teacher_id = self.add_teacher_combobox.get()
        if teacher_id:
            teacher_names = [t.name() for t in self.controller.teacher_vm.teachers]
            teacher_id = self.controller.teacher_vm.teachers[
                teacher_names.index(teacher_id)
            ].id
        else:
            print("No teacher selected, class will be created without a teacher.")

        if not name:
            self.add_error_label.configure(text="Class name cannot be empty.")
            return
        cls = self.controller.db.add_class(name, teacher_id)
        if cls:
            self.controller.class_vm.classes = self.controller.db.get_all_classes()
            self.add_name_entry.delete(0, "end")
            self.add_error_label.configure(text="")
            self._refresh_list()
            self.show_frame("list")
        else:
            self.add_error_label.configure(text="Failed to add class.")

    # ------------------------------------------------------------------ edit --

    def _show_edit_frame(self):
        selected = self.class_listbox.selection()
        if not selected:
            return
        class_id = self.class_listbox.item(selected[0])["values"][0]
        cls = self.controller.class_vm.get_class_by_id(class_id)
        if cls:
            frame = self.frames["edit"]
            for widget in frame.winfo_children():
                widget.destroy()
            self._build_edit_frame(cls, frame)
            self.show_frame("edit")

    def _build_edit_frame(self, cls: Class, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Edit Class").pack(pady=(20, 10))

        self.edit_name_entry = ctk.CTkEntry(frame, placeholder_text="Class Name")
        self.edit_name_entry.pack(pady=5, padx=20, fill="x")
        self.edit_name_entry.insert(0, cls.name)

        self.edit_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.edit_error_label.pack(pady=5)

        ctk.CTkButton(frame, text="Save", command=self._update_class).pack(pady=5)
        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=5)

    def _update_class(self):
        selected = self.class_listbox.selection()
        if not selected:
            return
        class_id = self.class_listbox.item(selected[0])["values"][0]
        cls = self.controller.class_vm.get_class_by_id(class_id)
        teacher_id = cls.teacher_id if cls else None
        name = self.edit_name_entry.get().strip()
        if not name:
            self.edit_error_label.configure(text="Class name cannot be empty.")
            return
        self.controller.class_vm.update_class(class_id, name, teacher_id)
        self._refresh_list()
        self.show_frame("list")

    # --------------------------------------------------------------- detail --

    def _on_double_click(self, event):
        row = self.class_listbox.identify_row(event.y)
        if not row:
            return
        self.class_listbox.selection_set(row)
        class_id = self.class_listbox.item(row)["values"][0]
        cls = self.controller.class_vm.get_class_by_id(class_id)
        if cls:
            frame = self.frames["detail"]
            for widget in frame.winfo_children():
                widget.destroy()
            self._build_detail_frame(cls, frame)
            self.show_frame("detail")

    def _build_detail_frame(self, cls: Class, frame: ctk.CTkFrame):
        ctk.CTkLabel(
            frame, text=cls.name, font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 2))
        ctk.CTkLabel(
            frame, text=f"Created: {cls.created_at}  |  Updated: {cls.updated_at}"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Enrolled Students").pack(pady=(5, 2))

        columns = ("ID", "First Name", "Last Name", "Email", "Date of Birth")
        student_list = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        col_widths = {
            "ID": 30,
            "First Name": 120,
            "Last Name": 120,
            "Email": 200,
            "Date of Birth": 110,
        }
        for col in columns:
            student_list.column(col, anchor=tk.W, width=col_widths[col])
            student_list.heading(col, text=col, anchor=tk.W)
        student_list.pack(pady=5, padx=20, fill="both", expand=True)

        students = self.controller.db.get_students_by_class_id(cls.id)
        for student in students:
            student_list.insert(
                "",
                "end",
                values=(
                    student.id,
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.date_of_birth,
                ),
            )

        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=10)
