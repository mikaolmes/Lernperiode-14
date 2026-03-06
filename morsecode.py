import customtkinter
import cv2
from PIL import Image, ImageTk

class MorseCodeFrame(customtkinter.CTkFrame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)

        self.go_back_callback = go_back_callback
        self.cam = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Bildanzeige
        self.label = customtkinter.CTkLabel(self, text="")
        self.label.grid(row=0, column=0, sticky="nsew", pady=10)

        # Button-Container
        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.grid(row=1, column=0, pady=10)

        # Start Button
        start_btn = customtkinter.CTkButton(
            btn_frame,
            text="Start Camera",
            command=self.start_camera
        )
        start_btn.pack(side="left", padx=10)

        # Stop Button
        stop_btn = customtkinter.CTkButton(
            btn_frame,
            text="Stop Camera",
            command=self.stop_camera
        )
        stop_btn.pack(side="left", padx=10)

        # Zurück Button
        back_btn = customtkinter.CTkButton(
            self,
            text="Zurück",
            command=self.go_back
        )
        back_btn.grid(row=2, column=0, pady=10)

        # Eingabefeld für Text-zu-Morse
        self.input_field = customtkinter.CTkEntry(
            self, 
            placeholder_text="Text zum Übersetzen hier eingeben...", 
            width=400, 
            height=40
        )
        self.input_field.grid(row=3, column=0, pady=10, padx=20)

        # Textbox für die Anzeige (Read-Only)
        self.morse_output = customtkinter.CTkTextbox(
            self, 
            width=400, 
            height=100, 
            corner_radius=10
        )
        self.morse_output.grid(row=4, column=0, pady=10, padx=20)
        self.morse_output.insert("0.0", "Hier erscheint der Morse-Code...")
        
        self.morse_output.configure(state="disabled")

    def update_output(self, new_text):
        self.morse_output.configure(state="normal") 
        self.morse_output.delete("0.0", "end")     
        self.morse_output.insert("0.0", new_text) 
        self.morse_output.configure(state="disabled")

    # =========================
    # Kamera starten
    # =========================
    def start_camera(self):
        self.cam = cv2.VideoCapture(0)
        self.update_frame()

    # =========================
    # Kamera stoppen
    # =========================
    def stop_camera(self):
        if self.cam:
            self.cam.release()
            self.cam = None

    # =========================
    # Zurück zum Hauptmenü
    # =========================
    def go_back(self):
        self.stop_camera()
        self.grid_forget()

        if self.go_back_callback:
            self.go_back_callback()

    # =========================
    # Frame Update Loop
    # =========================
    def update_frame(self):
        if self.cam and self.cam.isOpened():
            ret, frame_img = self.cam.read()

            if ret:
                frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame_img)
                img = img.resize((640, 480))
                ctk_img = ImageTk.PhotoImage(img)

                self.label.configure(image=ctk_img, text="")
                self.label.image = ctk_img  

            self.after(16, self.update_frame)