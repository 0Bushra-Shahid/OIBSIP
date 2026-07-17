# BMI Calculator (Advanced) — Python Programming Internship (OIBSIP)

## 📌 Objective
A GUI-based Python program that calculates a user's Body Mass Index (BMI),
classifies it into health categories, stores historical records per user in
an SQLite database, and displays a BMI trend graph over time.

## 🛠️ Tech Stack
- Python 3
- tkinter (GUI)
- sqlite3 (data persistence)
- matplotlib (trend visualisation)
- datetime (timestamps)

## ✨ Features
- GUI window built with tkinter — no command line needed
- Input fields for Name, Weight (kg), and Height (m)
- BMI calculated using the formula: `BMI = weight / (height²)`
- Result colour-coded by category:
  - Underweight → Orange
  - Normal → Green
  - Overweight → Orange
  - Obese → Red
- Input validation: rejects non-numeric and non-positive values with a clear error message
- Multi-user support: records are saved and filtered by name
- Historical records stored in an SQLite database (`bmi_history.db`)
- "View History" button displays all past entries for the entered name
- "Show Graph" button plots BMI trend over time using matplotlib

## ▶️ How to Run
1. Install matplotlib (tkinter and sqlite3 come built-in with Python):
   ```
   pip install matplotlib
   ```
2. Run the script:
   ```
   python BMI.py
   ```
3. Enter your name, weight, and height, then click **Calculate**.
4. Click **View History** to see past records, or **Show Graph** to see your BMI trend.

## 🗄️ Database Schema
Table: `records`

| Column   | Type    | Description                    |
|----------|---------|---------------------------------|
| id       | INTEGER | Auto-incrementing primary key  |
| name     | TEXT    | User's name                     |
| weight   | REAL    | Weight in kg                    |
| height   | REAL    | Height in metres                |
| bmi      | REAL    | Calculated BMI value            |
| category | TEXT    | BMI classification               |
| date     | TEXT    | Timestamp of the entry          |

## 📂 Folder Structure (as per OIBSIP guidelines)
```
OIBSIP/Python-Task2-BMICalculator/
├── bmi_calculator.py
├── bmi_history.db (generated after first run)
├── README.md
└── screenshots/
```

## 🙋 Notes
- Passwords/security are not applicable here since this task doesn't involve login.
- Error handling uses `try/except ValueError` to catch invalid (non-numeric) input.
- Parameterised SQL queries (`?` placeholders) are used throughout to prevent SQL injection.

```

## Author
-BUSHRA SHAHID