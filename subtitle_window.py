import tkinter as tk
from queue import Empty

class SubtitleWindow:
    def __init__(self, queue, on_clear_callback):
        self.queue = queue
        self.on_clear = on_clear_callback   # <-- callback from main

        self.root = tk.Tk()
        self.root.title("Live Interpreter")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#000000")

        self.root.geometry("1400x180")
        self.root.minsize(600, 120)
        self.root.resizable(True, False)

        self.line1 = tk.Label(
            self.root, text="", font=("Helvetica Neue", 30, "bold"),
            fg="#E0E0E0", bg="#000000", anchor="center"
        )
        self.line1.pack(pady=5, fill="x")

        self.line2 = tk.Label(
            self.root, text="", font=("Helvetica Neue", 34, "bold"),
            fg="#FFEB3B", bg="#000000", anchor="center"
        )
        self.line2.pack(pady=5, fill="x")

        self.root.after(20, self.process_queue)

    def trim_line(self, text, font_widget):
        text = str(text).strip()
        if not text:
            return ""

        max_width = self.root.winfo_width() - 40

        temp = tk.Label(self.root, font=font_widget.cget("font"))

        # Start from the full text → remove words from the LEFT until it fits
        words = text.split()
        while words:
            candidate = " ".join(words)
            temp.config(text=candidate)
            temp.update_idletasks()

            if temp.winfo_reqwidth() <= max_width:
                return candidate  # ✔ fits → show it

            # too long → drop the oldest word
            words.pop(0)

        return ""


    def update_labels(self, line_raw, line_translated):
        clean1 = self.trim_line(line_raw, self.line1)
        clean2 = self.trim_line(line_translated, self.line2)

        if clean1 == "" or clean2 == "":
            # clear UI
            self.line1.config(text="")
            self.line2.config(text="")
            # notify main.py that clear occurred
            self.on_clear()
            return

        self.line1.config(text=clean1)
        self.line2.config(text=clean2)

    def process_queue(self):
        try:
            l1, l2 = self.queue.get_nowait()
            self.update_labels(l1, l2)
        except Empty:
            pass

        self.root.after(20, self.process_queue)

    def run(self):
        self.root.mainloop()
