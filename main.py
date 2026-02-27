import customtkinter
from SignLanguage import CameraFrame

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

root = customtkinter.CTk()
root.geometry("700x600")

current_frame = None


def show_main_menu():
    global current_frame
    current_frame = create_main_menu()
    current_frame.pack(fill="both", expand=True)


def signLanguage():
    global current_frame
    current_frame.pack_forget()
    current_frame = CameraFrame(root, show_main_menu)
    current_frame.pack(fill="both", expand=True)


def create_main_menu():
    frame = customtkinter.CTkFrame(root)

    label = customtkinter.CTkLabel(frame, text="Was möchten Sie übersetzen?", font=("Roboto", 24))
    label.pack(pady=20)

    button = customtkinter.CTkButton(frame, text="Gebärdensprache", command=signLanguage)
    button.pack(pady=10)

    button2 = customtkinter.CTkButton(frame, text="Morsecode")
    button2.pack(pady=10)

    return frame


show_main_menu()
root.mainloop()
