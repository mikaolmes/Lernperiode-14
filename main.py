import customtkinter as ctk
from SignLanguage import CameraFrame
from morsecode import MorseCodeFrame
from meme_movement import MemeMovementTestFrame
from settings_frame import SettingsFrame
from alphabet_frame import AlphabetFrame 
from MorseCodeAlphabetFrame import MorseAL_Frame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green") 

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sign & Morse Translator")
        self.geometry("800x900") # Etwas höher für den zusätzlichen Button

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Globaler Hotkey: Esc bringt einen immer zurück zum Menü
        self.bind("<Escape>", lambda e: self.show_main_menu())
        
        # Ziffern-Hotkeys für das schnelle Wechseln (Jetzt 1-5)
        self.bind("1", lambda e: self.switch_frame(CameraFrame))
        self.bind("2", lambda e: self.switch_frame(MorseCodeFrame))
        self.bind("3", lambda e: self.switch_frame(MemeMovementTestFrame))
        self.bind("4", lambda e: self.switch_frame(SettingsFrame))
        self.bind("5", lambda e: self.switch_frame(AlphabetFrame))
        self.bind("6", lambda e: self.switch_frame(MorseAL_Frame))

        self.current_frame = None
        self.show_main_menu()

    def switch_frame(self, new_frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        
        # Erstellt eine neue Instanz des gewählten Frames
        self.current_frame = new_frame_class(self, self.show_main_menu)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, master, show_main_menu_callback):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)

        # Titel
        self.label = ctk.CTkLabel(
            self, 
            text="Sign & Morse Translator", 
            font=("Bahnschrift", 40, "bold"),
            text_color="#10b981"
        )
        self.label.grid(row=0, column=0, pady=(50, 30))

        # --- Button 1: Sign Language ---
        self.button1 = ctk.CTkButton(
            self,
            text="Sign Language (1)",
            font=("Roboto", 22, "bold"),
            height=70, width=400, corner_radius=15,
            command=lambda: master.switch_frame(CameraFrame)
        )
        self.button1.grid(row=1, column=0, pady=10)

        # --- Button 2: Alphabet Referenz (DEIN NEUER TEIL) ---
        self.button2 = ctk.CTkButton(
            self,
            text="Morse Code (2)",
            font=("Roboto", 22, "bold"),
            height=70, width=400, corner_radius=15,
            fg_color="#333333", hover_color="#444444",
            command=lambda: master.switch_frame(MorseCodeFrame)
        )
        self.button2.grid(row=2, column=0, pady=10)

        
        # --- Button 3: Morse Code ---
        self.button3 = ctk.CTkButton(
            self,
            text="Meme Movement Test (3)",
            font=("Roboto", 22, "bold"),
            height=70, width=400, corner_radius=15,
            fg_color="#1f2937", hover_color="#374151",
            command=lambda: master.switch_frame(MemeMovementTestFrame)
        )
        self.button3.grid(row=3, column=0, pady=10)

        # --- Button 4: Meme Movement ---
        self.button4 = ctk.CTkButton(
                self,
                text="Settings (4)",
                font=("Roboto", 22, "bold"),
                height=70, width=400, corner_radius=15,
                fg_color="transparent", border_width=2,
                command=lambda: master.switch_frame(SettingsFrame)
            )
        self.button4.grid(row=4, column=0, pady=10)

        # --- Button 5: Settings ---
        self.button_alpha = ctk.CTkButton(
            self,
            text="Alphabet Lernen (5)",
            font=("Roboto", 22, "bold"),
            height=70, width=400, corner_radius=15,
            fg_color="#2563eb", # Blau zur optischen Abhebung
            hover_color="#1d4ed8",
            command=lambda: master.switch_frame(AlphabetFrame)
        )
        self.button_alpha.grid(row=5, column=0, pady=10)

        # --- Button 6: Morse Code Alphatbet ---
        self.button_button6 =ctk.CTkButton(
            self,
            text="Morse Code Alphabet (6)",
            font=("Roboto", 22, "bold"),
            height=70, width=400, corner_radius=15,
            fg_color="#10b981",
            hover_color="#059669",
            command=lambda: master.switch_frame(MorseAL_Frame)
        )
        self.button_button6.grid(row=6, column=0, pady=10)

        # Footer Info
        self.info_label = ctk.CTkLabel(
            self, 
            text="Nutze Tasten 1-6 zum schnellen Wechseln", 
            font=("Arial", 12), text_color="gray"
        )
        self.info_label.grid(row=7, column=0, pady=20)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()