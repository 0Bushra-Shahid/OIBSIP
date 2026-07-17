# Real-Time Chat Application

A full-stack web-based chat application built with Flask and Flask-SocketIO, 
featuring user authentication, multiple chat rooms, and persistent message history.

## Features
- User registration and login (passwords hashed with Werkzeug security)
- Real-time bidirectional messaging using WebSockets (Flask-SocketIO)
- Multiple chat rooms — users can create or join any room by name
- Message history stored in SQLite and loaded when a user joins a room
- Timestamps on every message
- Emoji shortcode support (e.g. `:smile:` → 😄)
- Desktop notifications for new messages when the browser tab is not focused
- Graceful disconnect handling

## Tech Stack
- **Backend:** Python, Flask, Flask-SocketIO, Flask-SQLAlchemy, Flask-Login
- **Frontend:** HTML, CSS, JavaScript (Socket.IO client)
- **Database:** SQLite

## How to Run
1. Clone this repository and navigate to the project folder
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open your browser at `http://127.0.0.1:5000`

### Quick Start (Windows)
After the first-time setup above, you can simply double-click `run.bat`
in the project folder to activate the environment and start the app
in one step — no need to type commands each time.

## Security Notes (Transparency)
- Passwords are hashed using Werkzeug's `generate_password_hash` — never stored in plain text.
- Messages are stored in the local SQLite database (`chat.db`) **without encryption**.
  This is a learning project and is **not** intended for production use with sensitive data.
- There is no end-to-end encryption; anyone with access to the server or database file
  could read message contents.

## Project Structure
```
Chat_Application/
├── app.py               # Backend: routes, database models, SocketIO events
├── requirements.txt      # Python dependencies
├── run.bat               # One-click launcher (Windows)
├── templates/            # HTML pages
│   ├── login.html
│   ├── register.html
│   └── chat.html
├── static/
│   ├── style.css         # Styling
│   └── chat.js           # Real-time chat logic (client-side)
└── README.md
```

## Author
Built as part of the Oasis Infobyte Python Programming Internship (Task 5).
