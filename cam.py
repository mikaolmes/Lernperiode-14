import customtkinter
import cv2 #why are you blue
from PIL import Image, ImageTk

root = customtkinter.CTk()
root.geometry("700x600")
root.title("Camera")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="")
label.pack(pady=10)



cam = None

def start_camera():
    global cam
    cam = cv2.VideoCapture(0) #default cam
    update_frame()

def stop_camera():
    global cam
    if cam:
        cam.release()
        cam = None

def update_frame():
    global cam
    if cam and cam.isOpened():
        ret, frame_img = cam.read()
        if ret:
            frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB) # Convert OpenCV to RGB
            img = Image.fromarray(frame_img)
            img = img.resize((640, 480))  
            ctk_img = ImageTk.PhotoImage(img)
            label.configure(image=ctk_img, text="")
            #label.image = ctk_img  
        root.after(10, update_frame)   #10ms - 100fps / 16ms - 60fps



# Buttons
btn_frame = customtkinter.CTkFrame(master=root)
btn_frame.pack(pady=10)

start_btn = customtkinter.CTkButton(master=btn_frame, text="Start Camera", command=start_camera)
start_btn.pack(side="left", padx=10)

stop_btn = customtkinter.CTkButton(master=btn_frame, text="Stop Camera", command=stop_camera)
stop_btn.pack(side="left", padx=10)

root.mainloop()