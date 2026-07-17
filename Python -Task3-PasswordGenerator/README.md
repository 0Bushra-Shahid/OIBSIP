# 🔐 Random Password Generator

**OIBSIP Internship – Python Programming Track – Task 3 (Advanced Tier)**

## 📌 Objective
Build a Python tool that generates strong, random passwords based on
user-defined criteria such as length and character types, using a secure
random generation method and a graphical interface.

## ✨ Features
- GUI built with **Tkinter** — no command line needed
- Adjustable password length (Spinbox control)
- Checkboxes to include/exclude: Uppercase, Lowercase, Numbers, Symbols
- Uses Python's **`secrets`** module (cryptographically secure) instead of
  `random`, which is not safe for security-related use cases
- Guarantees the generated password contains **at least one character**
  from every selected character type
- Option to **exclude ambiguous characters** (`0`, `O`, `1`, `l`, `I`) to
  avoid confusion when reading/typing the password
- **Password strength indicator** — Weak / Medium / Strong, based on
  length and character variety
- **Copy to Clipboard** button using `pyperclip`
- **Session history** — displays the last 5 generated passwords
  (kept only in memory, never written to a file, for security)

## 🛠️ Tech Stack
- Python 3
- `tkinter` — GUI
- `secrets` — secure random character generation
- `string` — character sets (letters, digits)
- `pyperclip` — clipboard access

## ▶️ How to Run

1. Install the one external dependency:
   ```bash
   pip install pyperclip
   ```
2. Run the script:
   ```bash
   python password_generator.py
   ```
3. Set your desired length, select character types, and click
   **Generate Password**.

## 🔒 Why `secrets` instead of `random`?
Python's `random` module is a **pseudo-random** generator meant for
simulations and games — its output can theoretically be predicted.
The `secrets` module is designed specifically for generating
security-sensitive data like passwords, tokens, and keys, using a
cryptographically secure source of randomness. This project always
uses `secrets.choice()` and a manual Fisher–Yates shuffle (also powered
by `secrets`) instead of the insecure `random` equivalents.

## 📷 Screenshots
See the `screenshots/` folder in this repository for the app in action.

## 🎥 Demo Video
Linked in the task submission form / LinkedIn post.

## 👤 Author
Submitted as part of the **Oasis Infobyte Summer Internship Program (SIP)**
— Python Programming Track.
