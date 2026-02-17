from UI.Home import Home
from UI.Students import Students
from Utils.Database import Database
from Utils.ViewModels.StudentViewModel import StudentViewModel
import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.student_vm = StudentViewModel(self.db)

        self.title("Student Management System - KHS")
        self.geometry("800x500")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="KHS DB", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        ctk.CTkButton(
            self.sidebar, text="Home", command=lambda: self.show_frame(Home)
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            self.sidebar, text="Students", command=lambda: self.show_frame(Students)
        ).pack(pady=10, padx=10)

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Page in (Home, Students):
            frame = Page(self.container, self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Home)

    def show_frame(self, page_class):
        self.frames[page_class].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
