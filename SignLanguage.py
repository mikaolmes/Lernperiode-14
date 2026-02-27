import customtkinter
import cv2
from PIL import Image, ImageTk


class CameraFrame(customtkinter.CTkFrame):
    def __init__(self, master, go_back_callback):
        super().__init__(master)

        self.go_back_callback = go_back_callback
        self.cam = None

        self.label = customtkinter.CTkLabel(self, text="")
        self.label.pack(pady=10)

        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.pack(pady=10)

        start_btn = customtkinter.CTkButton(btn_frame, text="Start Camera", command=self.start_camera)
        start_btn.pack(side="left", padx=10)

        stop_btn = customtkinter.CTkButton(btn_frame, text="Stop Camera", command=self.stop_camera)
        stop_btn.pack(side="left", padx=10)

        back_btn = customtkinter.CTkButton(self, text="Zurück", command=self.go_back)
        back_btn.pack(pady=10)

    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
        self.update_frame()

    def stop_camera(self):
        if self.cam:
            self.cam.release()
            self.cam = None

    def go_back(self):
        self.stop_camera()
        self.pack_forget()
        self.go_back_callback()

    def update_frame(self):
        if self.cam and self.cam.isOpened():
            ret, frame_img = self.cam.read()
            if ret:
                frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_img)
                img = img.resize((640, 480))
                ctk_img = ImageTk.PhotoImage(img)

                self.label.configure(image=ctk_img)
                self.label.image = ctk_img

            self.after(10, self.update_frame)