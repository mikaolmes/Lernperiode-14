import customtkinter
import cv2  # OpenCV für Kamerazugriff
from PIL import Image, ImageTk  # Für Bildumwandlung in Tkinter
import mediapipe as mp  # MediaPipe für Handerkennung
from mediapipe.tasks.python import vision
import os
import time
from tkinter import filedialog

# Import sign language letter recognizer
from sign_recognizer import SignLanguageRecognizer

# ================================
# MediaPipe Tasks API Setup
# ================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Daumen
    (0, 5), (5, 6), (6, 7), (7, 8),        # Zeigefinger
    (0, 9), (9, 10), (10, 11), (11, 12),   # Mittelfinger
    (0, 13), (13, 14), (14, 15), (15, 16), # Ringfinger
    (0, 17), (17, 18), (18, 19), (19, 20), # Kleiner Finger
    (5, 9), (9, 13), (13, 17)              # Handfläche
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

class CameraFrame(customtkinter.CTkFrame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)

        # Callback-Funktion für Zurück-Button
        self.go_back_callback = go_back_callback

        self.cam = None
        self.landmarker = None
        self.frame_timestamp_ms = 0
        
        # Sign language recognizer
        self.recognizer = SignLanguageRecognizer()
        self.current_letters = []

        # Tracking for confirmed sign
        self.last_sign = None
        self.sign_start_time = None
        self.confirmed_sign = None
        self.sentence_history = ""
        
        # Fast Mode Variables
        self.time_normal = 3.0
        self.time_fast = 0.5
        self.current_confirm_time = self.time_normal

        # ========== Layout ==========
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Title ---
        self.title_label = customtkinter.CTkLabel(
            self,
            text="Sign Language Translator",
            font=("Bahnschrift", 32, "bold"),
            text_color="#10b981"
        )
        self.title_label.grid(row=0, column=0, pady=(15, 5), sticky="n")

        # --- Content container ---
        content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=3)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # --- Left side: Current letter label ---
        self.current_letter_label = customtkinter.CTkLabel(
            content_frame,
            text="–",
            font=("Bahnschrift", 48, "bold"),
            text_color="#facc15",
            width=80,
            height=60,
            fg_color="#333333",
            corner_radius=10
        )
        self.current_letter_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 5))

        # --- Left side: Camera feed ---
        self.label = customtkinter.CTkLabel(content_frame, text="Kamera nicht gestartet")
        self.label.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # --- Right side: Sentence history panel ---
        right_panel = customtkinter.CTkFrame(content_frame, fg_color="#2b2b2b", corner_radius=10)
        right_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        right_title = customtkinter.CTkLabel(
            right_panel,
            text="Erkannte Buchstaben",
            font=("Roboto", 16, "bold"),
            text_color="#94a3b8"
        )
        right_title.grid(row=0, column=0, pady=(15, 5), padx=10)

        self.sentence_textbox = customtkinter.CTkTextbox(
            right_panel,
            font=("Bahnschrift", 22),
            text_color="#10b981",
            fg_color="#1e1e1e",
            corner_radius=8,
            wrap="word"
        )
        self.sentence_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.sentence_textbox.configure(state="disabled")
        
        # --- Progress Bar ---
        self.progress_bar = customtkinter.CTkProgressBar(right_panel, width=200)
        self.progress_bar.grid(row=2, column=0, pady=10, padx=10)
        self.progress_bar.set(0)

        right_btn_frame = customtkinter.CTkFrame(right_panel, fg_color="transparent")
        right_btn_frame.grid(row=3, column=0, pady=(5, 10))

        customtkinter.CTkButton(right_btn_frame, text="Space", width=60, command=self.add_space).pack(side="left", padx=2)
        customtkinter.CTkButton(right_btn_frame, text="Copy", width=60, command=self.copy_to_clipboard).pack(side="left", padx=2)
        customtkinter.CTkButton(right_btn_frame, text="DL", width=50, command=self.download_history).pack(side="left", padx=2)
        customtkinter.CTkButton(right_btn_frame, text="Clear", width=60, fg_color="#dc2626", hover_color="#b91c1c", command=self.clear_sentence).pack(side="left", padx=2)

        self.confirmed_hint = customtkinter.CTkLabel(
            right_panel,
            text=f"Halte ein Zeichen {self.current_confirm_time}s lang",
            font=("Roboto", 11),
            text_color="#64748b"
        )
        self.confirmed_hint.grid(row=4, column=0, pady=(0, 10))

        # --- Button bar ---
        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)

        customtkinter.CTkButton(btn_frame, text="Start (Space)", command=self.start_camera).pack(side="left", padx=10)
        customtkinter.CTkButton(btn_frame, text="Stop", command=self.stop_camera).pack(side="left", padx=10)
        
        # Fast Mode Button
        self.fast_mode_btn = customtkinter.CTkButton(
            btn_frame, 
            text="Fast Mode: OFF", 
            fg_color="#333333",
            command=self.toggle_fast_mode
        )
        self.fast_mode_btn.pack(side="left", padx=10)

        customtkinter.CTkButton(btn_frame, text="Zurück (Esc)", command=self.go_back).pack(side="left", padx=10)

        # Bindings
        self.master.bind("<space>", lambda e: self.toggle_camera())
        self.master.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.master.bind("c", lambda e: self.clear_sentence())
        self.master.bind("f", lambda e: self.toggle_fast_mode())
        self.master.bind("d", lambda e: self.download_history())

    # ================================
    # Logik: Download Funktion
    # ================================
    def download_history(self):
        text_to_save = self.sentence_history.strip()
        if not text_to_save:
            self.confirmed_hint.configure(text="Nichts zum Speichern!", text_color="#dc2626")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
            title="Übersetzung speichern",
            initialfile="uebersetzung.txt"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("--- Gebärdensprache Protokoll ---\n")
                    file.write(f"Datum: {time.strftime('%d.%m.%Y %H:%M:%S')}\n\n")
                    file.write(text_to_save)
                self.confirmed_hint.configure(text="Datei gespeichert!", text_color="#10b981")
            except Exception as e:
                self.confirmed_hint.configure(text=f"Fehler: {e}", text_color="#dc2626")

    def toggle_fast_mode(self, event=None):
        if self.current_confirm_time == self.time_normal:
            self.current_confirm_time = self.time_fast
            self.fast_mode_btn.configure(text="Fast Mode: ON", fg_color="#facc15", text_color="black")
        else:
            self.current_confirm_time = self.time_normal
            self.fast_mode_btn.configure(text="Fast Mode: OFF", fg_color="#333333", text_color="white")
        self.confirmed_hint.configure(text=f"Halte ein Zeichen {self.current_confirm_time}s lang")

    def _update_sentence_display(self):
        self.sentence_textbox.configure(state="normal")
        self.sentence_textbox.delete("1.0", "end")
        self.sentence_textbox.insert("1.0", self.sentence_history)
        self.sentence_textbox.see("end")
        self.sentence_textbox.configure(state="disabled")

    def add_space(self):
        self.sentence_history += " "
        self._update_sentence_display()

    def clear_sentence(self):
        self.sentence_history = ""
        self.confirmed_sign = None
        self._update_sentence_display()
        self.confirmed_hint.configure(text="Satz gelöscht", text_color="#dc2626")
        self.after(1000, lambda: self.confirmed_hint.configure(text=f"Halte ein Zeichen {self.current_confirm_time}s lang", text_color="#64748b"))

    def toggle_camera(self):
        if self.cam is None: self.start_camera()
        else: self.stop_camera()

    def copy_to_clipboard(self):
        content = self.sentence_history
        if content:
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            self.confirmed_hint.configure(text="Kopiert!", text_color="#10b981")
            self.after(1000, lambda: self.confirmed_hint.configure(text=f"Halte ein Zeichen {self.current_confirm_time}s lang", text_color="#64748b"))

    def start_camera(self):
        if self.cam is None:
            self.cam = cv2.VideoCapture(0)  
            self.frame_timestamp_ms = 0
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=MODEL_PATH),
                running_mode=VisionRunningMode.VIDEO, num_hands=4,
                min_hand_detection_confidence=0.3, min_hand_presence_confidence=0.3, min_tracking_confidence=0.4,
            )
            self.landmarker = HandLandmarker.create_from_options(options)
            self.update_frame()

    def stop_camera(self):
        if self.cam: self.cam.release(); self.cam = None
        if self.landmarker: self.landmarker.close(); self.landmarker = None
        self.label.configure(image="", text="Kamera gestoppt")
        self.progress_bar.set(0)

    def go_back(self):
        self.stop_camera()  
        self.grid_forget()  
        if self.go_back_callback: self.go_back_callback()

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        if detection_result.hand_landmarks:
            h, w, _ = rgb_image.shape
            for hand_idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                for connection in HAND_CONNECTIONS:
                    start = hand_landmarks[connection[0]]
                    end = hand_landmarks[connection[1]]
                    cv2.line(rgb_image, (int(start.x * w), int(start.y * h)), (int(end.x * w), int(end.y * h)), (0, 255, 0), 2)
                for idx, landmark in enumerate(hand_landmarks):
                    cv2.circle(rgb_image, (int(landmark.x * w), int(landmark.y * h)), 3, (0, 255, 255), -1)
        return rgb_image

    def update_frame(self):
        if self.cam and self.cam.isOpened():
            ret, frame_img = self.cam.read()
            if ret:
                frame_img = cv2.flip(frame_img, 1)
                frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                if self.landmarker:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                    self.frame_timestamp_ms += 33
                    result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)
                    self.current_letters = self.recognizer.recognize_from_result(result)

                    if self.current_letters:
                        recognized_text = "".join(self.current_letters)
                        self.current_letter_label.configure(text=recognized_text)
                        
                        if recognized_text == self.last_sign:
                            if self.sign_start_time:
                                elapsed = time.time() - self.sign_start_time
                                progress = min(1.0, elapsed / self.current_confirm_time)
                                self.progress_bar.set(progress)
                                
                                if elapsed >= self.current_confirm_time:
                                    if self.confirmed_sign != recognized_text:
                                        self.confirmed_sign = recognized_text
                                        self.sentence_history += recognized_text
                                        self._update_sentence_display()
                        else:
                            self.last_sign = recognized_text
                            self.sign_start_time = time.time()
                            self.confirmed_sign = None
                            self.progress_bar.set(0)
                    else:
                        self.current_letter_label.configure(text="–")
                        self.last_sign = None
                        self.sign_start_time = None
                        self.progress_bar.set(0)

                    frame_rgb = self.draw_landmarks_on_image(frame_rgb, result)

                img = Image.fromarray(frame_rgb).resize((640, 480))
                ctk_img = ImageTk.PhotoImage(img)
                self.label.configure(image=ctk_img, text="")
                self.label.image = ctk_img  
            self.after(10, self.update_frame)