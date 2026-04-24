import os
import time
import math
import cv2
import customtkinter
import mediapipe as mp
from collections import deque
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
ABSOLUTE_CINEMA_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "Absolute_Cinema.png")
GORILLA_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "Gorilla_MiddleFinger.png")
NERD_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "Nerd_Meme.png")
BOI_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "boiii.png")
SIX_SEVEN_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "memes", "67_meme.png")


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
        self.absolute_cinema_image_rgb = None
        self.gorilla_image_rgb = None
        self.nerd_image_rgb = None
        self.boi_image_rgb = None
        self.six_seven_image_rgb = None
        self.movement_history = deque(maxlen=75)
        self.last_dynamic_trigger_time = 0.0

        if os.path.exists(ABSOLUTE_CINEMA_IMAGE_PATH):
            meme_bgr = cv2.imread(ABSOLUTE_CINEMA_IMAGE_PATH)
            if meme_bgr is not None:
                self.absolute_cinema_image_rgb = cv2.cvtColor(meme_bgr, cv2.COLOR_BGR2RGB)

        if os.path.exists(GORILLA_IMAGE_PATH):
            gorilla_bgr = cv2.imread(GORILLA_IMAGE_PATH)
            if gorilla_bgr is not None:
                self.gorilla_image_rgb = cv2.cvtColor(gorilla_bgr, cv2.COLOR_BGR2RGB)

        if os.path.exists(NERD_IMAGE_PATH):
            nerd_bgr = cv2.imread(NERD_IMAGE_PATH)
            if nerd_bgr is not None:
                self.nerd_image_rgb = cv2.cvtColor(nerd_bgr, cv2.COLOR_BGR2RGB)

        if os.path.exists(BOI_IMAGE_PATH):
            boi_bgr = cv2.imread(BOI_IMAGE_PATH)
            if boi_bgr is not None:
                self.boi_image_rgb = cv2.cvtColor(boi_bgr, cv2.COLOR_BGR2RGB)

        if os.path.exists(SIX_SEVEN_IMAGE_PATH):
            six_seven_bgr = cv2.imread(SIX_SEVEN_IMAGE_PATH)
            if six_seven_bgr is not None:
                self.six_seven_image_rgb = cv2.cvtColor(six_seven_bgr, cv2.COLOR_BGR2RGB)

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
            text="Triggers: open palms near head | double point camera | dynamic 6->7 movement",
            font=("Roboto", 12),
            text_color="#64748b"
        )
        self.hint_label.grid(row=3, column=0, pady=(0, 8))

        button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=(4, 14))

        customtkinter.CTkButton(button_frame, text="Start Camera", command=self.start_camera).pack(side="left", padx=8)
        customtkinter.CTkButton(button_frame, text="Stop Camera", command=self.stop_camera).pack(side="left", padx=8)
        customtkinter.CTkButton(button_frame, text="Zurück", command=self.go_back).pack(side="left", padx=8)

        self.mode_var = customtkinter.StringVar(value="Static Memes")
        self.mode_selector = customtkinter.CTkSegmentedButton(
            self,
            values=["Static Memes", "Dynamic Memes (67)"],
            variable=self.mode_var
        )
        self.mode_selector.grid(row=5, column=0, pady=(0, 10))

        self.minigame_state = "IDLE"
        self.minigame_start_time = 0
        self.minigame_score = 0
        self.minigame_last_side = 0

        self.minigame_btn = customtkinter.CTkButton(
            self, text="Start 67 Minigame", command=self.start_minigame,
            fg_color="#8b5cf6", hover_color="#7c3aed"
        )
        self.minigame_btn.grid(row=6, column=0, pady=(0, 10))

        self.master.bind("<space>", lambda e: self.toggle_camera())

    def start_minigame(self):
        if not self.cam or not self.cam.isOpened():
            self.start_camera()
        self.minigame_state = "COUNTDOWN"
        self.minigame_start_time = time.time()
        self.minigame_score = 0
        self.minigame_last_side = 0

    def toggle_camera(self):
        if self.cam is None: self.start_camera()
        else: self.stop_camera()

    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
        self.frame_timestamp_ms = 0
        self.movement_history.clear()
        self.last_dynamic_trigger_time = 0.0

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.1,
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
        self.movement_history.clear()

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

    def _hand_scale(self, hand_landmarks):
        xs = [point.x for point in hand_landmarks]
        ys = [point.y for point in hand_landmarks]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        # A small floor avoids unstable division when tracking is noisy.
        return max(0.05, (width * width + height * height) ** 0.5)

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

    def _is_middle_finger_pose(self, hand_landmarks):
        middle_up = hand_landmarks[12].y < hand_landmarks[10].y
        index_down = hand_landmarks[8].y > hand_landmarks[6].y
        ring_down = hand_landmarks[16].y > hand_landmarks[14].y
        pinky_down = hand_landmarks[20].y > hand_landmarks[18].y

        return middle_up and index_down and ring_down and pinky_down

    def _detect_middle_finger(self, detection_result):
        if not detection_result.hand_landmarks:
            return False

        for hand_landmarks in detection_result.hand_landmarks:
            if self._is_middle_finger_pose(hand_landmarks):
                return True

        return False

    def _is_index_finger_pose(self, hand_landmarks):
        index_up = hand_landmarks[8].y < hand_landmarks[6].y
        middle_down = hand_landmarks[12].y > hand_landmarks[10].y
        ring_down = hand_landmarks[16].y > hand_landmarks[14].y
        pinky_down = hand_landmarks[20].y > hand_landmarks[18].y

        return index_up and middle_down and ring_down and pinky_down

    def _detect_index_finger(self, detection_result):
        if not detection_result.hand_landmarks:
            return False

        for hand_landmarks in detection_result.hand_landmarks:
            if self._is_index_finger_pose(hand_landmarks):
                return True

        return False

    def _squared_distance(self, p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z
        return dx * dx + dy * dy + dz * dz

    def _is_finger_extended(self, hand_landmarks, tip_idx, pip_idx, mcp_idx):
        tip = hand_landmarks[tip_idx]
        pip = hand_landmarks[pip_idx]
        mcp = hand_landmarks[mcp_idx]

        tip_to_mcp = self._squared_distance(tip, mcp)
        pip_to_mcp = self._squared_distance(pip, mcp)
        return tip_to_mcp > (pip_to_mcp * 1.15)

    def _is_finger_curled(self, hand_landmarks, tip_idx, pip_idx, mcp_idx):
        tip = hand_landmarks[tip_idx]
        pip = hand_landmarks[pip_idx]
        mcp = hand_landmarks[mcp_idx]

        tip_to_mcp = self._squared_distance(tip, mcp)
        pip_to_mcp = self._squared_distance(pip, mcp)
        return tip_to_mcp < (pip_to_mcp * 1.05)

    def _is_pointing_to_camera(self, hand_landmarks):
        # Instead of strict index pointing, we require an open palm.
        if not self._is_open_palm(hand_landmarks):
            return False

        # Check if hand is facing generally forward (fingertips closer to camera than base)
        index_tip = hand_landmarks[8]
        index_mcp = hand_landmarks[5]
        
        return (index_mcp.z - index_tip.z) > 0.015

    def _detect_double_point_camera(self, detection_result, face_box):
        if not detection_result.hand_landmarks or len(detection_result.hand_landmarks) < 2:
            return False

        pointing_hands = [
            hand_landmarks for hand_landmarks in detection_result.hand_landmarks
            if self._is_pointing_to_camera(hand_landmarks)
        ]

        if len(pointing_hands) < 2:
            return False

        # If absolute cinema would trigger, don't trigger BOI.
        if self._detect_absolute_cinema(detection_result, face_box):
            return False

        hand_depths = []
        for hand_landmarks in pointing_hands[:2]:
            avg_depth = sum(point.z for point in hand_landmarks) / len(hand_landmarks)
            hand_depths.append(avg_depth)

        # One hand should be slightly in front of the other
        depth_difference = abs(hand_depths[0] - hand_depths[1])
        return depth_difference >= 0.03

    def _get_handed_finger_counts(self, detection_result):
        left_count = 0
        right_count = 0
        centers = []
        scales = []

        if not detection_result.hand_landmarks:
            return left_count, right_count, centers, scales

        for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
            handedness = "Right"
            if detection_result.handedness and idx < len(detection_result.handedness):
                handedness = detection_result.handedness[idx][0].category_name

            finger_count = self.counter.count_fingers(hand_landmarks, handedness)
            if handedness == "Left":
                left_count = finger_count
            else:
                right_count = finger_count

            centers.append(self._hand_center(hand_landmarks))
            scales.append(self._hand_scale(hand_landmarks))

        return left_count, right_count, centers, scales

    def _update_movement_history(self, detection_result):
        now = time.time()
        left_count, right_count, centers, scales = self._get_handed_finger_counts(detection_result)

        mean_x, mean_y = 0.5, 0.5
        if centers:
            mean_x = sum(point[0] for point in centers) / len(centers)
            mean_y = sum(point[1] for point in centers) / len(centers)

        mean_scale = 0.12
        if scales:
            mean_scale = sum(scales) / len(scales)

        left_y = None
        right_y = None
        if len(centers) >= 2:
            # Sort centers by X coordinate to reliably get left and right hand on screen
            sorted_centers = sorted(centers, key=lambda c: c[0])
            left_y = sorted_centers[0][1]
            right_y = sorted_centers[-1][1]

        sample = {
            "time": now,
            "left": left_count,
            "right": right_count,
            "total": left_count + right_count,
            "hands": len(centers),
            "x": mean_x,
            "y": mean_y,
            "scale": mean_scale,
            "left_y": left_y,
            "right_y": right_y
        }
        self.movement_history.append(sample)

    def _window_mode(self, values):
        if not values:
            return None

        return max(set(values), key=values.count)

    def _path_length(self, samples):
        if len(samples) < 2:
            return 0.0

        distance = 0.0
        for i in range(1, len(samples)):
            dx = samples[i]["x"] - samples[i - 1]["x"]
            dy = samples[i]["y"] - samples[i - 1]["y"]
            distance += (dx * dx + dy * dy) ** 0.5

        return distance

    def _normalized_path_length(self, samples):
        if len(samples) < 2:
            return 0.0

        distance = 0.0
        for i in range(1, len(samples)):
            dx = samples[i]["x"] - samples[i - 1]["x"]
            dy = samples[i]["y"] - samples[i - 1]["y"]
            step = (dx * dx + dy * dy) ** 0.5
            scale = max(0.05, (samples[i]["scale"] + samples[i - 1]["scale"]) * 0.5)
            distance += step / scale

        return distance

    def _normalized_displacement(self, start_sample, end_sample):
        dx = end_sample["x"] - start_sample["x"]
        dy = end_sample["y"] - start_sample["y"]
        distance = (dx * dx + dy * dy) ** 0.5
        scale = max(0.05, (start_sample["scale"] + end_sample["scale"]) * 0.5)
        return distance / scale

    def _detect_dynamic_six_seven(self):
        now = time.time()
        cooldown_s = 2.0
        
        if now - self.last_dynamic_trigger_time < cooldown_s:
            return True

        # Need history of about 3 seconds to capture "repeating constantly"
        history_window_s = 3.0
        recent_samples = [
            sample for sample in self.movement_history
            if now - sample["time"] <= history_window_s
        ]

        # Require a reasonable amount of data points
        if len(recent_samples) < 15:
            return False
            
        # We look for the "weighing scales" alternating movement
        # Specifically: left hand higher than right, then right higher than left, repeated.
        # Check consecutive states where difference is > 8% of screen height
        states = []
        for s in recent_samples:
            if s.get("left_y") is not None and s.get("right_y") is not None:
                dy = s["right_y"] - s["left_y"]
                # dy > 0 means right hand is lower (larger y), left is higher
                if dy > 0.08:
                    states.append(1)
                elif dy < -0.08:
                    states.append(-1)
                    
        if not states:
            return False
            
        alternations = 0
        last_state = states[0]
        
        for state in states[1:]:
            if state != last_state:
                alternations += 1
                last_state = state
                
        # "repeating constantly" -> at least 3 alternations (e.g. Left Up -> Right Up -> Left Up -> Right Up)
        if alternations >= 1:
            self.last_dynamic_trigger_time = now
            self.movement_history.clear()
            return True

        return False

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

    def _overlay_meme(self, frame_rgb, meme_image_rgb):
        if meme_image_rgb is None:
            return frame_rgb

        frame_h, frame_w, _ = frame_rgb.shape
        target_w = min(360, frame_w - 20)
        aspect = meme_image_rgb.shape[0] / meme_image_rgb.shape[1]
        target_h = int(target_w * aspect)

        resized_meme = cv2.resize(meme_image_rgb, (target_w, target_h))

        x_start = (frame_w - target_w) // 2
        y_start = 10
        y_end = min(frame_h, y_start + target_h)
        x_end = x_start + target_w

        overlay_h = y_end - y_start
        if overlay_h <= 0:
            return frame_rgb

        frame_rgb[y_start:y_end, x_start:x_end] = resized_meme[:overlay_h, :target_w]
        return frame_rgb

    def _draw_bouncing_numbers(self, frame_rgb):
        frame_h, frame_w, _ = frame_rgb.shape
        now = time.time()
        
        # Fast bounce calculation using sine wave
        bounce_speed = 15.0 # How fast it moves
        bounce_height = 40  # How far it moves up/down
        
        # Calculate Y offset based on time
        y_offset_6 = int(math.sin(now * bounce_speed) * bounce_height)
        y_offset_7 = int(math.sin(now * bounce_speed + math.pi) * bounce_height) # Opposite phase
        
        base_y = frame_h // 2
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 5.0
        thickness = 10
        color = (255, 255, 255) # White
        outline_color = (0, 0, 0) # Black outline
        
        # Draw "6" on the left
        pos_6 = (50, base_y + y_offset_6)
        cv2.putText(frame_rgb, "6", pos_6, font, font_scale, outline_color, thickness + 5, cv2.LINE_AA)
        cv2.putText(frame_rgb, "6", pos_6, font, font_scale, color, thickness, cv2.LINE_AA)
        
        # Draw "7" on the right
        # Need text size to properly align "7" on the right side
        text_size_7, _ = cv2.getTextSize("7", font, font_scale, thickness)
        pos_7 = (frame_w - 50 - text_size_7[0], base_y + y_offset_7)
        cv2.putText(frame_rgb, "7", pos_7, font, font_scale, outline_color, thickness + 5, cv2.LINE_AA)
        cv2.putText(frame_rgb, "7", pos_7, font, font_scale, color, thickness, cv2.LINE_AA)
        
        return frame_rgb

    def _run_minigame_logic(self, frame_rgb, detection_result, now):
        frame_h, frame_w, _ = frame_rgb.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        if self.minigame_state == "COUNTDOWN":
            elapsed = now - self.minigame_start_time
            left = 3.0 - elapsed
            if left <= 0:
                self.minigame_state = "PLAYING"
                self.minigame_start_time = now
                self.minigame_score = 0
                self.minigame_last_side = 0
            else:
                num = str(math.ceil(left))
                text_size, _ = cv2.getTextSize(num, font, 7.0, 15)
                cx = (frame_w - text_size[0]) // 2
                cy = (frame_h + text_size[1]) // 2
                cv2.putText(frame_rgb, num, (cx, cy), font, 7.0, (0, 0, 0), 20, cv2.LINE_AA)
                cv2.putText(frame_rgb, num, (cx, cy), font, 7.0, (0, 255, 255), 10, cv2.LINE_AA)
                self.status_label.configure(text="Get Ready! Raise hands...", text_color="#facc15")
                
        elif self.minigame_state == "PLAYING":
            game_time = 15.0  # 15 seconds minigame
            elapsed = now - self.minigame_start_time
            left = game_time - elapsed
            
            if left <= 0:
                self.minigame_state = "FINISHED"
                self.minigame_start_time = now
            else:
                # Score logic: Count each time a different hand is raised significantly higher
                left_count, right_count, centers, scales = self._get_handed_finger_counts(detection_result)
                if len(centers) >= 2:
                    sorted_centers = sorted(centers, key=lambda c: c[0])
                    ly = sorted_centers[0][1]
                    ry = sorted_centers[-1][1]
                    dy = ry - ly # >0 means right is lower (larger y), left is higher
                    
                    current_side = self.minigame_last_side
                    if dy > 0.08:
                        current_side = 1
                    elif dy < -0.08:
                        current_side = -1
                        
                    if current_side != 0 and current_side != self.minigame_last_side:
                        self.minigame_score += 1
                        self.minigame_last_side = current_side
                
                # Draw UI
                time_str = f"Time: {left:.1f}s"
                score_str = f"Score: {self.minigame_score}"
                
                cv2.putText(frame_rgb, time_str, (20, 50), font, 1.2, (0, 0, 0), 5, cv2.LINE_AA)
                cv2.putText(frame_rgb, time_str, (20, 50), font, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
                
                cv2.putText(frame_rgb, score_str, (20, 100), font, 1.5, (0, 0, 0), 6, cv2.LINE_AA)
                cv2.putText(frame_rgb, score_str, (20, 100), font, 1.5, (100, 255, 100), 3, cv2.LINE_AA)
                
                self.status_label.configure(text="KEEP ALTERNATING!", text_color="#22c55e")
                
        elif self.minigame_state == "FINISHED":
            elapsed = now - self.minigame_start_time
            if elapsed > 5.0: # show result for 5 seconds
                self.minigame_state = "IDLE"
            
            msg = "TIME IS UP!"
            score_msg = f"Final Score: {self.minigame_score}"
            
            t_size1, _ = cv2.getTextSize(msg, font, 3.0, 8)
            cx1 = (frame_w - t_size1[0]) // 2
            cv2.putText(frame_rgb, msg, (cx1, frame_h//2 - 40), font, 3.0, (0, 0, 255), 8, cv2.LINE_AA)
            cv2.putText(frame_rgb, msg, (cx1, frame_h//2 - 40), font, 3.0, (255, 255, 255), 3, cv2.LINE_AA)
            
            t_size2, _ = cv2.getTextSize(score_msg, font, 2.0, 5)
            cx2 = (frame_w - t_size2[0]) // 2
            cv2.putText(frame_rgb, score_msg, (cx2, frame_h//2 + 50), font, 2.0, (0, 255, 0), 5, cv2.LINE_AA)
            
            self.status_label.configure(text="Minigame Finished! Press Start to play again.", text_color="#facc15")

        return frame_rgb

    def update_frame(self):
        if not (self.cam and self.cam.isOpened()):
            return

        success, frame_img = self.cam.read()
        if not success:
            self.after(10, self.update_frame)
            return

        frame_img = cv2.flip(frame_img, 1)
        frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)

        if self.landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            self.frame_timestamp_ms += 33

            result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp_ms)
            frame_rgb = self._draw_landmarks(frame_rgb, result)
            face_box = self._get_face_box(frame_rgb)
            self._update_movement_history(result)

            if face_box:
                h, w, _ = frame_rgb.shape
                x_min, y_min, x_max, y_max = face_box
                p1 = (int(x_min * w), int(y_min * h))
                p2 = (int(x_max * w), int(y_max * h))
                cv2.rectangle(frame_rgb, p1, p2, (0, 180, 255), 2)
            else:
                self.gesture_start_time = None
                self.status_label.configure(text="Face not detected", text_color="#f87171")

            # Check based on selected mode
            if self.minigame_state != "IDLE":
                frame_rgb = self._run_minigame_logic(frame_rgb, result, time.time())
            elif self.mode_var.get() == "Dynamic Memes (67)":
                is_dynamic_six_seven = self._detect_dynamic_six_seven()
                if is_dynamic_six_seven:
                    self.status_label.configure(text="67 MOVEMENT", text_color="#22d3ee")
                    frame_rgb = self._overlay_meme(frame_rgb, self.six_seven_image_rgb)
                    frame_rgb = self._draw_bouncing_numbers(frame_rgb)
                elif face_box:
                    self.status_label.configure(text="Waiting for 6->7 movement...", text_color="#94a3b8")
            else:
                # Static Memes
                is_cinema_pose = self._detect_absolute_cinema(result, face_box)
                is_middle_finger = self._detect_middle_finger(result)
                is_index_finger = self._detect_index_finger(result)
                is_double_point_camera = self._detect_double_point_camera(result, face_box)

                if is_double_point_camera:
                    self.status_label.configure(text="BOI", text_color="#eab308")
                    frame_rgb = self._overlay_meme(frame_rgb, self.boi_image_rgb)
                elif is_middle_finger:
                    self.status_label.configure(text="GORILLA MODE", text_color="#f97316")
                    frame_rgb = self._overlay_meme(frame_rgb, self.gorilla_image_rgb)
                elif is_index_finger:
                    self.status_label.configure(text="NERD MODE", text_color="#60a5fa")
                    frame_rgb = self._overlay_meme(frame_rgb, self.nerd_image_rgb)
                elif is_cinema_pose:
                    self.status_label.configure(text="ABSOLUTE CINEMA", text_color="#facc15")
                    frame_rgb = self._overlay_meme(frame_rgb, self.absolute_cinema_image_rgb)
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
