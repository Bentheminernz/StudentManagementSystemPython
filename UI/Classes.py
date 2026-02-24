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

        ctk.CTkButton(frame, text="Add Class", command=self._show_add_frame).pack(
            pady=10
        )

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

        # Dual-list student picker
        hstack = ctk.CTkFrame(frame)
        hstack.pack(fill="both", expand=True, padx=20, pady=5)

        left_vstack = ctk.CTkFrame(hstack)
        left_vstack.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left_vstack, text="Available Students").pack(pady=5)
        self._add_available_frame = ctk.CTkScrollableFrame(left_vstack)
        self._add_available_frame.pack(fill="both", expand=True, padx=5, pady=5)

        mid_vstack = ctk.CTkFrame(hstack)
        mid_vstack.pack(side="left", fill="y", padx=10)
        ctk.CTkButton(
            mid_vstack, text=">", width=40, command=self._add_move_to_selected
        ).pack(pady=5, padx=5)
        ctk.CTkButton(
            mid_vstack, text="<", width=40, command=self._add_move_to_available
        ).pack(pady=5, padx=5)

        right_vstack = ctk.CTkFrame(hstack)
        right_vstack.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(right_vstack, text="Selected Students").pack(pady=5)
        self._add_selected_frame = ctk.CTkScrollableFrame(right_vstack)
        self._add_selected_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.add_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.add_error_label.pack(pady=5)

        ctk.CTkButton(frame, text="Save", command=self._save_class).pack(pady=5)
        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=5)

    # -------------------------------------------------- student picker helpers --

    def _process_click(self, student, event, students, highlighted, anchor):
        """Handle single / Cmd+Ctrl (toggle) / Shift (range) click."""
        shift = bool(event.state & 0x1) if event else False
        multi = bool(event.state & 0xC) if event else False  # Ctrl (0x4) or Cmd (0x8)

        if shift and anchor is not None:
            try:
                a_idx = next(i for i, s in enumerate(students) if s.id == anchor.id)
                c_idx = next(i for i, s in enumerate(students) if s.id == student.id)
                lo, hi = min(a_idx, c_idx), max(a_idx, c_idx)
                new_hl = students[lo : hi + 1]
            except StopIteration:
                new_hl = [student]
                anchor = student
        elif multi:
            ids = {s.id for s in highlighted}
            if student.id in ids:
                new_hl = [s for s in highlighted if s.id != student.id]
            else:
                new_hl = highlighted + [student]
            anchor = student
        else:
            new_hl = [student]
            anchor = student

        return new_hl, anchor

    def _render_picker_list(
        self,
        frame: ctk.CTkScrollableFrame,
        students: list,
        highlighted_ids: set,
        on_click,
    ):
        for w in frame.winfo_children():
            w.destroy()
        for s in students:
            is_hl = s.id in highlighted_ids
            btn = ctk.CTkButton(
                frame,
                text=s.name(),
                fg_color=("gray70", "gray35") if is_hl else "transparent",
                text_color=("black", "white"),
                hover_color=("gray75", "gray30"),
                anchor="w",
            )
            btn.bind("<Button-1>", lambda e, st=s: on_click(st, e))
            btn.pack(fill="x", pady=1)

    # ------------------------------------------- add-frame picker state/actions --

    def _show_add_frame(self):
        self._add_available = list(self.controller.student_vm.students)
        self._add_selected = []
        self._add_highlighted_available = []
        self._add_highlighted_selected = []
        self._add_anchor_available = None
        self._add_anchor_selected = None
        self._add_render()
        self.add_name_entry.delete(0, "end")
        self.add_teacher_combobox.set("")
        self.add_error_label.configure(text="")
        self.show_frame("add")

    def _add_render(self):
        self._render_picker_list(
            self._add_available_frame,
            self._add_available,
            {s.id for s in self._add_highlighted_available},
            self._add_click_available,
        )
        self._render_picker_list(
            self._add_selected_frame,
            self._add_selected,
            {s.id for s in self._add_highlighted_selected},
            self._add_click_selected,
        )

    def _add_click_available(self, student, event):
        self._add_highlighted_available, self._add_anchor_available = (
            self._process_click(
                student,
                event,
                self._add_available,
                self._add_highlighted_available,
                self._add_anchor_available,
            )
        )
        self._add_render()

    def _add_click_selected(self, student, event):
        self._add_highlighted_selected, self._add_anchor_selected = self._process_click(
            student,
            event,
            self._add_selected,
            self._add_highlighted_selected,
            self._add_anchor_selected,
        )
        self._add_render()

    def _add_move_to_selected(self):
        if not self._add_highlighted_available:
            return
        move_ids = {s.id for s in self._add_highlighted_available}
        self._add_selected.extend(self._add_highlighted_available)
        self._add_available = [s for s in self._add_available if s.id not in move_ids]
        self._add_highlighted_available = []
        self._add_anchor_available = None
        self._add_render()

    def _add_move_to_available(self):
        if not self._add_highlighted_selected:
            return
        move_ids = {s.id for s in self._add_highlighted_selected}
        self._add_available.extend(self._add_highlighted_selected)
        self._add_selected = [s for s in self._add_selected if s.id not in move_ids]
        self._add_highlighted_selected = []
        self._add_anchor_selected = None
        self._add_render()

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
            selected_ids = [s.id for s in getattr(self, "_add_selected", [])]
            if selected_ids:
                self.controller.db.set_students_for_class(cls.id, selected_ids)
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

        self.edit_teacher_combobox = ctk.CTkComboBox(
            frame,
            values=[t.name() for t in self.controller.teacher_vm.teachers],
            state="readonly",
        )
        self.edit_teacher_combobox.pack(pady=5, padx=20, fill="x")
        if cls.teacher_id:
            teacher_names = [t.name() for t in self.controller.teacher_vm.teachers]
            teacher_id = self.controller.teacher_vm.get_teacher_by_id(cls.teacher_id).id
            self.edit_teacher_combobox.set(
                teacher_names[teacher_id - 1]
                if teacher_id - 1 < len(teacher_names)
                else ""
            )
        else:
            self.edit_teacher_combobox.set("")

        # Dual-list student picker (pre-populate with enrolled students)
        enrolled = self.controller.db.get_students_by_class_id(cls.id)
        enrolled_ids = {s.id for s in enrolled}
        self._edit_available = [
            s for s in self.controller.student_vm.students if s.id not in enrolled_ids
        ]
        self._edit_selected = list(enrolled)
        self._edit_highlighted_available = []
        self._edit_highlighted_selected = []
        self._edit_anchor_available = None
        self._edit_anchor_selected = None

        hstack = ctk.CTkFrame(frame)
        hstack.pack(fill="both", expand=True, padx=20, pady=5)

        left_vstack = ctk.CTkFrame(hstack)
        left_vstack.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left_vstack, text="Available Students").pack(pady=5)
        self._edit_available_frame = ctk.CTkScrollableFrame(left_vstack)
        self._edit_available_frame.pack(fill="both", expand=True, padx=5, pady=5)

        mid_vstack = ctk.CTkFrame(hstack)
        mid_vstack.pack(side="left", fill="y", padx=10)
        ctk.CTkButton(
            mid_vstack, text=">", width=40, command=self._edit_move_to_selected
        ).pack(pady=5, padx=5)
        ctk.CTkButton(
            mid_vstack, text="<", width=40, command=self._edit_move_to_available
        ).pack(pady=5, padx=5)

        right_vstack = ctk.CTkFrame(hstack)
        right_vstack.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(right_vstack, text="Selected Students").pack(pady=5)
        self._edit_selected_frame = ctk.CTkScrollableFrame(right_vstack)
        self._edit_selected_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self._edit_render()

        self.edit_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.edit_error_label.pack(pady=5)
        ctk.CTkButton(frame, text="Save", command=self._update_class).pack(pady=5)
        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=5)

    # ------------------------------------------ edit-frame picker state/actions --

    def _edit_render(self):
        self._render_picker_list(
            self._edit_available_frame,
            self._edit_available,
            {s.id for s in self._edit_highlighted_available},
            self._edit_click_available,
        )
        self._render_picker_list(
            self._edit_selected_frame,
            self._edit_selected,
            {s.id for s in self._edit_highlighted_selected},
            self._edit_click_selected,
        )

    def _edit_click_available(self, student, event):
        self._edit_highlighted_available, self._edit_anchor_available = (
            self._process_click(
                student,
                event,
                self._edit_available,
                self._edit_highlighted_available,
                self._edit_anchor_available,
            )
        )
        self._edit_render()

    def _edit_click_selected(self, student, event):
        self._edit_highlighted_selected, self._edit_anchor_selected = (
            self._process_click(
                student,
                event,
                self._edit_selected,
                self._edit_highlighted_selected,
                self._edit_anchor_selected,
            )
        )
        self._edit_render()

    def _edit_move_to_selected(self):
        if not self._edit_highlighted_available:
            return
        move_ids = {s.id for s in self._edit_highlighted_available}
        self._edit_selected.extend(self._edit_highlighted_available)
        self._edit_available = [s for s in self._edit_available if s.id not in move_ids]
        self._edit_highlighted_available = []
        self._edit_anchor_available = None
        self._edit_render()

    def _edit_move_to_available(self):
        if not self._edit_highlighted_selected:
            return
        move_ids = {s.id for s in self._edit_highlighted_selected}
        self._edit_available.extend(self._edit_highlighted_selected)
        self._edit_selected = [s for s in self._edit_selected if s.id not in move_ids]
        self._edit_highlighted_selected = []
        self._edit_anchor_selected = None
        self._edit_render()

    def _update_class(self):
        selected = self.class_listbox.selection()
        if not selected:
            return
        teacher_id = self.edit_teacher_combobox.get()
        if teacher_id:
            teacher_names = [t.name() for t in self.controller.teacher_vm.teachers]
            teacher_id = self.controller.teacher_vm.teachers[
                teacher_names.index(teacher_id)
            ].id
        else:
            print("No teacher selected, class will be updated without a teacher.")
        class_id = self.class_listbox.item(selected[0])["values"][0]
        name = self.edit_name_entry.get().strip()
        if not name:
            self.edit_error_label.configure(text="Class name cannot be empty.")
            return
        self.controller.class_vm.update_class(class_id, name, teacher_id)
        selected_ids = [s.id for s in getattr(self, "_edit_selected", [])]
        self.controller.db.set_students_for_class(class_id, selected_ids)
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
        teacher = (
            self.controller.teacher_vm.get_teacher_by_id(cls.teacher_id)
            if cls.teacher_id
            else None
        )
        ctk.CTkLabel(
            frame, text=cls.name, font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 2))
        ctk.CTkLabel(
            frame, text=f"Teacher: {teacher.name() if teacher else 'None'}"
        ).pack(pady=(0, 2))
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
