import customtkinter
import cv2  # OpenCV für Kamerazugriff
from PIL import Image, ImageTk  # Für Bildumwandlung in Tkinter
import mediapipe as mp  # MediaPipe für Handerkennung
from mediapipe.tasks.python import vision
import os

# Import finger counter module (for counting 1-5)
from finger_counter import FingerCounter

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
        
        # Finger counter instance
        self.finger_counter = FingerCounter()
        self.current_finger_count = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Bildanzeige-Label
        self.label = customtkinter.CTkLabel(self, text="")
        self.label.grid(row=0, column=0, sticky="nsew", pady=10)

        # Button-Container
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.grid(row=1, column=0, pady=10)

        # Kamera starten
        start_btn = customtkinter.CTkButton(
            btn_frame,
            text="Start Camera",
            command=self.start_camera
        )
        start_btn.pack(side="left", padx=10)

        # Kamera stoppen
        stop_btn = customtkinter.CTkButton(
            btn_frame,
            text="Stop Camera",
            command=self.stop_camera
        )
        stop_btn.pack(side="left", padx=10)

        # Zurück zum Hauptmenü
        back_btn = customtkinter.CTkButton(
            self,
            text="Zurück",
            command=self.go_back
        )
        back_btn.grid(row=2, column=0, pady=10)

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
        
        # Display finger count on screen
        if self.current_finger_count > 0:
            text = f"Fingers: {self.current_finger_count}"
            cv2.putText(
                rgb_image, 
                text, 
                (10, 50),  # Top-left position
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,  # Font size
                (255, 255, 0),  # Cyan color
                3,  # Thickness
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

                    # Count fingers
                    total_fingers, individual_counts = self.finger_counter.count_all_hands(result)
                    self.current_finger_count = total_fingers

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