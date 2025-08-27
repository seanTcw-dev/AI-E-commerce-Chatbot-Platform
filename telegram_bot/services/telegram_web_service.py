import logging
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the correct paths for templates and static files.
# This ensures that Flask can find the HTML, CSS, and JS files, regardless of how the script is run.
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir) # This should be the 'telegram_bot' directory
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# Set up Flask app
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'secret_telegram_chat!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/agent-chat/<session_id>')
def agent_chat(session_id):
    """Serve the agent chat page."""
    return render_template('telegram_chat_new.html', session_id=session_id)

@socketio.on('join')
def on_join(data):
    """Handle a client joining a room."""
    room = data['room']
    join_room(room)
    print(f"Client joined room: {room}")
    emit('status', {'msg': f'A new user has joined the room {room}.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    """Handle a client leaving a room."""
    room = data['room']
    leave_room(room)
    logger.info(f'WEB_SERVICE: Agent left room: {room}')
    # Optionally notify others in the room
    emit('status', {'msg': 'Agent has left the room.'}, room=room)

@socketio.on('agent_ends_chat')
def on_agent_ends_chat(data):
    session_id = data.get('session_id')
    if not session_id:
        return

    logger.info(f"WEB_SERVICE: Agent is ending chat for session {session_id}")

    # Notify the bot service that the agent has ended the chat
    emit('chat_ended_by_agent', {'session_id': session_id}, broadcast=True)

    # Notify the agent's own UI to disable input
    emit('chat_ended', {'message': 'You have ended the chat. The session is closed.'}, room=session_id)

@socketio.on('user_to_agent')
def handle_user_to_agent(data):
    """
    Receives a message from the Telegram bot service (sent by a user)
    and relays it to the correct agent's web UI.
    """
    session_id = data.get('session_id')
    message = data.get('message')
    sender = data.get('sender', 'User')
    
    if not session_id or not message:
        logger.warning(f"WEB_SERVICE: Received incomplete message from bot service: {data}")
        return

    logger.info(f"WEB_SERVICE: Relaying message from {sender} to agent in session {session_id}: {message}")
    
    # Emit to the specific room (session_id) where the agent is listening
    emit('message_from_user', {
        'message': message,
        'sender': sender,
        'session_id': session_id
    }, room=session_id)

@socketio.on('agent_to_user')
def handle_message_from_agent(data):
    """
    Receives a message from the agent's web UI and forwards it
    to the bot service to be sent to the Telegram user.
    """
    session_id = data.get('session_id') or data.get('room')
    message = data.get('message') or data.get('data')
    sender = data.get('sender')
    
    if not session_id or not message:
        logger.warning(f"WEB_SERVICE: Missing session_id or message in agent_to_user: {data}")
        return

    logger.info(f"WEB_SERVICE: Relaying message from agent to Telegram user (session: {session_id}): {message}")
    
    # Standardize the data format for the bot service
    bot_data = {
        'session_id': session_id,
        'message': message,
        'sender': sender or 'Agent'
    }
    
    # Emit to the bot service (not broadcast, as we want to target specific client)
    emit('agent_to_user', bot_data, room=session_id)
    logger.debug(f"WEB_SERVICE: Emitted 'agent_to_user' for session {session_id}")


@socketio.on('user_to_agent')
def handle_message_from_user(data):
    """
    Receives a message from the bot service (originating from a Telegram user)
    and relays it to the correct agent's web UI.
    """
    room = data.get('session_id')
    message_text = data.get('message')
    sender_name = data.get('sender', 'User')

    if not all([room, message_text]):
        print(f"WEB_SERVICE: Received incomplete message data from bot: {data}")
        return
    
    print(f"WEB_SERVICE: Relaying message from user to agent in room {room}: {message_text}")

    agent_data = {
        'msg': message_text,
        'sender': sender_name
    }

    emit('message', agent_data, room=room)
    print(f"WEB_SERVICE: Emitted 'message' to agent in room {room}")

if __name__ == '__main__':
    print("Starting Telegram Agent Chat Web Service on http://127.0.0.1:8001")
    # Use a different port for the Telegram agent chat
    socketio.run(app, host='127.0.0.1', port=8001, debug=False)
