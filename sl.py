import customtkinter
import cv2 #why are you blue
from PIL import Image, ImageTk
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time

# MediaPipe Tasks API setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Hand connections for drawing (21 landmarks)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index finger
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle finger
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring finger
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm
]

# Path to the model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")

root = customtkinter.CTk()
root.geometry("700x600")
root.title("Camera")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="")
label.pack(pady=10)



cam = None
landmarker = None
frame_timestamp_ms = 0

def start_camera():
    global cam, landmarker, frame_timestamp_ms
    cam = cv2.VideoCapture(0) #default cam
    frame_timestamp_ms = 0
    
    # Create Hand Landmarker with VIDEO mode
    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=4,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    landmarker = HandLandmarker.create_from_options(options)
    update_frame()

def stop_camera():
    global cam, landmarker
    if cam:
        cam.release()
        cam = None
    if landmarker:
        landmarker.close()
        landmarker = None

def draw_landmarks_on_image(rgb_image, detection_result):
    """Draw hand landmarks on the image using OpenCV."""
    if detection_result.hand_landmarks:
        h, w, _ = rgb_image.shape
        for hand_landmarks in detection_result.hand_landmarks:
            # Draw connections
            for connection in HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start = hand_landmarks[start_idx]
                end = hand_landmarks[end_idx]
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(rgb_image, start_point, end_point, (0, 255, 0), 2)
            
            # Draw landmarks
            for landmark in hand_landmarks:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(rgb_image, (cx, cy), 5, (255, 0, 0), -1)
    return rgb_image

def update_frame():
    global cam, landmarker, frame_timestamp_ms
    if cam and cam.isOpened():
        ret, frame_img = cam.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB) # Convert OpenCV to RGB

            if landmarker:
                # Convert to MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                
                # Detect hand landmarks (VIDEO mode requires timestamp)
                frame_timestamp_ms += 33  # ~30 FPS
                result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
                
                # Draw landmarks on the frame
                frame_rgb = draw_landmarks_on_image(frame_rgb, result)

            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480))  
            ctk_img = ImageTk.PhotoImage(img)
            label.configure(image=ctk_img, text="")
            label.image = ctk_img  
        root.after(10, update_frame)   #10ms - 100fps / 16ms - 60fps



# Buttons
btn_frame = customtkinter.CTkFrame(master=root)
btn_frame.pack(pady=10)

start_btn = customtkinter.CTkButton(master=btn_frame, text="Start Camera", command=start_camera)
start_btn.pack(side="left", padx=10)

stop_btn = customtkinter.CTkButton(master=btn_frame, text="Stop Camera", command=stop_camera)
stop_btn.pack(side="left", padx=10)

root.mainloop()