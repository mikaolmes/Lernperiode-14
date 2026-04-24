import customtkinter as ctk
import time
import threading
import os

# Versuche winsound für Windows zu importieren (für den Ton)
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# Das Morsecode-Wörterbuch (A-Z)
MORSE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..'
}

class MorseAL_Frame(ctk.CTkFrame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)
        self.go_back_callback = go_back_callback

        # Das Layout der Seite
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Titel ---
        self.label = ctk.CTkLabel(
            self, 
            text="Morsecode Alphabet", 
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
        # Wir gehen durch unser Wörterbuch statt durch einen normalen String
        for index, (letter, morse_code) in enumerate(MORSE_DICT.items()):
            row = index // 4
            col = index % 4

            # Einzelner Container für jeden Buchstaben
            char_card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b", corner_radius=10)
            char_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Buchstabe als großer Text
            l_label = ctk.CTkLabel(char_card, text=letter, font=("Arial", 28, "bold"))
            l_label.pack(pady=(15, 5))

            # --- Vorschlag 3: Visuelle Punkte und Striche ---
            # Ein Container für die grafischen Morse-Zeichen
            visual_frame = ctk.CTkFrame(char_card, fg_color="transparent")
            visual_frame.pack(pady=10)

            for symbol in morse_code:
                if symbol == '.':
                    # Zeichne einen Punkt (kleines Quadrat mit abgerundeten Ecken = Kreis)
                    dot = ctk.CTkFrame(visual_frame, width=12, height=12, corner_radius=6, fg_color="#10b981")
                    dot.pack(side="left", padx=3)
                elif symbol == '-':
                    # Zeichne einen Strich (breiteres Rechteck)
                    dash = ctk.CTkFrame(visual_frame, width=35, height=12, corner_radius=6, fg_color="#10b981")
                    dash.pack(side="left", padx=3)

            # --- Vorschlag 4: Der Play Button ---
            # Wir übergeben den jeweiligen Morsecode an unsere Abspiel-Funktion
            play_btn = ctk.CTkButton(
                char_card, 
                text="▶ Play", 
                width=80, 
                fg_color="#3b82f6", 
                hover_color="#2563eb",
                command=lambda m=morse_code: self.play_audio_thread(m)
            )
            play_btn.pack(pady=(5, 15))

    # --- Audio Funktionen ---
    def play_audio_thread(self, morse_code):
        # Startet den Ton in einem Hintergrund-Thread, damit die GUI nicht einfriert
        thread = threading.Thread(target=self._play_morse_sound, args=(morse_code,))
        thread.start()

    def _play_morse_sound(self, morse_code):
        dot_duration = 150  # Dauer eines Punktes in Millisekunden
        dash_duration = dot_duration * 3 # Ein Strich ist 3x so lang wie ein Punkt
        pause_duration = dot_duration # Pause zwischen den Signalen
        frequency = 800 # Tonhöhe in Hertz

        for symbol in morse_code:
            if symbol == '.':
                if HAS_WINSOUND:
                    winsound.Beep(frequency, dot_duration)
                else:
                    time.sleep(dot_duration / 1000)
            elif symbol == '-':
                if HAS_WINSOUND:
                    winsound.Beep(frequency, dash_duration)
                else:
                    time.sleep(dash_duration / 1000)
            
            # Kurze Pause nach jedem Signal (damit sie nicht ineinander fließen)
            time.sleep(pause_duration / 1000)