from UI.Home import Home
from UI.Students import Students
from UI.Classes import Classes
from UI.Teachers import Teachers
from Utils.Database import Database
from Utils.ViewModels.TeacherViewModel import TeacherViewModel
from Utils.ViewModels.StudentViewModel import StudentViewModel
from Utils.ViewModels.ClassViewModel import ClassViewModel
import customtkinter as ctk

"""The apps entry point. Initializes the database, view models, and main application window."""


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()  # Create a new database instance

        # Create ViewModels from the database instance
        self.student_vm = StudentViewModel(self.db)
        self.class_vm = ClassViewModel(self.db)
        self.teacher_vm = TeacherViewModel(self.db)

        # Initialize the main application window
        self.title("Student Management System - KHS")
        self.geometry("1000x600")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Creates the sidebar buttons
        ctk.CTkLabel(
            self.sidebar, text="KHS DB", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        ctk.CTkButton(
            self.sidebar, text="Home", command=lambda: self.show_frame(Home)
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            self.sidebar, text="Students", command=lambda: self.show_frame(Students)
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            self.sidebar, text="Teachers", command=lambda: self.show_frame(Teachers)
        ).pack(pady=10, padx=10)
        ctk.CTkButton(
            self.sidebar, text="Classes", command=lambda: self.show_frame(Classes)
        ).pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Exit", command=self.destroy).pack(
            pady=10, padx=10, side="bottom"
        )

        # Makes the container for main content area
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Makes each frame, and adds it to the container, and stores it in a dictionary for easy access
        self.frames = {}
        for Page in (Home, Students, Teachers, Classes):
            frame = Page(self.container, self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Home)

    # Helper function to show a frame, and call its on_show method if it has one
    def show_frame(self, page_class):
        frame = self.frames[page_class]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()


if __name__ == "__main__":
    # Initialize and run the application
    app = App()
    app.mainloop()
