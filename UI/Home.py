import customtkinter as ctk

class Home(ctk.CTkFrame):
    def __init__(self, parent, controller: ctk.CTk):
        super().__init__(parent)

        self.label = ctk.CTkLabel(self, text="Welcome to the Home Page!")
        self.label.pack(pady=20)

        self.exit_button = ctk.CTkButton(self, text="Exit", command=controller.quit)
        self.exit_button.pack(pady=10)