import customtkinter as ctk
from SignLanguage import CameraFrame
from morsecode import MorseCodeFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("700x600")

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

current_frame = None

def switch_frame(new_frame_class):
    global current_frame
    if current_frame is not None:
        current_frame.destroy() 
    
    current_frame = new_frame_class(root, show_main_menu)
    current_frame.grid(row=0, column=0, sticky="nsew")

def show_main_menu():
    switch_frame(MainMenuFrame)

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.label = ctk.CTkLabel(self, text="Was möchten Sie übersetzen?", font=("Roboto", 32))
        self.label.grid(row=0, column=0, pady=20)

        self.button1 = ctk.CTkButton(self, text="Gebärdensprache", 
                                     font=("Roboto", 20),
                                     command=lambda: switch_frame(CameraFrame))
        self.button1.grid(row=1, column=0, pady=20, padx=50, sticky="nsew")

        self.button2 = ctk.CTkButton(self, text="Morsecode", 
                                     font=("Roboto", 20),
                                     command=lambda: switch_frame(MorseCodeFrame))
        self.button2.grid(row=2, column=0, pady=20, padx=50, sticky="nsew")

show_main_menu()
root.mainloop()