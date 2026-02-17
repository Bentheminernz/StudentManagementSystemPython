import tkinter as tk
import customtkinter as ctk

class Students(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        super().__init__(parent)
        self.controller = controller
        self.label = ctk.CTkLabel(self, text="Students Page")
        self.label.pack(pady=20)

        self.student_listbox = tk.Listbox(self)
        self.student_listbox.pack(pady=10, padx=10, fill="both", expand=True)
        self.students = controller.student_vm.students
        for student in self.students:
            self.student_listbox.insert("end", f"{student.first_name} {student.last_name}")