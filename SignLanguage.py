import customtkinter
import cv2  # OpenCV für Kamerazugriff
from PIL import Image, ImageTk  # Für Bildumwandlung in Tkinter
import mediapipe as mp  # MediaPipe für Handerkennung
from mediapipe.tasks.python import vision
import os
import time

# Import sign language letter recognizer
from sign_recognizer import SignLanguageRecognizer

# ================================
# MediaPipe Tasks API Setup
# ================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Verbindungen zwischen den 21 Hand-Landmarks
# (Damit Linien zwischen Punkten gezeichnet werden können)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Daumen
    (0, 5), (5, 6), (6, 7), (7, 8),        # Zeigefinger
    (0, 9), (9, 10), (10, 11), (11, 12),   # Mittelfinger
    (0, 13), (13, 14), (14, 15), (15, 16), # Ringfinger
    (0, 17), (17, 18), (18, 19), (19, 20), # Kleiner Finger
    (5, 9), (9, 13), (13, 17)              # Handfläche
]

# Pfad zum MediaPipe Modell (.task Datei muss im selben Ordner liegen)
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

        # Tracking for 3-second confirmed sign
        self.last_sign = None
        self.sign_start_time = None
        self.confirmed_sign = None
        self.sentence_history = ""

        # ========== Layout ==========
        # Row 0: Title (spans full width)
        # Row 1: Content area (left camera + right panel)
        # Row 2: Buttons
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

        # --- Content container (left + right) ---
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

        right_btn_frame = customtkinter.CTkFrame(right_panel, fg_color="transparent")
        right_btn_frame.grid(row=2, column=0, pady=(5, 10))

        space_btn = customtkinter.CTkButton(
            right_btn_frame,
            text="Leerzeichen",
            width=100,
            command=self.add_space
        )
        space_btn.pack(side="left", padx=5)

        clear_btn = customtkinter.CTkButton(
            right_btn_frame,
            text="Löschen",
            width=80,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self.clear_sentence
        )
        clear_btn.pack(side="left", padx=5)

        self.confirmed_hint = customtkinter.CTkLabel(
            right_panel,
            text="Halte ein Zeichen 3s lang",
            font=("Roboto", 11),
            text_color="#64748b"
        )
        self.confirmed_hint.grid(row=3, column=0, pady=(0, 10))

        # --- Button bar ---
        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)

        start_btn = customtkinter.CTkButton(
            btn_frame,
            text="Start Camera",
            command=self.start_camera
        )
        start_btn.pack(side="left", padx=10)

        stop_btn = customtkinter.CTkButton(
            btn_frame,
            text="Stop Camera",
            command=self.stop_camera
        )
        stop_btn.pack(side="left", padx=10)

        back_btn = customtkinter.CTkButton(
            btn_frame,
            text="Zurück",
            command=self.go_back
        )
        back_btn.pack(side="left", padx=10)

    # ================================
    # Sentence helpers
    # ================================
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

    # ================================
    # Kamera starten
    # ================================
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)  
        self.frame_timestamp_ms = 0

        # MediaPipe HandLandmarker konfigurieren
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=4,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = HandLandmarker.create_from_options(options)
        self.update_frame()

    # ================================
    # Kamera stoppen
    # ================================
    def stop_camera(self):
        if self.cam:
            self.cam.release()
            self.cam = None

        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None

    # ================================
    # Zurück-Button Funktion
    # ================================
    def go_back(self):
        self.stop_camera()  
        self.grid_forget()  

        if self.go_back_callback:
            self.go_back_callback()  # Zurück zum Hauptmenü

    # ================================
    # Hand-Landmarks zeichnen
    # ================================
    def draw_landmarks_on_image(self, rgb_image, detection_result):
        if detection_result.hand_landmarks:
            h, w, _ = rgb_image.shape

            for hand_landmarks in detection_result.hand_landmarks:

                # Linien zeichnen
                for connection in HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    start = hand_landmarks[start_idx]
                    end = hand_landmarks[end_idx]

                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))

                    cv2.line(rgb_image, start_point, end_point, (0, 255, 0), 2)

                # Punkte zeichnen
                for landmark in hand_landmarks:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(rgb_image, (cx, cy), 5, (255, 0, 0), -1)
        
        # Display recognized letter on screen
        if self.current_letters:
            text = "  ".join(self.current_letters)
            cv2.putText(
                rgb_image,
                text,
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.0,
                (255, 255, 0),
                3,
                cv2.LINE_AA
            )

        return rgb_image

    # ================================
    # Frame-Update Loop
    # ================================
    def update_frame(self):
        if self.cam and self.cam.isOpened():
            ret, frame_img = self.cam.read()

            if ret:
                # OpenCV → RGB konvertieren
                frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)

                # Handerkennung ausführen
                if self.landmarker:
                    mp_image = mp.Image(
                        image_format=mp.ImageFormat.SRGB,
                        data=frame_rgb
                    )

                    # VIDEO-Modus benötigt Timestamp
                    self.frame_timestamp_ms += 33  # ~30 FPS

                    result = self.landmarker.detect_for_video(
                        mp_image,
                        self.frame_timestamp_ms
                    )

                    # Recognize sign language letters
                    self.current_letters = self.recognizer.recognize_from_result(result)

                    if self.current_letters:
                        recognized_text = "".join(self.current_letters)
                        self.current_letter_label.configure(text=recognized_text)

                        # Track how long the same sign is shown
                        current_sign = recognized_text
                        if current_sign == self.last_sign:
                            if self.sign_start_time and (time.time() - self.sign_start_time) >= 3.0:
                                if self.confirmed_sign != current_sign:
                                    self.confirmed_sign = current_sign
                                    self.sentence_history += current_sign
                                    self._update_sentence_display()
                        else:
                            self.last_sign = current_sign
                            self.sign_start_time = time.time()
                            self.confirmed_sign = None
                    else:
                        self.current_letter_label.configure(text="–")
                        self.last_sign = None
                        self.sign_start_time = None

                    # Landmark-Punkte einzeichnen
                    frame_rgb = self.draw_landmarks_on_image(
                        frame_rgb,
                        result
                    )

                # Bild für Tkinter vorbereiten
                img = Image.fromarray(frame_rgb)
                img = img.resize((640, 480))
                ctk_img = ImageTk.PhotoImage(img)

                self.label.configure(image=ctk_img, text="")
                self.label.image = ctk_img  


            self.after(10, self.update_frame)

if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root = customtkinter.CTk()
    root.geometry("900x700")
    root.title("Sign Language Camera")

    frame = CameraFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()