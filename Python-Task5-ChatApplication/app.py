# app.py
# Main backend file: handles routes, database, login, and socket events

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ---------- App Configuration ----------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---------- Database Models ----------

# User table: stores username and hashed password
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Message table: stores chat history per room
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Load logged-in user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Routes ----------

# Home route: redirect to chat if logged in, else to login page
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

# Register route: create a new user account
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Try another.')
            return redirect(url_for('register'))

        # Hash the password before saving (never store plain text)
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route: verify credentials and start a session
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # Check user exists and password matches
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout route: end the session
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Chat route: main chat page (only for logged-in users)
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)


# ---------- SocketIO Events (Real-Time Chat Logic) ----------

# Triggered when a user joins a room
@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)  # add this user's connection to the room

    # Fetch last 50 messages from this room (message history)
    past_messages = Message.query.filter_by(room=room).order_by(Message.timestamp).limit(50).all()

    history = [
        {
            'username': msg.username,
            'message': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M')
        }
        for msg in past_messages
    ]

    # Send history only to the user who just joined
    emit('load_history', history)

    # Notify everyone in the room that a new user joined
    emit('receive_message', {
        'username': 'System',
        'message': f'{username} has joined the room.',
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }, room=room)

# Triggered when a user sends a message
@socketio.on('send_message')
def handle_send_message(data):
    username = data['username']
    room = data['room']
    message = data['message']

    # Save message to database (persistent history)
    new_message = Message(username=username, room=room, content=message)
    db.session.add(new_message)
    db.session.commit()

    # Broadcast the message to everyone in the room
    emit('receive_message', {
        'username': username,
        'message': message,
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }, room=room)

# Triggered when a user disconnects (closes tab/browser)
@socketio.on('disconnect')
def handle_disconnect():
    print('A user disconnected.')  # graceful disconnect handling (logged server-side)


# ---------- Run the App ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # create database tables if they don't exist
    socketio.run(app, debug=True)