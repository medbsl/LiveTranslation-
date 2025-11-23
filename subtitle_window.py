import tkinter as tk
from queue import Empty
import time

class SubtitleWindow:
    def __init__(self, queue, reset_callback):
        self.queue = queue
        self.reset_callback = reset_callback

        self.root = tk.Tk()
        self.root.title("Live Interpreter")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#000000")

        self.root.geometry("1400x180")
        self.root.minsize(600, 120)
        self.root.resizable(True, False)

        # First line (original)
        self.line1 = tk.Label(
            self.root, text="", font=("Helvetica Neue", 30, "bold"),
            fg="#E0E0E0", bg="#000000", anchor="center"
        )
        self.line1.pack(pady=5, fill="x")

        # Second line (translation)
        self.line2 = tk.Label(
            self.root, text="", font=("Helvetica Neue", 34, "bold"),
            fg="#FFEB3B", bg="#000000", anchor="center"
        )
        self.line2.pack(pady=5, fill="x")

        self.root.after(20, self.process_queue)

    # --------------------------------------------------------
    # Trim logic: if text exceeds label width → signal "RESET"
    # --------------------------------------------------------
    def trim_line(self, text, font_widget):
        if not isinstance(text, str):
            text = str(text)

        text = text.strip()

        if text == "":
            return ""

        max_width = self.root.winfo_width() - 40

        temp = tk.Label(self.root, font=font_widget.cget("font"))
        temp.config(text=text)
        temp.update_idletasks()

        if temp.winfo_reqwidth() <= max_width:
            return text

        # Too long → CLEAR the line but allow it to continue
        return ""   # NOT None

    # --------------------------------------------------------
    # Update the two subtitle lines
    # --------------------------------------------------------
    def update_labels(self, line_raw, line_translated):
        clean1 = self.trim_line(line_raw, self.line1)
        clean2 = self.trim_line(line_translated, self.line2)

        # If exceeded → clear both lines + reset recognizer memory
        if clean1 == "" and clean2 == "":
            self.line1.config(text="")
            self.line2.config(text="")

            self.reset_callback()   # resets last_original + last_translated
            return

        # Continue normally
        self.line1.config(text=clean1)
        self.line2.config(text=clean2)

    # --------------------------------------------------------
    # Check queue for new text from recognizer
    # --------------------------------------------------------
    def process_queue(self):
        try:
            data = self.queue.get_nowait()
            self.update_labels(*data)
        except Empty:
            pass

        self.root.after(20, self.process_queue)

    def run(self):
        self.root.mainloop()
