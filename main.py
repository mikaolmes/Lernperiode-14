import customtkinter as ctk
from SignLanguage import CameraFrame
from morsecode import MorseCodeFrame
from meme_movement import MemeMovementTestFrame

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("green") 

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sign & Morse Translator")
        self.geometry("900x700")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_main_menu()

    def switch_frame(self, new_frame_class):
        if hasattr(self, "current_frame") and self.current_frame:
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

        
        self.label = ctk.CTkLabel(
            self, 
            text="Übersetzungs-Tool", 
            font=("Bahnschrift", 42, "bold"),
            text_color="#10b981" 
        )
        self.label.grid(row=0, column=0, pady=(40, 10))

        self.subtitle = ctk.CTkLabel(
            self, 
            text="Wählen Sie eine Methode aus:", 
            font=("Roboto", 18)
        )
        self.subtitle.grid(row=1, column=0, pady=(0, 20))

        self.button1 = ctk.CTkButton(
            self, 
            text="Gebärdensprache", 
            font=("Roboto", 22, "bold"),
            height=80,
            width=400,
            corner_radius=15,
            command=lambda: master.switch_frame(CameraFrame)
        )
        self.button1.grid(row=2, column=0, pady=15)

        self.button2 = ctk.CTkButton(
            self, 
            text="Morsecode", 
            font=("Roboto", 22, "bold"),
            height=80,
            width=400,
            corner_radius=15,
            fg_color="#333333",
            hover_color="#444444",
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

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()