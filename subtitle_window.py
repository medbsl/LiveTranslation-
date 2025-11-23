import tkinter as tk
from queue import Empty
import time

class SubtitleWindow:
    def __init__(self, queue):
        self.queue = queue

        self.root = tk.Tk()
        self.root.title("Live Interpreter")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#000000")

        self.root.geometry("1400x180")
        self.root.minsize(600, 150)
        self.root.resizable(True, False)

        # -------- 2-LINE YOUTUBE STYLE --------
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

        # -------- smoothing / stability --------
        self.last_update_time = 0
        self.min_interval = 180   # update UI only every 220 ms (SMOOTH)
        self.freeze_after_final = 450  # freeze final text for readability (ms)

        self.buffer_line1 = ""
        self.buffer_line2 = ""
        self.last_final_time = 0

        # dynamic word limit based on width
        self.dynamic_max_words = 10
        self.test_label = tk.Label(self.root, font=("Helvetica Neue", 30, "bold"))

        self.root.after(20, self.process_queue)

    # --------------------------------------------------------
    def calculate_dynamic_max_words(self, sample_words):
        max_width = self.root.winfo_width() - 40

        for n in range(3, 20):
            chunk = " ".join(sample_words[:n])
            self.test_label.config(text=chunk)
            self.test_label.update_idletasks()

            if self.test_label.winfo_reqwidth() > max_width:
                return max(3, n - 1)

        return 10

    # --------------------------------------------------------
    def chunk_words(self, text):
        text = text.strip()
        if not text:
            return ""

        words = text.split()

        max_words = self.dynamic_max_words  # your auto-calculated limit
        total_words = len(words)

        # How many chunks exist so far?
        chunk_count = (total_words - 1) // max_words

        # Compute current chunk boundaries
        start = chunk_count * max_words
        end = start + max_words

        # Slice exact chunk
        chunk = words[start:end]

        return " ".join(chunk)


    # --------------------------------------------------------
    # NEW: Smooth + stabilized update
    # --------------------------------------------------------
    def update_smooth(self):
        now = int(time.time() * 1000)

        # ---------- freeze after final result ----------
        if now - self.last_final_time < self.freeze_after_final:
            return

        # ---------- debounce fast updates ----------
        if now - self.last_update_time < self.min_interval:
            return

        self.last_update_time = now

        line1_clean = self.chunk_words(self.buffer_line1)
        line2_clean = self.chunk_words(self.buffer_line2)

        self.line1.config(text=line1_clean)
        self.line2.config(text=line2_clean)

    # --------------------------------------------------------
    def process_queue(self):
        try:
            l1, l2 = self.queue.get_nowait()

            # If incoming text ends with punctuation → final sentence
            if l2.strip().endswith((".", "!", "؟", "?", "…")):
                self.last_final_time = int(time.time() * 1000)

            self.buffer_line1 = l1
            self.buffer_line2 = l2


        except Empty:
            pass

        self.update_smooth()
        self.root.after(20, self.process_queue)

    def run(self):
        self.root.mainloop()
