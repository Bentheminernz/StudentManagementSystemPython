import customtkinter as ctk
from UI.Home import Home

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My App")
        self.geometry("400x300")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Page in (Home,):
            frame = Page(self, self)
            self.frames[Page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Home)

    def show_frame(self, page_class):
        self.frames[page_class].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()