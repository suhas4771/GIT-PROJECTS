from tkinter import *
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os
from pathlib import Path
import time
import logging
logging.basicConfig(level=logging.INFO)

# local modules
from game_logic import Game
import storage

# ================= WINDOW =================
root = Tk()
root.title("Number Guess Game")
root.attributes("-fullscreen", True)
root.update()
root.bind("<Escape>", lambda e: root.destroy())

# ================= SCREEN SIZE =================
sw = root.winfo_width()
sh = root.winfo_height()

# ================= BACKGROUND (with fallback) =================
bg_path = Path(r"D:\Downloads\Screenshot 2025-12-16 114913.png")
bg = None
bg_label = Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
try:
    if bg_path.exists():
        bg_img = Image.open(bg_path).resize((sw, sh))
        bg = ImageTk.PhotoImage(bg_img)
        bg_label.configure(image=bg)
    else:
        raise FileNotFoundError("Background image not found")
except Exception as e:
    logging.warning("Background load failed: %s. Using fallback color.", e)
    bg_label.configure(bg="#0b1020")
bg_label.lower()

# ================= NEON BUTTON =================
class NeonButton(Frame):
    def __init__(self, master, text, command,
                 bg="#2e7d32", glow="#00ff99",
                 hover="#43a047", width=22, animate=False, pulse_interval=600):

        super().__init__(master, bg=glow)
        self.command = command

        self.button = Button(
            self, text=text,
            font=("Segoe UI", 14, "bold"),
            bg=bg, fg="white",
            width=width,
            bd=0, relief="flat",
            cursor="hand2",
            command=self.command
        )
        self.button.pack(padx=3, pady=3)

        self.default_bg = bg
        self.hover_bg = hover
        self.glow_bg = glow

        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)

        # Animation / pulsing
        self._animate = animate
        self._pulse_interval = pulse_interval
        self._pulse_state = False
        self._after_id = None

        # Prepare alternate glow color (slightly dimmer)
        def _hex_to_rgb(hexcolor):
            hexcolor = hexcolor.lstrip('#')
            return tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))

        def _rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        def _adjust_color(hexcolor, factor):
            r, g, b = _hex_to_rgb(hexcolor)
            r = max(0, min(255, int(r * factor)))
            g = max(0, min(255, int(g * factor)))
            b = max(0, min(255, int(b * factor)))
            return _rgb_to_hex((r, g, b))

        self._alt_glow = _adjust_color(self.glow_bg, 0.8)

        if self._animate:
            self.start_animation()

        # ensure animation stops when widget is destroyed
        self.bind('<Destroy>', lambda e: self.stop_animation())

    def on_enter(self, e):
        # pause visual pulsing on the frame to show hover state clearly
        self.stop_animation()
        self.configure(bg=self.glow_bg)
        self.button.configure(bg=self.hover_bg)

    def on_leave(self, e):
        self.button.configure(bg=self.default_bg)
        if self._animate:
            self.start_animation()
        else:
            self.configure(bg=self.glow_bg)

    def _pulse(self):
        # toggle between glow and alt glow
        self._pulse_state = not self._pulse_state
        color = self.glow_bg if self._pulse_state else self._alt_glow
        try:
            self.configure(bg=color)
        except Exception:
            return
        self._after_id = self.after(self._pulse_interval, self._pulse)

    def start_animation(self):
        if not self._animate:
            self._animate = True
        if self._after_id is None:
            # start immediate pulse
            self._pulse_state = False
            self._pulse()

    def stop_animation(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None


# ================= MAIN CARD =================
card_glow = Frame(root, bg="#00ff99")
card_glow.place(relx=0.5, rely=0.18, anchor="n")

panel = Frame(card_glow, bg="white")
panel.pack(padx=6, pady=6)
panel.tkraise()

# ================= GAME INSTANCE =================
# use Game class to encapsulate logic
game = Game()
# try load saved best score (JSON with timestamp)
best_score = storage.load_best_score()
start_time = None

# ================= UTIL =================
def clear_panel():
    for w in panel.winfo_children():
        w.destroy()

def play_win_sound():
    try:
        # winsound is Windows-only; wrap in try/except
        import winsound
        winsound.Beep(880, 250)
        winsound.Beep(1320, 250)
    except Exception:
        pass

# simple confetti using canvas circles
confetti_items = []

def _show_confetti(duration=1200, count=40):
    try:
        c = Canvas(panel, width=360, height=140, bg='white', highlightthickness=0)
        c.pack(pady=6)
        import random as _r
        colors = ['#f44336', '#e91e63', '#9c27b0', '#2196f3', '#4caf50', '#ffeb3b']
        w = c.winfo_reqwidth()
        h = c.winfo_reqheight()
        for i in range(count):
            x = _r.randint(10, w-10)
            y = _r.randint(10, h-10)
            r = _r.randint(3, 8)
            color = _r.choice(colors)
            item = c.create_oval(x-r, y-r, x+r, y+r, fill=color, outline='')
            confetti_items.append(item)
        panel.update_idletasks()
        panel.after(duration, lambda: c.destroy())
    except Exception:
        pass
# ================= SCORE STORAGE =================
# storage handled by storage.py (JSON)

# helper wrappers (compat)
def load_best_score():
    return storage.load_best_score()


def save_best_score(score):
    storage.save_best_score(score)


def reset_best_score():
    storage.reset_best_score()
    messagebox.showinfo("Reset", "Highest score has been reset.")
    show_score()

# load persisted score on startup (if any)
best_score = load_best_score()

# ================= GAME =================
def start_game():
    global start_time
    game.start_new_game()
    start_time = time.time()
    start_level()

def start_level():
    clear_panel()

    max_num = game.current_max()

    Label(panel, text=f"LEVEL : {game.current_name()} ({game.level_index + 1}/{game.total_levels()})",
          font=("Segoe UI", 22, "bold"),
          fg="#1b5e20",
          bg="white").pack(pady=(15, 5))

    Frame(panel, bg="#1b5e20", height=2, width=360).pack(pady=5)

    Label(panel, text=f"Guess a number between 1 and {max_num}",
          font=("Segoe UI", 14),
          bg="white").pack(pady=10)

    entry = Entry(panel, font=("Segoe UI", 18),
                  width=15, justify="center",
                  bd=2, relief="groove")
    entry.pack(pady=10)
    entry.focus()
    entry.bind("<Return>", lambda e: check_guess(entry))

    NeonButton(panel, "SUBMIT",
               command=lambda: check_guess(entry),
               bg="#2e7d32",
               hover="#43a047",
               glow="#00ff99").pack(pady=15)

def check_guess(entry):
    global best_score, start_time

    raw = entry.get().strip()
    if not raw.isdigit():
        messagebox.showwarning("Invalid", "Please enter a valid number.")
        return

    guess = int(raw)
    max_num = game.current_max()
    if not (1 <= guess <= max_num):
        messagebox.showwarning("Out of range", f"Enter a number between 1 and {max_num}.")
        return

    result = game.check_guess(guess)
    # Show hints or progress
    if result["result"] == "correct":
        if result["level_up"]:
            # moved to next level
            messagebox.showinfo("Correct", "Correct! Moving to next level.")
            start_level()
        elif result["completed"]:
            elapsed = int(time.time() - start_time) if start_time else None
            # update best score if necessary
            if best_score is None or result["attempts"] < best_score[0]:
                best_score = (result["attempts"], time.time())
                storage.save_best_score(best_score[0])
            play_win_sound()
            _show_confetti()
            messagebox.showinfo("Congratulations",
                                f"You completed all levels!\nAttempts: {result['attempts']}\nTime: {elapsed}s")
            start_menu()
    elif result["result"] == "high":
        messagebox.showinfo("Hint", "Too High")
    elif result["result"] == "low":
        messagebox.showinfo("Hint", "Too Low")

# ================= SCORE =================
def show_score():
    clear_panel()

    Label(panel, text="🏆 BEST SCORE",
          font=("Segoe UI", 24, "bold"),
          fg="#0d47a1",
          bg="white").pack(pady=20)

    score_data = storage.load_best_score()
    if score_data is None:
        score_text = "No score yet"
    else:
        score_text = f"Least attempts: {score_data[0]}  (saved: {score_data[1]})"

    Label(panel, text=score_text,
          font=("Segoe UI", 14),
          bg="white").pack(pady=15)

    NeonButton(panel, "RESET HIGHEST SCORE",
               command=lambda: reset_best_score(),
               bg="#c62828",
               hover="#e53935",
               glow="#ff5252").pack(pady=10)

    NeonButton(panel, "BACK",
               command=start_menu,
               bg="#1565c0",
               hover="#1e88e5",
               glow="#42a5f5").pack(pady=5)

# ================= MENU =================
def start_menu():
    clear_panel()

    Label(panel, text="NUMBER GUESS GAME",
          font=("Segoe UI", 28, "bold"),
          fg="#1b5e20",
          bg="white").pack(pady=(20, 10))

    Frame(panel, bg="#1b5e20", height=2, width=420).pack(pady=10)

    NeonButton(panel, "START GAME",
               command=start_game,
               bg="#2e7d32",
               hover="#43a047",
               glow="#00ff99",
               animate=True,
               pulse_interval=700).pack(pady=10)

    NeonButton(panel, "HIGHEST SCORE",
               command=show_score,
               bg="#1565c0",
               hover="#1e88e5",
               glow="#42a5f5",
               animate=True,
               pulse_interval=900).pack(pady=10)

    NeonButton(panel, "SETTINGS",
               command=show_settings,
               bg="#6a1b9a",
               hover="#7b1fa2",
               glow="#ba68c8").pack(pady=6)

    NeonButton(panel, "EXIT",
               command=root.destroy,
               bg="#c62828",
               hover="#e53935",
               glow="#ff5252").pack(pady=(10, 20))

# =============== SETTINGS ===============
def show_settings():
    clear_panel()
    Label(panel, text="SETTINGS",
          font=("Segoe UI", 20, "bold"),
          fg="#4a148c",
          bg="white").pack(pady=(10, 8))

    Label(panel, text="Levels (comma-separated):",
          font=("Segoe UI", 12),
          bg="white").pack(pady=(6, 2))
    levels_entry = Entry(panel, width=30)
    levels_entry.insert(0, ",".join(str(x) for x in game.levels))
    levels_entry.pack(pady=6)

    def apply_settings():
        txt = levels_entry.get().strip()
        try:
            nums = [int(p.strip()) for p in txt.split(",") if p.strip()]
            if not nums:
                raise ValueError("Empty levels")
            game.levels = nums
            game.start_new_game()
            messagebox.showinfo("Settings", "Levels updated.")
            start_menu()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid levels: {e}")

    NeonButton(panel, "APPLY",
               command=apply_settings,
               bg="#2e7d32",
               hover="#43a047",
               glow="#00ff99").pack(pady=6)

    NeonButton(panel, "BACK",
               command=start_menu,
               bg="#1565c0",
               hover="#1e88e5",
               glow="#42a5f5").pack(pady=6)

# quick keyboard shortcut
root.bind_all("<Control-s>", lambda e: start_game())

# ================= START =================
start_menu()
root.mainloop()