import customtkinter
import cv2
from PIL import Image, ImageTk
import time
import numpy as np

#funktioniert to some cewrtain degree aber de scheiss isch nonig guet fucking expo und so fucköalsdfkj

MORSE_CODE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6",
    "--...": "7", "---..": "8", "----.": "9",
}


class MorseDecoder:
    DASH_RATIO = 2.5
    LETTER_GAP_RATIO = 2.5
    WORD_GAP_RATIO = 6.0

    SAMPLE_SIZE = 60
    LIGHT_HYSTERESIS = 15
    BASELINE_ALPHA = 0.02

    def __init__(self):
        self._reset()

    def _reset(self):
        self.baseline: float | None = None
        self.light_on: bool = False
        self.state_start: float = time.time()
        self.current_symbols: list[str] = []
        self.decoded_text: str = ""
        self.unit_ms: float | None = None
        self._on_samples: list[float] = []

    def process_frame(self, frame_bgr: np.ndarray) -> str:
        brightness = self._sample_brightness(frame_bgr)
        self._update_state(brightness)
        return self.decoded_text

    def reset(self):
        self._reset()

    def _sample_brightness(self, frame_bgr: np.ndarray) -> float:
        h, w = frame_bgr.shape[:2]
        cx, cy = w // 2, h // 2
        half = self.SAMPLE_SIZE // 2
        roi = frame_bgr[
            max(0, cy - half): cy + half,
            max(0, cx - half): cx + half,
        ]
        gray = np.mean(roi) if roi.ndim == 2 else np.mean(roi @ [0.114, 0.587, 0.299])
        return float(gray)

    def _update_state(self, brightness: float):
        now = time.time()
        elapsed_ms = (now - self.state_start) * 1000.0

        if self.baseline is None:
            self.baseline = brightness
            return

        threshold_on = self.baseline + self.LIGHT_HYSTERESIS
        threshold_off = self.baseline + self.LIGHT_HYSTERESIS * 0.5

        if not self.light_on:
            if brightness > threshold_on:
                self._handle_off_pulse(elapsed_ms)
                self.light_on = True
                self.state_start = now
            else:
                self.baseline = (
                    self.BASELINE_ALPHA * brightness
                    + (1 - self.BASELINE_ALPHA) * self.baseline
                )
        else:
            if brightness < threshold_off:
                self._handle_on_pulse(elapsed_ms)
                self.light_on = False
                self.state_start = now

    def _handle_on_pulse(self, duration_ms: float):
        self._calibrate(duration_ms)
        if self.unit_ms is None:
            return
        symbol = "-" if duration_ms >= self.DASH_RATIO * self.unit_ms else "."
        self.current_symbols.append(symbol)

    def _handle_off_pulse(self, duration_ms: float):
        if self.unit_ms is None or not self.current_symbols:
            return
        if duration_ms >= self.WORD_GAP_RATIO * self.unit_ms:
            self._commit_letter()
            self.decoded_text += " "
        elif duration_ms >= self.LETTER_GAP_RATIO * self.unit_ms:
            self._commit_letter()

    def _commit_letter(self):
        if not self.current_symbols:
            return
        code = "".join(self.current_symbols)
        letter = MORSE_CODE.get(code, f"[{code}]")
        self.decoded_text += letter
        self.current_symbols = []

    def _calibrate(self, on_duration_ms: float):
        self._on_samples.append(on_duration_ms)
        if len(self._on_samples) > 20:
            self._on_samples.pop(0)
        if len(self._on_samples) >= 3:
            sorted_samples = sorted(self._on_samples)
            dot_cluster = sorted_samples[: max(1, len(sorted_samples) // 3)]
            self.unit_ms = float(np.median(dot_cluster))


class MorseCodeFrame(customtkinter.CTkFrame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master)

        self.go_back_callback = go_back_callback
        self.cam = None
        self.decoder = MorseDecoder()  # ← lives here, in the one real __init__

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Kamera nicht gestartet")
        self.label.grid(row=0, column=0, sticky="nsew", pady=10)

        btn_frame = customtkinter.CTkFrame(self)
        btn_frame.grid(row=1, column=0, pady=10)

        customtkinter.CTkButton(btn_frame, text="Start (Space)", command=self.start_camera).pack(side="left", padx=10)
        customtkinter.CTkButton(btn_frame, text="Stop", command=self.stop_camera).pack(side="left", padx=10)
        customtkinter.CTkButton(btn_frame, text="Copy (Ctrl+C)", command=self.copy_to_clipboard).pack(side="left", padx=10)

        customtkinter.CTkButton(self, text="Zurück (Esc)", command=self.go_back).grid(row=2, column=0, pady=10)

        self.input_field = customtkinter.CTkEntry(
            self, placeholder_text="testntextfeld", width=400, height=40
        )
        self.input_field.grid(row=3, column=0, pady=10, padx=20)

        self.morse_output = customtkinter.CTkTextbox(self, width=400, height=100, corner_radius=10)
        self.morse_output.grid(row=4, column=0, pady=10, padx=20)
        self.morse_output.insert("0.0", "Hier erscheint der Morse-Code...")
        self.morse_output.configure(state="disabled")

        self.master.bind("<space>", lambda e: self.toggle_camera())
        self.master.bind("<Control-c>", lambda e: self.copy_to_clipboard())

    def toggle_camera(self):
        if self.cam is None:
            self.start_camera()
        else:
            self.stop_camera()

    def copy_to_clipboard(self):
        content = self.morse_output.get("1.0", "end-1c")
        self.master.clipboard_clear()
        self.master.clipboard_append(content)

    def update_output(self, new_text):
        self.morse_output.configure(state="normal")
        self.morse_output.delete("0.0", "end")
        self.morse_output.insert("0.0", new_text)
        self.morse_output.configure(state="disabled")

    def start_camera(self):
        if self.cam is None:
            self.cam = cv2.VideoCapture(0)
            self.update_frame()

    def stop_camera(self):
        if self.cam:
            self.cam.release()
            self.cam = None
            self.decoder.reset()
            self.label.configure(image="", text="Kamera gestoppt")

    def go_back(self):
        self.stop_camera()
        self.grid_forget()
        if self.go_back_callback:
            self.go_back_callback()

    def update_frame(self):
        if self.cam and self.cam.isOpened():
            ret, frame_img = self.cam.read()
            if ret:
                frame_img = cv2.flip(frame_img, 1)

                # Morse detection on the raw BGR frame
                text = self.decoder.process_frame(frame_img)
                if text:
                    self.update_output(text)

                # Draw sampling region so the user can aim the phone
                h, w = frame_img.shape[:2]
                cx, cy, half = w // 2, h // 2, 30
                cv2.rectangle(
                    frame_img,
                    (cx - half, cy - half),
                    (cx + half, cy + half),
                    (0, 255, 180), 2,
                )

                frame_img = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_img).resize((640, 480))
                ctk_img = ImageTk.PhotoImage(img)
                self.label.configure(image=ctk_img, text="")
                self.label.image = ctk_img

            self.after(16, self.update_frame)