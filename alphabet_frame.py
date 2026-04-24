import customtkinter as ctk
from PIL import Image
import os

class AlphabetFrame(ctk.CTkFrame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback

        # Das Layout der Seite
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Titel ---
        self.label = ctk.CTkLabel(
            self, 
            text="Gebärdensprache Alphabet", 
            font=("Bahnschrift", 32, "bold"),
            text_color="#10b981"
        )
        self.label.grid(row=0, column=0, pady=20)

        # --- Scrollbarer Bereich für die Buchstaben ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Referenz A-Z")
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Konfiguriere Spalten im Scroll-Bereich (z.B. 4 Spalten)
        for i in range(4):
            self.scroll_frame.grid_columnconfigure(i, weight=1)

        # --- Alphabet laden ---
        self.load_alphabet()

        # --- Zurück Button ---
        self.back_btn = ctk.CTkButton(
            self,
            text="Zurück zum Menü",
            font=("Roboto", 18, "bold"),
            height=50,
            command=self.go_back_callback
        )
        self.back_btn.grid(row=2, column=0, pady=20)

    def load_alphabet(self):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        image_folder = "alphabet_images" # Hier müssen deine Bilder rein

        for index, letter in enumerate(alphabet):
            row = index // 4
            col = index % 4

            # Einzelner Container für jeden Buchstaben
            char_card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=10)
            char_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Buchstabe als Text
            l_label = ctk.CTkLabel(char_card, text=letter, font=("Arial", 20, "bold"))
            l_label.pack(pady=5)

            # Bild laden
            img_path = os.path.join(os.path.dirname(__file__), image_folder, f"{letter}.jpg")
            
            if os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(120, 120))
                    img_display = ctk.CTkLabel(char_card, text="", image=ctk_img)
                    img_display.pack(pady=5, padx=10)
                except:
                    self.show_placeholder(char_card)
            else:
                self.show_placeholder(char_card)

    def show_placeholder(self, parent):
        placeholder = ctk.CTkLabel(parent, text="Bild fehlt", text_color="gray", font=("Arial", 12))
        placeholder.pack(pady=40, padx=10)