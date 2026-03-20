import os
import cv2
import customtkinter
import mediapipe as mp
from PIL import Image, ImageTk

from finger_counter import FingerCounter


BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MEME_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "Absolute_Cinema.png")


class MemeMovementTestFrame(customtkinter.CTkFrame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)

        self.go_back_callback = go_back_callback
        self.cam = None
        self.landmarker = None
        self.frame_timestamp_ms = 0
        self.counter = FingerCounter()
        self.gesture_start_time = None
        self.face_detector = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        )
        self.meme_image_rgb = None

        if os.path.exists(MEME_IMAGE_PATH):
            meme_bgr = cv2.imread(MEME_IMAGE_PATH)
            if meme_bgr is not None:
                self.meme_image_rgb = cv2.cvtColor(meme_bgr, cv2.COLOR_BGR2RGB)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = customtkinter.CTkLabel(
            self,
            text="Meme Movement Test",
            font=("Bahnschrift", 30, "bold"),
            text_color="#10b981"
        )
        self.title_label.grid(row=0, column=0, pady=(15, 8))

        self.video_label = customtkinter.CTkLabel(self, text="Kamera nicht gestartet")
        self.video_label.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        self.status_label = customtkinter.CTkLabel(
            self,
            text="Show both open palms next to your head",
            font=("Roboto", 18, "bold"),
            text_color="#94a3b8"
        )
        self.status_label.grid(row=2, column=0, pady=(2, 8))

        self.hint_label = customtkinter.CTkLabel(
            self,
            text="Example trigger: both hands visible, open, near left/right side of head",
            font=("Roboto", 12),
            text_color="#64748b"
        )
        self.hint_label.grid(row=3, column=0, pady=(0, 8))

        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=(4, 14))

        customtkinter.CTkButton(button_frame, text="Start Camera", command=self.start_camera).pack(side="left", padx=8)
        customtkinter.CTkButton(button_frame, text="Stop Camera", command=self.stop_camera).pack(side="left", padx=8)
        customtkinter.CTkButton(button_frame, text="Zurück", command=self.go_back).pack(side="left", padx=8)

    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
        self.frame_timestamp_ms = 0

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = HandLandmarker.create_from_options(options)
        self.update_frame()

    def stop_camera(self):
        if self.cam:
            self.cam.release()
            self.cam = None

        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None

        self.gesture_start_time = None

    def _get_face_box(self, frame_rgb):
        gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) == 0:
            return None

        largest_face = max(faces, key=lambda box: box[2] * box[3])
        x, y, width, height = largest_face
        img_h, img_w = gray.shape

        x_min = max(0.0, x / img_w)
        y_min = max(0.0, y / img_h)
        x_max = min(1.0, (x + width) / img_w)
        y_max = min(1.0, (y + height) / img_h)

        return x_min, y_min, x_max, y_max

    def go_back(self):
        self.stop_camera()
        self.grid_forget()

        if self.go_back_callback:
            self.go_back_callback()

    def _is_open_palm(self, landmarks):
        right_count = self.counter.count_fingers(landmarks, "Right")
        left_count = self.counter.count_fingers(landmarks, "Left")
        return max(right_count, left_count) >= 4

    def _hand_center(self, hand_landmarks):
        x_mean = sum(point.x for point in hand_landmarks) / len(hand_landmarks)
        y_mean = sum(point.y for point in hand_landmarks) / len(hand_landmarks)
        return x_mean, y_mean

    def _detect_absolute_cinema(self, detection_result, face_box):
        if not face_box:
            return False

        if not detection_result.hand_landmarks or len(detection_result.hand_landmarks) < 2:
            return False

        x_min, y_min, x_max, y_max = face_box
        side_outer_tolerance = 0.30
        side_inner_tolerance = 0.07
        y_upper_tolerance = 0.45
        y_lower_tolerance = 0.20

        left_ok = False
        right_ok = False

        for hand_landmarks in detection_result.hand_landmarks:
            if not self._is_open_palm(hand_landmarks):
                continue

            hand_center_x, hand_center_y = self._hand_center(hand_landmarks)

            near_head_height = (y_min - y_upper_tolerance) <= hand_center_y <= (y_max + y_lower_tolerance)
            in_left_band = (x_min - side_outer_tolerance) <= hand_center_x <= (x_min + side_inner_tolerance)
            in_right_band = (x_max - side_inner_tolerance) <= hand_center_x <= (x_max + side_outer_tolerance)

            if in_left_band and near_head_height:
                left_ok = True

            if in_right_band and near_head_height:
                right_ok = True

        return left_ok and right_ok

    def _draw_landmarks(self, rgb_image, detection_result):
        if not detection_result.hand_landmarks:
            return rgb_image

        h, w, _ = rgb_image.shape
        for hand_landmarks in detection_result.hand_landmarks:
            for start_idx, end_idx in HAND_CONNECTIONS:
                start = hand_landmarks[start_idx]
                end = hand_landmarks[end_idx]
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(rgb_image, start_point, end_point, (0, 255, 0), 2)

            for landmark in hand_landmarks:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(rgb_image, (cx, cy), 5, (255, 0, 0), -1)

        return rgb_image

    def _overlay_meme(self, frame_rgb):
        if self.meme_image_rgb is None:
            return frame_rgb

        frame_h, frame_w, _ = frame_rgb.shape
        target_w = min(360, frame_w - 20)
        aspect = self.meme_image_rgb.shape[0] / self.meme_image_rgb.shape[1]
        target_h = int(target_w * aspect)

        resized_meme = cv2.resize(self.meme_image_rgb, (target_w, target_h))

        x_start = (frame_w - target_w) // 2
        y_start = 10
        y_end = min(frame_h, y_start + target_h)
        x_end = x_start + target_w

        overlay_h = y_end - y_start
        if overlay_h <= 0:
            return frame_rgb

        frame_rgb[y_start:y_end, x_start:x_end] = resized_meme[:overlay_h, :target_w]
        return frame_rgb

    def update_frame(self):
        if not (self.cam and self.cam.isOpened()):
            return

        success, frame_img = self.cam.read()
        if not success:
            self.after(10, self.update_frame)
            return

        frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)

        if self.landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            self.frame_timestamp_ms += 33

            result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)
            frame_rgb = self._draw_landmarks(frame_rgb, result)
            face_box = self._get_face_box(frame_rgb)

            if face_box:
                h, w, _ = frame_rgb.shape
                x_min, y_min, x_max, y_max = face_box
                p1 = (int(x_min * w), int(y_min * h))
                p2 = (int(x_max * w), int(y_max * h))
                cv2.rectangle(frame_rgb, p1, p2, (0, 180, 255), 2)
            else:
                self.gesture_start_time = None
                self.status_label.configure(text="Face not detected", text_color="#f87171")

            is_cinema_pose = self._detect_absolute_cinema(result, face_box)

            if is_cinema_pose:
                self.status_label.configure(text="ABSOLUTE CINEMA", text_color="#facc15")
                frame_rgb = self._overlay_meme(frame_rgb)
            else:
                if face_box:
                    self.gesture_start_time = None
                    self.status_label.configure(
                        text="Show both open palms next to your head",
                        text_color="#94a3b8"
                    )

        img = Image.fromarray(frame_rgb).resize((640, 480))
        tk_img = ImageTk.PhotoImage(img)
        self.video_label.configure(image=tk_img, text="")
        self.video_label.image = tk_img

        self.after(10, self.update_frame)


if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root = customtkinter.CTk()
    root.geometry("900x700")
    root.title("Meme Movement Test")

    frame = MemeMovementTestFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
