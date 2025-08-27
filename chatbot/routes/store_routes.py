import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from flask_socketio import emit, join_room, leave_room
from ..extensions import socketio


# --- Blueprint Definition ---
store_bp = Blueprint('store', 
                     __name__,
                     template_folder='../Store/templates', 
                     static_folder='../Store/static',      
                     url_prefix='/store')

# --- Mock User Database (for demo) ---
USERS = {
    "test@example.com": {"password": "password123", "username": "Test User"},
    "guest@example.com": {"password": "guest", "username": "Guest"}
}

# --- Route Definitions ---

@store_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handles guest access, user login, and displays the login page."""
    
    # 1. Handle Guest Login via URL parameter
    if request.args.get('guest') == 'true':
        guest_email = 'guest@example.com'
        guest_user = USERS.get(guest_email)
        session['user_email'] = guest_email
        session['username'] = guest_user.get('username', 'Guest')
        return redirect(url_for('store.dashboard_page'))

    # 2. Redirect if already logged in
    if 'user_email' in session:
        return redirect(url_for('store.dashboard_page'))

    # 3. Process form submission for real users
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = USERS.get(email)

        if user and user['password'] == password:
            session['user_email'] = email
            session['username'] = user.get('username')
            return redirect(url_for('store.dashboard_page'))
        else:
            return jsonify({"error": "Invalid email or password."}), 401

    # 4. If none of the above, just show the login page
    return render_template('login.html')

@store_bp.route('/')
def dashboard_page():
    """Serves the main store page, protected for logged-in users."""
    if 'user_email' not in session:
        return redirect(url_for('store.login_page'))
    
    # Prepare user info to pass to both the template and JavaScript
    user_info = {
        "email": session.get('user_email'),
        "username": session.get('username', 'Guest')
    }
    
    return render_template('store.html', user_info=user_info)

@store_bp.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('user_email', None)
    session.pop('username', None)
    return redirect(url_for('store.login_page'))

@store_bp.route('/signup', methods=['POST'])
def signup():
    """Handles new user registration."""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    if email in USERS:
        return jsonify({"error": "An account with this email already exists."}), 409
    
    USERS[email] = {'password': password, 'username': request.form.get('username')}
    return jsonify({"success": True, "message": "Account created successfully! Please log in."})

# --- Socket.IO Event Handlers for Store Chatbot ---

@socketio.on('request_agent')
def handle_agent_request(data):
    email_service = current_app.email_service
    """Handle request for a live agent from the store's chatbot."""
    print(f"Agent request received: {data}")
    
    # Get user info from the session or the data sent from the client
    user_id = data.get('user_id')
    username = data.get('username', 'Customer')
    email = data.get('email', '')
    
    # Generate a unique session ID for this chat
    session_id = f"store_chat_{user_id}_{uuid.uuid4().hex[:8]}"
    host_url = request.host_url or 'http://localhost:5000/'
    success, message = email_service.send_agent_notification(session_id, host_url)

    if success:
        print(f"Email notification sent successfully for session {session_id}")
        # email sucess, notify client
        emit('agent_assigned', {
            'session_id': session_id,
            'agent_name': 'Support Agent',
            'message': 'A support agent has been notified and will join your chat shortly.'
        }, room=request.sid)
    else:
        print(f"Failed to send email notification for session {session_id}: {message}")
        # email failed, notify client
        emit('agent_failed', {
            'message': 'We could not reach an agent at the moment. Please try again later.'
        }, room=request.sid)

@socketio.on('join')
def on_join(data):
    """Handle user joining a chat room."""
    room = data.get('room')
    username = data.get('username')
    join_room(room)
    print(f"{username} joined room {room}")
    emit('user_joined_notification', {
        'username': username,
        'message': f'{username} has joined the chat.'
    }, room=room)

@socketio.on('leave')
def on_leave(data):
    """Handle user leaving a chat room."""
    room = data.get('room')
    username = data.get('username')
    leave_room(room)
    print(f"{username} left room {room}")
    emit('user_left_notification', {
        'username': username,
        'message': f'{username} has left the chat.'
    }, room=room)

@socketio.on('message')
def handle_message(data):
    print(f"\n--- 1. SERVER RECEIVED ---")
    print(f"    DATA: {data}")
    
    room = data.get('room')
    # Use 'sender' field from frontend, fall back to 'username' for backward compatibility
    username = data.get('sender') or data.get('username', 'Anonymous')
    # Use 'msg' field from frontend, fall back to 'message' for backward compatibility
    message = data.get('msg') or data.get('message', '')
    user_type = data.get('user_type', 'customer')  # Default to 'customer' if not specified

    payload_to_broadcast = {
        'msg': message,  # Using 'msg' to match frontend expectation
        'sender': username,  # Using 'sender' to match frontend expectation
        'user_type': user_type,
        'username': username  # Keeping for backward compatibility
    }
    
    print(f"--- 2. SERVER BROADCASTING ---")
    print(f"    PAYLOAD: {payload_to_broadcast}\n")
    
    emit('message', payload_to_broadcast, room=room, broadcast=True, include_self=False)

@socketio.on('end_chat')
def handle_end_chat(data):
    """Handle ending a chat session."""
    room = data.get('room')
    username = data.get('username')
    print(f"Chat ended in room {room} by {username}")
    emit('chat_ended', {
        'username': username, 
        'message': f'Chat ended by {username}',
        'room': room
    }, room=room)

