from tkinter import ttk
from Utils.Dataclasses import Class, GradeEnum
import tkinter as tk
import customtkinter as ctk
import sys


class Classes(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        """The Classes frame is responsible for displaying the list of classes, and allowing the user to add, edit, and delete classes. Also has a detail view for showing the details of a class and the students enrolled in it."""
        super().__init__(parent)
        self.controller = controller
        self.frames: dict[str, ctk.CTkFrame] = {}

        # the frames that are within the Classes page, which are switched between when the user clicks on the different buttons (list, add, edit, detail)
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

        # show the list frame by default
        self.show_frame("list")

    def show_frame(self, name: str):
        """Brings the specified frame to the front, making it visible to the user."""
        self.frames[name].lift()

    def _build_list_frame(self, frame: ctk.CTkFrame):
        """Builds the list frame, which shows the list of classes in a treeview, and has buttons for adding a new class, editing a selected class, and deleting a selected class."""
        ctk.CTkLabel(frame, text="Classes").pack(pady=(20, 5))

        # creates the treeview for displaying the list of classes, and sets up the columns and headings
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

        # configure the columns of the treeview to have the appropriate widths and headings
        for col in columns:
            self.class_listbox.column(col, anchor=tk.W, width=col_widths[col])
            self.class_listbox.heading(col, text=col, anchor=tk.W)
        self.class_listbox.pack(pady=10, padx=20, fill="both", expand=True)

        # adds a context menu to the treeview for editing and deleting classes
        menu = tk.Menu(self.class_listbox, tearoff=0)
        menu.add_command(label="Edit", command=self._show_edit_frame)
        menu.add_command(label="Delete", command=self._delete_selected_class)

        def show_context_menu(event):
            """Shows the context menu when the user right-clicks on a class in the treeview."""
            selected_item = self.class_listbox.identify_row(event.y)
            if selected_item:
                self.class_listbox.selection_set(selected_item)
                menu.tk_popup(event.x_root, event.y_root)

        # Darwin (macOS) uses Button-2 for right-click, while Windows (and hopefully Linux) use Button-3
        if sys.platform == "darwin":
            self.class_listbox.bind("<Button-2>", show_context_menu)
        else:
            self.class_listbox.bind("<Button-3>", show_context_menu)

        self.class_listbox.bind("<Double-1>", self._on_double_click)

        ctk.CTkButton(frame, text="Add Class", command=self._show_add_frame).pack(
            pady=10
        )

        # initially populate the list of classes when the frame is built
        self._refresh_list()

    def _refresh_list(self):
        """Refreshes the list of classes in the treeview by clearing the existing items and re-populating it with the current list of classes from the database."""
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
        """Deletes the selected class from the database, and refreshes the list to remove it from the treeview."""
        selected = self.class_listbox.selection()
        if not selected:
            return
        class_id = self.class_listbox.item(selected[0])["values"][0]
        self.controller.class_vm.delete_class(class_id)
        self._refresh_list()

    def _build_add_frame(self, frame: ctk.CTkFrame):
        """Builds the add frame, which allows the user to enter the details of a new class and save it to the database."""
        ctk.CTkLabel(frame, text="Add Class").pack(pady=(20, 10))

        self.add_name_entry = ctk.CTkEntry(frame, placeholder_text="Class Name")
        self.add_name_entry.pack(pady=5, padx=20, fill="x")

        self.add_teacher_combobox = ctk.CTkComboBox(
            frame,
            values=[t.name() for t in self.controller.teacher_vm.teachers],
            state="readonly",
        )
        self.add_teacher_combobox.pack(pady=5, padx=20, fill="x")

        # creates a HStack (swiftui naming for horizontal layout) with two VStacks (vertical layouts) for the available students and selected students, and buttons in the middle for moving students between the two lists
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
        self.add_error_label.pack(pady=(5, 0))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=(0, 5))
        ctk.CTkButton(btn_row, text="Save", command=self._save_class).pack(
            side="left", padx=5
        )
        ctk.CTkButton(
            btn_row,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(side="left", padx=5)

    def _process_click(self, student, event, students, highlighted, anchor):
        """Helper method to process a click on a student in the available or selected list, and determine the new highlighted students and anchor based on whether shift or ctrl/cmd is held."""
        shift = (
            bool(event.state & 0x1) if event else False
        )  # The shift key is represented by the least significant bit (0x1) in the event state
        multi = (
            bool(event.state & 0xC) if event else False
        )  # The ctrl key is represented by the 0x4 bit and the cmd key (on macOS) is represented by the 0x8 bit in the event state, so we check for both to determine if either is held for multi-selection

        # if shift is held, and there is an anchor (student that was previously clicked), we want to highlight all students between the anchor and the currently clicked student.
        if shift and anchor is not None:
            try:
                # tries to find the indices of the anchor and clicked student in the list of students, and highlights all students between those indices (inclusive)
                anchor_idx = next(
                    i for i, s in enumerate(students) if s.id == anchor.id
                )  # anchor_idx is the index of the anchor student in the list of students
                current_idx = next(
                    i for i, s in enumerate(students) if s.id == student.id
                )  # current_idx is the index of the currently clicked student in the list of students
                lower_bound, higher_bound = (
                    min(anchor_idx, current_idx),
                    max(anchor_idx, current_idx),
                )  # lower_bound and higher_bound are the lower and upper bounds of the indices to highlight
                new_highlight = students[
                    lower_bound : higher_bound + 1
                ]  # new_highlight is the new list of highlighted students, which includes all students between the anchor and clicked student
            except StopIteration:  # exception handling for the case where the anchor or clicked student is not found in the list of students (shouldn't happen, but just in case), in which case we just highlight the clicked student
                new_highlight = [student]  # new_highlight is just the clicked student
                anchor = student  # we also set the anchor to the clicked student
        elif multi:
            # if ctrl/cmd is held, we want to toggle the highlight of the clicked student (add to highlighted if not already highlighted, or remove from highlighted if already highlighted), and set the anchor to the clicked student
            ids = {
                student.id for student in highlighted
            }  # ids is the set of IDs of the currently highlighted students
            if (
                student.id in ids
            ):  # if the clicked student is already highlighted, unhighlight them
                new_highlight = [
                    s for s in highlighted if s.id != student.id
                ]  # new list of highlighted students with the clicked student removed
            else:
                new_highlight = (
                    highlighted + [student]
                )  # otherwise, if the clicked student is not already highlighted, we add them to the list of highlighted students
            anchor = student  # in either case, we set the anchor to the clicked student
        else:
            # if neither shift nor ctrl/cmd is held, clear the highlighted students and just highlight the clicked student, and set the anchor to the clicked student
            new_highlight = [student]
            anchor = student

        # return the new list of highlighted students and the new anchor
        return new_highlight, anchor

    def _render_picker_list(
        self,
        frame: ctk.CTkScrollableFrame,
        students: list,
        highlighted_ids: set,
        on_click,
    ):
        """Helper method to render the list of students in the available or selected list of the add/edit frames"""
        for widget in frame.winfo_children():
            # for each widget in the frame (i.e. each student button), we destroy it to clear the existing list before re-rendering the updated list of students
            widget.destroy()
        for student in students:
            # for each student in the list of students to render, we want to make a button for them, and if their ID is in the set of highlighted IDs, we want to give the button a different bg colour
            is_highlighted = student.id in highlighted_ids
            btn = ctk.CTkButton(
                frame,
                text=student.name(),
                fg_color=("gray70", "gray35") if is_highlighted else "transparent",
                text_color=("black", "white"),
                hover_color=("gray75", "gray30"),
                anchor="w",
            )
            # bind the Button-1 action (left-click) to call the on_click function with the student and event as arguments.
            btn.bind(
                "<Button-1>", lambda event, student=student: on_click(student, event)
            )
            btn.pack(fill="x", pady=1)

    def _show_add_frame(self):
        """Shows the add frame and initialise the available and selected lists for the student picker, and clears any existing input in the entry fields."""
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
        """Renders the available and selected student lists in the add frame by calling the _render_picker_list helper method for each list with the appropriate arguments."""
        self._render_picker_list(
            self._add_available_frame,
            self._add_available,
            {student.id for student in self._add_highlighted_available},
            self._add_click_available,
        )
        self._render_picker_list(
            self._add_selected_frame,
            self._add_selected,
            {student.id for student in self._add_highlighted_selected},
            self._add_click_selected,
        )

    def _add_click_available(self, student, event):
        """Handles a click on a student in the available list in the add frame by updating the highlighted students and anchor based on whether shift or ctrl/cmd is held, and then re-rendering the lists to show the updated highlights."""
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
        """Handles a click on a student in the selected list in the add frame by updating the highlighted students and anchor based on whether shift or ctrl/cmd is held, and then re-rendering the lists to show the updated highlights."""
        self._add_highlighted_selected, self._add_anchor_selected = self._process_click(
            student,
            event,
            self._add_selected,
            self._add_highlighted_selected,
            self._add_anchor_selected,
        )
        self._add_render()

    def _add_move_to_selected(self):
        """Moves the highlighted students in the available list to the selected list in the add frame, and then re-renders the lists to show the updated available and selected students."""
        if not self._add_highlighted_available:
            return
        move_ids = {student.id for student in self._add_highlighted_available}
        self._add_selected.extend(self._add_highlighted_available)
        self._add_available = [s for s in self._add_available if s.id not in move_ids]
        self._add_highlighted_available = []
        self._add_anchor_available = None
        self._add_render()

    def _add_move_to_available(self):
        """Moves the highlighted students in the selected list back to the available list in the add frame, and then re-renders the lists to show the updated available and selected students."""
        if not self._add_highlighted_selected:
            return
        move_ids = {student.id for student in self._add_highlighted_selected}
        self._add_available.extend(self._add_highlighted_selected)
        self._add_selected = [s for s in self._add_selected if s.id not in move_ids]
        self._add_highlighted_selected = []
        self._add_anchor_selected = None
        self._add_render()

    def _save_class(self):
        """Saves the new class to the database with the details entered in the add frame, and refreshes the list to show the new class."""
        name = self.add_name_entry.get().strip()
        teacher_id = self.add_teacher_combobox.get()
        if teacher_id:
            teacher_names = [t.name() for t in self.controller.teacher_vm.teachers]
            teacher_id = self.controller.teacher_vm.teachers[
                teacher_names.index(teacher_id)
            ].id
        else:
            print("No teacher selected, setting teacher_id to None")
            teacher_id = None

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

    def _show_edit_frame(self):
        """Shows the edit frame for the selected class, and populates the entry fields and student picker with the current details of the class."""
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
        """Builds the edit class frame, which allows the user to edit the details of a class and save the changes to the database."""
        ctk.CTkLabel(frame, text="Edit Class").pack(pady=(20, 10))

        self.edit_name_entry = ctk.CTkEntry(frame, placeholder_text="Class Name")
        self.edit_name_entry.pack(pady=5, padx=20, fill="x")
        self.edit_name_entry.insert(0, cls.name)

        # creates the teacher combobox for the edit frame, and pre-populates it with the current teacher of the class (if any)
        self.edit_teacher_combobox = ctk.CTkComboBox(
            frame,
            values=[teacher.name() for teacher in self.controller.teacher_vm.teachers],
            state="readonly",
        )
        self.edit_teacher_combobox.pack(pady=5, padx=20, fill="x")
        teacher = self.controller.teacher_vm.get_teacher_by_id(cls.teacher_id)
        if teacher is not None:
            self.edit_teacher_combobox.set(teacher.name())
        else:
            self.edit_teacher_combobox.set("")

        self.edit_error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.edit_error_label.pack(pady=(5, 0))

        edit_btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        edit_btn_row.pack(pady=(0, 5))
        ctk.CTkButton(edit_btn_row, text="Save", command=self._update_class).pack(
            side="left", padx=5
        )
        ctk.CTkButton(
            edit_btn_row,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(side="left", padx=5)

        # initalise the available and selected lists for the student picker based on the current students enrolled in the class, and render the lists in the edit frame
        enrolled = self.controller.db.get_students_by_class_id(cls.id)
        enrolled_ids = {student.id for student in enrolled}
        self._edit_available = [
            student
            for student in self.controller.student_vm.students
            if student.id not in enrolled_ids
        ]
        self._edit_selected = list(enrolled)
        self._edit_highlighted_available = []
        self._edit_highlighted_selected = []
        self._edit_anchor_available = None
        self._edit_anchor_selected = None

        # creates a HStack (swiftui naming for horizontal layout) with two VStacks (vertical layouts) for the available students and selected students, and buttons in the middle for moving students between the two lists
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

    def _edit_render(self):
        """Renders the available and selected student lists in the edit frame by calling the _render_picker_list helper method for each list with the appropriate arguments."""
        self._render_picker_list(
            self._edit_available_frame,
            self._edit_available,
            {student.id for student in self._edit_highlighted_available},
            self._edit_click_available,
        )
        self._render_picker_list(
            self._edit_selected_frame,
            self._edit_selected,
            {student.id for student in self._edit_highlighted_selected},
            self._edit_click_selected,
        )

    def _edit_click_available(self, student, event):
        """Handles a click on a student in the available list in the edit frame by updating the highlighted students and anchor based on whether shift or ctrl/cmd is held, and then re-rendering the lists to show the updated highlights."""
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
        """Handles a click on a student in the selected list in the edit frame by updating the highlighted students and anchor based on whether shift or ctrl/cmd is held, and then re-rendering the lists to show the updated highlights."""
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
        """Moves the highlighted students in the available list to the selected list in the edit frame, and then re-renders the lists to show the updated available and selected students."""
        if not self._edit_highlighted_available:
            return
        move_ids = {student.id for student in self._edit_highlighted_available}
        self._edit_selected.extend(self._edit_highlighted_available)
        self._edit_available = [
            student for student in self._edit_available if student.id not in move_ids
        ]
        self._edit_highlighted_available = []
        self._edit_anchor_available = None
        self._edit_render()

    def _edit_move_to_available(self):
        """Moves the highlighted students in the selected list back to the available list in the edit frame, and then re-renders the lists to show the updated available and selected students."""
        if not self._edit_highlighted_selected:
            return
        move_ids = {student.id for student in self._edit_highlighted_selected}
        self._edit_available.extend(self._edit_highlighted_selected)
        self._edit_selected = [
            student for student in self._edit_selected if student.id not in move_ids
        ]
        self._edit_highlighted_selected = []
        self._edit_anchor_selected = None
        self._edit_render()

    def _update_class(self):
        """Saves the changes to the class details to the database, including the updated name, teacher, and enrolled students, and refreshes the list to show the updated class details."""
        selected = self.class_listbox.selection()
        if not selected:
            return
        teacher_id = self.edit_teacher_combobox.get()
        if teacher_id:
            teacher_names = [
                teacher.name() for teacher in self.controller.teacher_vm.teachers
            ]
            teacher_id = self.controller.teacher_vm.teachers[
                teacher_names.index(teacher_id)
            ].id
        else:
            teacher_id = None
        class_id = self.class_listbox.item(selected[0])["values"][0]
        name = self.edit_name_entry.get().strip()
        if not name:
            self.edit_error_label.configure(text="Class name cannot be empty.")
            return
        self.controller.class_vm.update_class(class_id, name, teacher_id)
        selected_ids = [student.id for student in getattr(self, "_edit_selected", [])]
        self.controller.db.set_students_for_class(class_id, selected_ids)
        self._refresh_list()
        self.show_frame("list")

    def _on_double_click(self, event):
        """Handles a double-click on a class in the list frame by showing the detail frame for the selected class, and populating it with the details of the class and the students enrolled in it."""
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
        """Builds the detail frame for a class, which shows the details of the class and the students enrolled in it, and allows the user to edit the grade for each student in the class."""
        self._detail_class_id = cls.id
        teacher = (
            self.controller.teacher_vm.get_teacher_by_id(cls.teacher_id)
            if cls.teacher_id
            else None
        )

        # displays the class name, teacher, and created/updated timestamps at the top of the detail frame
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

        # creates the treeview for displaying the list of students enrolled in the class, and sets up the columns and headings, including a column for the student's grade in the class
        columns = ("ID", "First Name", "Last Name", "Email", "Date of Birth", "Grade")
        self._detail_student_list = ttk.Treeview(
            frame, columns=columns, show="headings", height=12
        )
        col_widths = {
            "ID": 30,
            "First Name": 120,
            "Last Name": 120,
            "Email": 200,
            "Date of Birth": 110,
            "Grade": 70,
        }
        for col in columns:
            self._detail_student_list.column(col, anchor=tk.W, width=col_widths[col])
            self._detail_student_list.heading(col, text=col, anchor=tk.W)
        self._detail_student_list.pack(pady=5, padx=20, fill="both", expand=True)
        self._detail_student_list.bind(
            "<<TreeviewSelect>>", self._on_detail_student_selected
        )

        # creates the grade editor row, which includes a label, a combobox for selecting the grade to assign to the selected student, and a button for saving the selected grade for the student. Also includes a status label for showing messages about the grade saving process (e.g. success or error messages).
        grade_editor_row = ctk.CTkFrame(frame, fg_color="transparent")
        grade_editor_row.pack(pady=(0, 4))
        ctk.CTkLabel(grade_editor_row, text="Selected Student Grade:").pack(
            side="left", padx=(0, 8)
        )
        self._detail_grade_combobox = ctk.CTkComboBox(
            grade_editor_row,
            values=[grade.value for grade in GradeEnum],
            state="readonly",
            width=80,
        )
        self._detail_grade_combobox.pack(side="left", padx=(0, 8))
        self._detail_grade_combobox.set(GradeEnum.A.value)
        ctk.CTkButton(
            grade_editor_row,
            text="Save Grade",
            command=self._save_selected_student_grade,
        ).pack(side="left")

        self._detail_grade_status = ctk.CTkLabel(frame, text="", text_color="gray")
        self._detail_grade_status.pack(pady=(0, 6))

        self._refresh_detail_students()

        ctk.CTkButton(
            frame,
            text="Back",
            fg_color="gray",
            command=lambda: self.show_frame("list"),
        ).pack(pady=10)

    def _refresh_detail_students(self):
        """Refreshes the list of students enrolled in the class in the detail frame by clearing the existing items in the treeview and re-populating it with the current list of enrolled students and their grades from the database."""
        if not hasattr(self, "_detail_student_list"):
            return
        for item in self._detail_student_list.get_children():
            self._detail_student_list.delete(item)

        students = self.controller.db.get_students_by_class_id(self._detail_class_id)
        for student in students:
            grade = self.controller.db.get_grade_for_student_in_class(
                student.id, self._detail_class_id
            )
            self._detail_student_list.insert(
                "",
                "end",
                values=(
                    student.id,
                    student.first_name,
                    student.last_name,
                    student.email,
                    student.date_of_birth,
                    grade.grade.value if grade else "",
                ),
            )

    def _on_detail_student_selected(self, _event=None):
        """Handles the selection of a student in the enrolled students treeview in the detail frame by updating the grade editor combobox to show the current grade for the selected student (if any), and updating the status label to show a message about the current grade or prompt the user to select a grade if none is set yet."""
        selected = self._detail_student_list.selection()
        if not selected:
            return
        selected_values = self._detail_student_list.item(selected[0])["values"]
        if len(selected_values) < 6:
            return

        current_grade = selected_values[5]
        if current_grade in [grade.value for grade in GradeEnum]:
            self._detail_grade_combobox.set(current_grade)
            self._detail_grade_status.configure(
                text=f"Current grade: {current_grade}", text_color="gray"
            )
        else:
            self._detail_grade_combobox.set(GradeEnum.A.value)
            self._detail_grade_status.configure(
                text="No grade set yet. Choose a grade and save.",
                text_color="gray",
            )

    def _save_selected_student_grade(self):
        """Saves the grade selected in the grade editor combobox for the currently selected student in the enrolled students treeview in the detail frame to the database, and refreshes the list of students to show the updated grade. Also updates the status label to show a success message if the grade was saved successfully, or an error message if there was a problem saving the grade."""
        selected = self._detail_student_list.selection()
        if not selected:
            self._detail_grade_status.configure(
                text="Select a student first.", text_color="red"
            )
            return

        selected_values = self._detail_student_list.item(selected[0])["values"]
        student_id = selected_values[0]
        grade_value = self._detail_grade_combobox.get()
        success, _ = self.controller.db.set_grade_for_student_in_class(
            student_id, self._detail_class_id, grade_value
        )
        if success:
            self._refresh_detail_students()
            self._detail_grade_status.configure(
                text=f"Saved grade {grade_value}.", text_color="green"
            )
        else:
            self._detail_grade_status.configure(
                text="Failed to save grade for this student/class.", text_color="red"
            )
