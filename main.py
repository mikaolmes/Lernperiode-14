import customtkinter as ctk
from SignLanguage import CameraFrame
from morsecode import MorseCodeFrame
from meme_movement import MemeMovementTestFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green") 

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sign & Morse Translator Pro")
        self.geometry("800x800")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Globaler Hotkey: Esc bringt einen immer zurück zum Menü
        self.bind("<Escape>", lambda e: self.show_main_menu())
        
        self.current_frame = None
        self.show_main_menu()

    def switch_frame(self, new_frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = new_frame_class(self, self.show_main_menu)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
       
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.label = ctk.CTkLabel(
            self, 
            text="Übersetzungs-Zentrale", 
            font=("Bahnschrift", 46, "bold"),
            text_color="#10b981"
        )
        self.label.grid(row=0, column=0, pady=(40, 10))

        self.button1 = ctk.CTkButton(
            self, 
            text="Gebärdensprache (1)", 
            font=("Roboto", 22, "bold"),
            height=80, width=400, corner_radius=15,
            command=lambda: master.switch_frame(CameraFrame)
        )
        self.button1.grid(row=2, column=0, pady=15)

        self.button2 = ctk.CTkButton(
            self, 
            text="Morsecode (2)", 
            font=("Roboto", 22, "bold"),
            height=80, width=400, corner_radius=15,
            fg_color="#333333", hover_color="#444444",
            command=lambda: master.switch_frame(MorseCodeFrame)
        )
        self.button2.grid(row=3, column=0, pady=15)

        self.button3 = ctk.CTkButton(
            self,
            text="Meme Movement Test",
            font=("Roboto", 22, "bold"),
            height=80,
            width=400,
            corner_radius=15,
            fg_color="#1f2937",
            hover_color="#374151",
            command=lambda: master.switch_frame(MemeMovementTestFrame)
        )
        self.button3.grid(row=4, column=0, pady=15)
        # Ziffern-Hotkeys für das Menü
        master.bind("1", lambda e: master.switch_frame(CameraFrame))
        master.bind("2", lambda e: master.switch_frame(MorseCodeFrame))

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()