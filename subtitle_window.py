import tkinter as tk

class SubtitleWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Live Interpreter")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#000000")
        
        # Adaptive width / height
        self.root.geometry("1400x180")
        self.root.minsize(600, 120)
        
        # Allow horizontal stretch, but keep height small
        self.root.resizable(True, False)

        # --- LINE 1 (Original Spoken Text) ---
        self.line1 = tk.Label(
            self.root,
            text="",
            font=("Helvetica Neue", 30, "bold"),
            fg="#E0E0E0",
            bg="#000000",
            wraplength=0,
            justify="center"
        )
        self.line1.pack(pady=5, fill="x")

        # --- LINE 2 (Translation) ---
        self.line2 = tk.Label(
            self.root,
            text="",
            font=("Helvetica Neue", 34, "bold"),
            fg="#FFEB3B",
            bg="#000000",
            wraplength=0,
            justify="center"
        )
        self.line2.pack(pady=5, fill="x")

    # -----------------------------------------
    # SMART TRIMMING (Keeps text readable)
    # -----------------------------------------
    def trim_line(self, text, font_widget):
        max_width = self.root.winfo_width() - 40
        temp = tk.Label(self.root, font=font_widget.cget("font"))
        words = text.split()

        result = []
        temp_text = ""

        for word in reversed(words):
            test_text = word + (" " + temp_text if temp_text else "")
            temp.config(text=test_text)
            temp.update_idletasks()

            if temp.winfo_reqwidth() > max_width:
                break

            result.insert(0, word)
            temp_text = test_text

        return " ".join(result) if result else words[-1]

    # -----------------------------------------
    # UPDATE WINDOW
    # -----------------------------------------
    def update(self, line_raw, line_translated):
        # trim both lines nicely
        line1_clean = self.trim_line(line_raw, self.line1)
        line2_clean = self.trim_line(line_translated, self.line2)

        self.line1.config(text=line1_clean)
        self.line2.config(text=line2_clean)

        self.root.update_idletasks()
        self.root.update()

    def run(self):
        self.root.mainloop()
