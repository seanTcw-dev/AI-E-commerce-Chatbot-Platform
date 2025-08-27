# chatbot/extensions.py

from flask_socketio import SocketIO

# Only create the instance, but do not associate it with app
socketio = SocketIO()