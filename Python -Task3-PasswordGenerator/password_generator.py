"""
OIBSIP - Python Programming Track
Task 3: Random Password Generator (ADVANCED TIER)

Beginner-friendly, heavily commented version.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import string
import secrets          # secure random generator (better than 'random')
import pyperclip        # to copy password to clipboard


# ---------- STEP A: Setup constants ----------
# Characters we might exclude if user wants to avoid "confusing" characters
AMBIGUOUS_CHARS = "0O1lI"

# We will keep a history of last 5 passwords generated in this session
password_history = []


# ---------- STEP B: Function that builds the character pool ----------
def build_char_pool():
    """
    Looks at which checkboxes are ticked, and builds one big string
    of allowed characters to choose from.
    """
    pool = ""
    if var_upper.get():
        pool += string.ascii_uppercase      # ABCDEFGH...
    if var_lower.get():
        pool += string.ascii_lowercase      # abcdefgh...
    if var_digits.get():
        pool += string.digits               # 0123456789
    if var_symbols.get():
        pool += "!@#$%^&*()-_=+[]{}"        # common symbols

    # If user wants to exclude ambiguous characters, remove them
    if var_exclude_ambiguous.get():
        pool = "".join(ch for ch in pool if ch not in AMBIGUOUS_CHARS)

    return pool


# ---------- STEP C: Function that guarantees at least 1 char from each selected type ----------
def get_required_chars():
    """
    Returns a list containing at least ONE character from every
    checkbox that is currently ticked. This guarantees the final
    password always has a mix, not just luck.
    """
    required = []

    def clean(chars):
        if var_exclude_ambiguous.get():
            return "".join(c for c in chars if c not in AMBIGUOUS_CHARS)
        return chars

    if var_upper.get():
        required.append(secrets.choice(clean(string.ascii_uppercase)))
    if var_lower.get():
        required.append(secrets.choice(clean(string.ascii_lowercase)))
    if var_digits.get():
        required.append(secrets.choice(clean(string.digits)))
    if var_symbols.get():
        required.append(secrets.choice(clean("!@#$%^&*()-_=+[]{}")))

    return required


# ---------- STEP D: Password strength checker ----------
def check_strength(password):
    """
    Very simple strength scoring:
    - Length points
    - Variety of character types points
    """
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{}" for c in password):
        score += 1

    if score <= 2:
        return "Weak", "red"
    elif score <= 4:
        return "Medium", "orange"
    else:
        return "Strong", "green"


# ---------- STEP E: Main function that runs when "Generate" is clicked ----------
def generate_password():
    try:
        length = int(length_var.get())
    except ValueError:
        messagebox.showerror("Error", "Password length must be a number.")
        return

    if length < 8:
        messagebox.showerror("Error", "Password length must be at least 8 characters.")
        return

    # At least 2 character types must be selected
    selected_types = sum([var_upper.get(), var_lower.get(), var_digits.get(), var_symbols.get()])
    if selected_types < 1:
        messagebox.showerror("Error", "Please select at least one character type.")
        return

    pool = build_char_pool()
    if not pool:
        messagebox.showerror("Error", "Character pool is empty. Uncheck 'Exclude ambiguous' or select more types.")
        return

    # Step 1: get guaranteed characters (one of each selected type)
    required_chars = get_required_chars()

    # Step 2: fill up the rest of the password randomly using secrets.choice
    remaining_length = length - len(required_chars)
    if remaining_length < 0:
        remaining_length = 0
    random_part = [secrets.choice(pool) for _ in range(remaining_length)]

    # Step 3: combine required + random characters
    full_password_list = required_chars + random_part

    # Step 4: shuffle them so required chars aren't always at the start
    # secrets doesn't have shuffle, so we do a Fisher-Yates style shuffle manually
    for i in range(len(full_password_list) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        full_password_list[i], full_password_list[j] = full_password_list[j], full_password_list[i]

    password = "".join(full_password_list)

    # Show password in the result box
    result_var.set(password)

    # Update strength label
    strength_text, color = check_strength(password)
    strength_label.config(text=f"Strength: {strength_text}", fg=color)

    # Auto-copy to clipboard
    pyperclip.copy(password)
    copy_status_label.config(text="✔ Copied to clipboard!")

    # Update history (keep only last 5)
    password_history.insert(0, password)
    if len(password_history) > 5:
        password_history.pop()
    update_history_box()


def update_history_box():
    history_box.config(state="normal")
    history_box.delete("1.0", tk.END)
    for i, pwd in enumerate(password_history, start=1):
        history_box.insert(tk.END, f"{i}. {pwd}\n")
    history_box.config(state="disabled")


def copy_password_manually():
    pwd = result_var.get()
    if pwd:
        pyperclip.copy(pwd)
        copy_status_label.config(text="✔ Copied to clipboard!")
    else:
        messagebox.showinfo("Info", "Generate a password first.")


# ---------- STEP F: Build the GUI window ----------
root = tk.Tk()
root.title("Random Password Generator - OIBSIP")
root.geometry("420x520")
root.resizable(False, False)

# --- Length input ---
tk.Label(root, text="Password Length:", font=("Arial", 11)).pack(pady=(15, 0))
length_var = tk.StringVar(value="12")
length_spin = tk.Spinbox(root, from_=8, to=64, textvariable=length_var, width=10, font=("Arial", 11))
length_spin.pack(pady=5)

# --- Checkboxes for character types ---
var_upper = tk.BooleanVar(value=True)
var_lower = tk.BooleanVar(value=True)
var_digits = tk.BooleanVar(value=True)
var_symbols = tk.BooleanVar(value=True)
var_exclude_ambiguous = tk.BooleanVar(value=False)

tk.Checkbutton(root, text="Include Uppercase (A-Z)", variable=var_upper, font=("Arial", 10)).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include Lowercase (a-z)", variable=var_lower, font=("Arial", 10)).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include Numbers (0-9)", variable=var_digits, font=("Arial", 10)).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Include Symbols (!@#$...)", variable=var_symbols, font=("Arial", 10)).pack(anchor="w", padx=40)
tk.Checkbutton(root, text="Exclude Ambiguous Characters (0,O,1,l,I)", variable=var_exclude_ambiguous, font=("Arial", 10)).pack(anchor="w", padx=40, pady=(0, 10))

# --- Generate button ---
tk.Button(root, text="Generate Password", command=generate_password,
          bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

# --- Result display ---
result_var = tk.StringVar()
result_entry = tk.Entry(root, textvariable=result_var, font=("Consolas", 13), width=32, justify="center")
result_entry.pack(pady=5)

# --- Strength label ---
strength_label = tk.Label(root, text="Strength: ", font=("Arial", 11, "bold"))
strength_label.pack()

# --- Copy button ---
tk.Button(root, text="Copy to Clipboard", command=copy_password_manually,
          bg="#2196F3", fg="white", font=("Arial", 10)).pack(pady=8)
copy_status_label = tk.Label(root, text="", font=("Arial", 9), fg="gray")
copy_status_label.pack()

# --- History section ---
tk.Label(root, text="Last 5 Generated Passwords:", font=("Arial", 10, "bold")).pack(pady=(15, 0))
history_box = tk.Text(root, height=6, width=40, font=("Consolas", 9), state="disabled", bg="#f0f0f0")
history_box.pack(pady=5)

# ---------- STEP G: Run the app ----------
root.mainloop()