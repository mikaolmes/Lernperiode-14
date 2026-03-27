import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)
        self.go_back_callback = go_back_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Platz für die Liste

        # --- Titel ---
        self.label = ctk.CTkLabel(
            self, 
            text="Einstellungen & Hilfe", 
            font=("Bahnschrift", 32, "bold"),
            text_color="#10b981"
        )
        self.label.grid(row=0, column=0, pady=20)

        # --- Hotkey Erklärung (Scrollable Bereich) ---
        self.info_box = ctk.CTkScrollableFrame(self, label_text="Tastenkombinationen (Hotkeys)")
        self.info_box.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")

        self.add_hotkey_info("ESC", "Zurück zum Hauptmenü")
        self.add_hotkey_info("Leertaste", "Kamera Start / Stop")
        self.add_hotkey_info("F", "Fast Mode umschalten (0.5s statt 3.0s)")
        self.add_hotkey_info("Strg + C", "Erkannten Text in Zwischenablage kopieren")
        self.add_hotkey_info("C", "Aktuellen Satz löschen")
        self.add_hotkey_info("1, 2, 3, 4", "Direktwahl der Tools im Menü")

        # --- Back Button ---
        self.back_btn = ctk.CTkButton(
            self,
            text="Zurück (Esc)",
            font=("Roboto", 18, "bold"),
            height=50,
            width=200,
            command=self.go_back
        )
        self.back_btn.grid(row=2, column=0, pady=30)

        # Lokales Binding für Esc in diesem Frame
        self.master.bind("<Escape>", lambda e: self.go_back())

    def add_hotkey_info(self, key, description):
        """Hilfsfunktion um Zeilen zur Info-Box hinzuzufügen"""
        row = ctk.CTkFrame(self.info_box, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=10)
        
        key_label = ctk.CTkLabel(row, text=key, font=("Roboto", 14, "bold"), text_color="#facc15", width=100)
        key_label.pack(side="left")
        
        desc_label = ctk.CTkLabel(row, text=f"→ {description}", font=("Roboto", 14))
        desc_label.pack(side="left", padx=10)

    def go_back(self):
        self.grid_forget()
        if self.go_back_callback:
            self.go_back_callback()