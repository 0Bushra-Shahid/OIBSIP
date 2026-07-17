// chat.js: handles real-time messaging, room joining, and emoji conversion

const socket = io();  // connect to the Flask-SocketIO server

let currentRoom = null;

const roomInput = document.getElementById('room-input');
const joinBtn = document.getElementById('join-btn');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesBox = document.getElementById('messages');
const currentRoomLabel = document.getElementById('current-room');

// Simple emoji shortcode map (e.g. :smile: -> 😄)
const emojiMap = {
    ':smile:': '😄',
    ':laugh:': '😂',
    ':heart:': '❤️',
    ':thumbsup:': '👍',
    ':sad:': '😢',
    ':fire:': '🔥'
};

// Replace emoji shortcodes in a message with actual emoji characters
function convertEmojis(text) {
    let result = text;
    for (const [code, emoji] of Object.entries(emojiMap)) {
        result = result.split(code).join(emoji);
    }
    return result;
}

// Join or create a room
joinBtn.addEventListener('click', () => {
    const room = roomInput.value.trim();
    if (!room) return;

    currentRoom = room;
    socket.emit('join', { username: username, room: room });

    currentRoomLabel.textContent = `Room: ${room}`;
    messagesBox.innerHTML = '';  // clear previous room's messages from view
    messageInput.disabled = false;
    sendBtn.disabled = false;
});

// Send a message
function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !currentRoom) return;

    socket.emit('send_message', {
        username: username,
        room: currentRoom,
        message: text
    });

    messageInput.value = '';
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Load past messages when joining a room
socket.on('load_history', (history) => {
    history.forEach(displayMessage);
});

// Receive a new message in real-time
socket.on('receive_message', (data) => {
    displayMessage(data);

    // Show browser notification if window is not focused
    if (!document.hasFocus() && data.username !== username) {
        if (Notification.permission === 'granted') {
            new Notification(`${data.username} in ${data.room}`, { body: data.message });
        }
    }
});

// Display a single message in the chat window
function displayMessage(data) {
    const p = document.createElement('p');
    const time = data.timestamp;
    const text = convertEmojis(data.message);
    p.innerHTML = `<strong>[${time}] ${data.username}:</strong> ${text}`;
    messagesBox.appendChild(p);
    messagesBox.scrollTop = messagesBox.scrollHeight;  // auto-scroll to latest
}

// Ask permission for desktop notifications
if (Notification.permission !== 'granted') {
    Notification.requestPermission();
}