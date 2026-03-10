import customtkinter as ctk


class Home(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        """The Home frame is the default landing page of the application, which shows some quick facts about the number of students, teachers, and classes in the system."""
        super().__init__(parent)
        self.controller = controller

        self.label = ctk.CTkLabel(
            self,
            text="Welcome School Admin to the KHS Student Management System!",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.label.pack(pady=20)

        self.quick_facts_title = ctk.CTkLabel(
            self,
            text="Quick Facts",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.quick_facts_title.pack(pady=10)

        self.quick_facts = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.quick_facts.pack(pady=10)

        self.refresh_quick_facts()

    def refresh_quick_facts(self):
        """Refreshes the quick facts by reloading the data from the database and updating the text of the quick facts label."""
        self.controller.class_vm.load_classes()
        self.controller.student_vm.load_students()
        self.controller.teacher_vm.load_teachers()

        number_of_classes = len(self.controller.class_vm.classes)
        number_of_students = len(self.controller.student_vm.students)
        number_of_teachers = len(self.controller.teacher_vm.teachers)

        self.quick_facts.configure(
            text=(
                f"Number of Classes: {number_of_classes}\n"
                f"Number of Students: {number_of_students}\n"
                f"Number of Teachers: {number_of_teachers}"
            )
        )

    def on_show(self):
        self.refresh_quick_facts()
