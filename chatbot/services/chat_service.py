"""
WebSocket Service Module for handling real-time chat functionality
"""
import pandas as pd
from flask_socketio import join_room, leave_room, send

class ChatService:
    def __init__(self, socketio):
        self.socketio = socketio
        # Track which rooms have staff members
        self.rooms_with_staff = {}  # {room_id: staff_info}
        # Track active rooms and users
        self.active_rooms = {}      # {room_id: [list_of_users]}
        
    def handle_join(self, data, request_sid):
        """Handle a user joining a chat room"""
        room = data['room']
        user_type = data.get('user_type', 'customer')  # 'customer' or 'staff'
        user_name = data.get('user_name', 'Anonymous')
        
        # Check if this is a staff member trying to join
        if user_type == 'staff':
            # Check if room already has a staff member
            if room in self.rooms_with_staff:
                # Block additional staff from joining
                send({
                    "msg": f"This chat session already has an agent ({self.rooms_with_staff[room]['name']}). Only one agent per session is allowed.",
                    "sender": "System",
                    "type": "error"
                }, to=request_sid)
                print(f"Blocked staff member {user_name} from joining room {room} - already has staff {self.rooms_with_staff[room]['name']}")
                return
            
            # Add staff to the room tracking
            self.rooms_with_staff[room] = {
                'name': user_name,
                'sid': request_sid
            }
            print(f"Staff member {user_name} joined room {room}")
        
        # Add user to room
        join_room(room)
        
        # Track active rooms and users
        if room not in self.active_rooms:
            self.active_rooms[room] = []
        
        user_info = {
            'name': user_name,
            'type': user_type,
            'sid': request_sid
        }
        self.active_rooms[room].append(user_info)
        
        # Send join notification to room
        join_message = f"{user_name} ({'Agent' if user_type == 'staff' else 'Customer'}) has joined the chat."
        send({
            "msg": join_message,
            "sender": "System",
            "type": "join"
        }, to=room)
        
        print(f"User {user_name} ({user_type}) joined room: {room}")
        
    def handle_leave(self, data, request_sid):
        """Handle a user leaving a chat room"""
        room = data['room']
        user_type = data.get('user_type', 'customer')
        user_name = data.get('user_name', 'Anonymous')
        
        leave_room(room)
        
        # Remove staff from tracking if they're leaving
        if user_type == 'staff' and room in self.rooms_with_staff:
            if self.rooms_with_staff[room]['sid'] == request_sid:
                del self.rooms_with_staff[room]
                print(f"Staff member {user_name} left room {room} - room now available for other staff")
        
        # Remove user from active rooms tracking
        if room in self.active_rooms:
            self.active_rooms[room] = [user for user in self.active_rooms[room] if user['sid'] != request_sid]
            if not self.active_rooms[room]:  # If room is empty, clean it up
                del self.active_rooms[room]
        
        # Send leave notification
        leave_message = f"{user_name} ({'Agent' if user_type == 'staff' else 'Customer'}) has left the chat."
        send({
            "msg": leave_message,
            "sender": "System",
            "type": "leave"
        }, to=room)
        
        print(f"User {user_name} ({user_type}) left room: {room}")
        
    def handle_message(self, data):
        """Handle a chat message"""
        room = data['room']
        user_name = data.get('sender', 'Anonymous')
        message = data.get('msg', '')
        user_type = data.get('user_type', 'customer')
        
        # Broadcast the message to everyone in the room
        send({
            "msg": message,
            "message": message,  # Send both for compatibility
            "sender": user_name,
            "user_type": user_type,
            "timestamp": pd.Timestamp.now().strftime('%H:%M:%S')
        }, to=room)
        
        print(f"Message in room {room} from {user_name} ({user_type}): {message}")
        
    def get_room_status(self, room_id):
        """Get status information for a chat room"""
        has_staff = room_id in self.rooms_with_staff
        staff_name = self.rooms_with_staff[room_id]['name'] if has_staff else None
        active_users = len(self.active_rooms.get(room_id, []))
        
        return {
            "room_id": room_id,
            "has_staff": has_staff,
            "staff_name": staff_name,
            "active_users": active_users,
            "can_staff_join": not has_staff
        }

    def handle_end_chat(self, data, request_sid):
        """Handle ending a chat session"""
        room = data['room']
        ender_name = data.get('ender_name', 'Unknown')
        user_type = data.get('user_type', 'customer')
        
        print(f"Chat session in room {room} ended by {ender_name} ({user_type})")
        
        # Remove staff from tracking if they exist
        if room in self.rooms_with_staff:
            del self.rooms_with_staff[room]
        
        # Notify all users in the room that the chat has ended
        self.socketio.emit('chat_ended', {
            "ender_name": ender_name,
            "ender_type": user_type,
            "room": room
        }, to=room)
        
        # Clean up the room
        if room in self.active_rooms:
            del self.active_rooms[room]
        
        print(f"Room {room} cleaned up after chat end")
