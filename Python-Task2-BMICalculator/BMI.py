import tkinter as tk
import sqlite3
import os
from datetime import datetime
import matplotlib.pyplot as plt

# --- Database setup ---
# Get the folder where this script is located, and place the db file there.
# This ensures the same database file is used no matter how/where the
# script is run from (VS Code, terminal, double-click, etc.)
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "bmi_history.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        weight REAL,
        height REAL,
        bmi REAL,
        category TEXT,
        date TEXT
    )
""")
conn.commit()

# --- GUI setup ---
root = tk.Tk()
root.title("BMI Calculator")
root.geometry("400x450")

# Name field
name_label = tk.Label(root, text="Name:")
name_label.pack(pady=5)
name_entry = tk.Entry(root)
name_entry.pack()

# Weight field
weight_label = tk.Label(root, text="Weight (kg):")
weight_label.pack(pady=5)
weight_entry = tk.Entry(root)
weight_entry.pack()

# Height field
height_label = tk.Label(root, text="Height (m):")
height_label.pack(pady=5)
height_entry = tk.Entry(root)
height_entry.pack()

# Empty label to display the result later
result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=20)


def calculate_bmi():
    name = name_entry.get()
    weight_text = weight_entry.get()
    height_text = height_entry.get()

    try:
        weight = float(weight_text)
        height = float(height_text)

        if weight <= 0 or height <= 0:
            result_label.config(text="Error: Enter positive numbers only", fg="red")
            return

        bmi = round(weight / (height ** 2), 2)

        # Classify BMI into a category and assign a display color
        if bmi < 18.5:
            category, color = "Underweight", "orange"
        elif bmi < 25:
            category, color = "Normal", "green"
        elif bmi < 30:
            category, color = "Overweight", "orange"
        else:
            category, color = "Obese", "red"

        result_label.config(text=f"BMI: {bmi} ({category})", fg=color)

        # --- Save this record to the database ---
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute(
            "INSERT INTO records (name, weight, height, bmi, category, date) VALUES (?, ?, ?, ?, ?, ?)",
            (name, weight, height, bmi, category, today)
        )
        conn.commit()

    except ValueError:
        # Runs if float() fails, e.g. user typed letters instead of numbers
        result_label.config(text="Error: Enter valid numbers", fg="red")


calculate_button = tk.Button(root, text="Calculate", command=calculate_bmi)
calculate_button.pack(pady=10)


def view_history():
    name = name_entry.get()

    # Fetch only the records matching this name, oldest first
    cursor.execute(
        "SELECT weight, height, bmi, category, date FROM records WHERE name = ? ORDER BY date",
        (name,)
    )
    rows = cursor.fetchall()  # returns all matching rows as a list

    if not rows:
        history_label.config(text="No history found for this name")
        return

    # Build a multi-line string, one line per record
    history_text = ""
    for row in rows:
        weight, height, bmi, category, date = row
        history_text += f"{date} — BMI {bmi} ({category})\n"

    history_label.config(text=history_text)


history_button = tk.Button(root, text="View History", command=view_history)
history_button.pack(pady=5)


def show_graph():
    name = name_entry.get()

    cursor.execute(
        "SELECT bmi, date FROM records WHERE name = ? ORDER BY date",
        (name,)
    )
    rows = cursor.fetchall()

    if not rows:
        history_label.config(text="No data to plot for this name")
        return

    # Split rows into two separate lists: one for BMI values, one for dates
    bmi_values = [row[0] for row in rows]
    dates = [row[1] for row in rows]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, bmi_values, marker="o", color="blue")
    plt.title(f"{name}'s BMI Trend")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.xticks(rotation=45)
    plt.tight_layout()  # prevents labels from overlapping
    plt.show()          # opens a new window with the graph


graph_button = tk.Button(root, text="Show Graph", command=show_graph)
graph_button.pack(pady=5)

history_label = tk.Label(root, text="", font=("Arial", 10), justify="left")
history_label.pack(pady=10)

root.mainloop()

# Close the database connection after the window is closed
conn.close()

import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "bmi_history.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM records")
rows = cursor.fetchall()

print(f"Total records in database: {len(rows)}\n")
for row in rows:
    print(row)

conn.close()