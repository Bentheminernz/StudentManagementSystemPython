import tkinter as tk
import customtkinter as ctk


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

        self.show_frame("list")

    def show_frame(self, name: str):
        self.frames[name].lift()

    def _build_list_frame(self, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Students").pack(pady=(20, 5))

        self.student_listbox = tk.Listbox(frame)
        self.student_listbox.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkButton(
            frame, text="Add Student", command=lambda: self.show_frame("add")
        ).pack(pady=10)

        self._refresh_list()

    def _refresh_list(self):
        self.student_listbox.delete(0, "end")
        for student in self.controller.student_vm.students:
            self.student_listbox.insert(
                "end", f"{student.first_name} {student.last_name}"
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
