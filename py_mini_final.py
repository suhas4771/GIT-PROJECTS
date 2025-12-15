from tkinter import *
from tkinter import messagebox
import random

window1 = Tk()
window1.title("GAME BY GROUP(13)")

# global variables
max_num = 0
number = 0
attempts = 0

# --- game logic functions ---

def game_difficulty():
    global max_num, number
    user_difficulty = entry1.get().strip().lower()

    if user_difficulty == "easy":
        max_num = 10
    elif user_difficulty == "medium":
        max_num = 50
    elif user_difficulty == "hard":
        max_num = 100
    elif user_difficulty == "impossible":
        max_num = 1000
    else:
        messagebox.showwarning(
            title="THE GAME",
            message="Invalid choice, Entering SECRET level\n\nDifficulty: THE END (1-10000)\n\nGood luck!!!!!"
        )
        max_num = 10000

    entry1.config(state="disabled")
    button_difficulty.config(state="disabled")

    number = random.randint(1, max_num)
    label3 = Label(window1, text="GUESS YOUR NUMBER:", font=("Arial", 10))
    label3.grid(row=3, column=0)

    global entry2
    entry2 = Entry(window1, font=("Arial", 15))
    entry2.grid(row=3, column=1)

    Button(window1, text="Submit Guess", font=("Arial", 10), command=check_guess).grid(row=3, column=2)

def check_guess():
    global number, max_num, attempts
    guess_text = entry2.get().strip()

    if not guess_text:
        messagebox.showwarning("THE GAME", "NO ESCAPE!!!!\nGuess the number:")
        return

    try:
        guess = int(guess_text)
    except ValueError:
        messagebox.showerror("THE GAME", "Please enter a valid number!")
        return

    attempts += 1

    if guess == number:
        messagebox.showinfo("THE GAME", f" CONGRATULATIONS! \nYour guess is correct!\nAttempts: {attempts}")
        window1.destroy()  # close after win
    elif guess > max_num:
        messagebox.showwarning("THE GAME", "Your number is out of range!\nTry again!")
    elif guess < 0:
        messagebox.showerror("THE GAME", "Negative numbers are not allowed!")
    elif guess > number:
        messagebox.showinfo("THE GAME", "Too high!")
    elif guess < number:
        messagebox.showinfo("THE GAME", "Too low!")

# --- UI layout ---
label1 = Label(window1, text="Welcome to 'Can You Guess The Number'!", font=("Arial", 20, "bold"), fg="blue")
label1.grid(row=0, column=0, columnspan=3, pady=10)

label2 = Label(window1,
               text="Choose difficulty: easy (1-10), medium (1-50), hard (1-100), impossible (1-1000)",
               font=("Arial", 15))
label2.grid(row=1, column=0, columnspan=3)

entry1 = Entry(window1, font=("Arial", 20))
entry1.grid(row=2, column=0, padx=10, pady=5)

button_difficulty = Button(window1, text="ENTER", font=("Arial", 10), command=game_difficulty)
button_difficulty.grid(row=2, column=1, padx=10, pady=5)

window1.mainloop()


