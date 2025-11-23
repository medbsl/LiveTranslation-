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

        # -------- Smoothing (debounce) --------
        self.last_update_time = 0
        self.min_interval = 150  # ms
        self.buffer_line1 = ""
        self.buffer_line2 = ""

        # -------- Dynamic chunk size (auto width) --------
        self.dynamic_max_words = 8
        self.test_label = tk.Label(self.root, font=("Helvetica Neue", 30, "bold"))

        self.root.after(20, self.process_queue)

    # --------------------------------------------------------
    # Calculate max words that fit inside window
    # --------------------------------------------------------
    def calculate_dynamic_max_words(self, sample_words):
        max_width = self.root.winfo_width() - 40

        for n in range(3, 20):
            chunk = " ".join(sample_words[:n])
            self.test_label.config(text=chunk)
            self.test_label.update_idletasks()

            if self.test_label.winfo_reqwidth() > max_width:
                return max(3, n - 1)  # never less than 3

        return 10

    # --------------------------------------------------------
    # Split entire sentence into chunks of N words
    # --------------------------------------------------------
    def chunk_words(self, text):
        text = text.strip()
        if not text:
            return ""

        words = text.split()

        # Calculate how many words fit
        self.dynamic_max_words = self.calculate_dynamic_max_words(words)

        total_words = len(words)
        chunk_index = (total_words - 1) // self.dynamic_max_words

        start = chunk_index * self.dynamic_max_words
        end = start + self.dynamic_max_words

        return " ".join(words[start:end])

    # --------------------------------------------------------
    # Smooth update (YouTube-style)
    # --------------------------------------------------------
    def update_smooth(self):
        now = int(time.time() * 1000)
        if now - self.last_update_time < self.min_interval:
            return

        self.last_update_time = now

        line1_clean = self.chunk_words(self.buffer_line1)
        line2_clean = self.chunk_words(self.buffer_line2)

        self.line1.config(text=line1_clean)
        self.line2.config(text=line2_clean)

    # --------------------------------------------------------
    # Process recognizer queue
    # --------------------------------------------------------
    def process_queue(self):
        try:
            l1, l2 = self.queue.get_nowait()
            self.buffer_line1 = l1
            self.buffer_line2 = l2
        except Empty:
            pass

        self.update_smooth()
        self.root.after(20, self.process_queue)

    def run(self):
        self.root.mainloop()
