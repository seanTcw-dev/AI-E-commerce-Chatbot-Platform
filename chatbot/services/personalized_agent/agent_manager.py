# Beauty Companion - Enhanced Personalized Agent Manager
# This module handles the core logic for personalized AI beauty companions

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

class PersonalizedAgentManager:
    """
    Enhanced manager for personalized Beauty Companion agents.
    Features include custom personalities, persistent chat history,
    background customization, and multi-profile support.
    """
    
    def __init__(self, profiles_file='companion_profiles.json', db_path=None):
        """
        Initialize the enhanced agent manager.
        
        Args:
            profiles_file: JSON file for storing companion profiles
            db_path: Path to SQLite database for persistent storage
        """
        self.profiles_path = os.path.join(os.path.dirname(__file__), profiles_file)
        
        # Initialize database for persistent storage
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(__file__), 'beauty_companions.db')
        else:
            self.db_path = db_path
            
        self._init_database()
        self.profiles = self._load_profiles()
        self._create_default_templates()

    def _init_database(self):
        """Initialize SQLite database with enhanced schema for Beauty Companion."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enhanced companions table with new features
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT DEFAULT 'guest',
                    name TEXT NOT NULL,
                    personality_type TEXT DEFAULT 'friendly',
                    tone TEXT DEFAULT 'professional',
                    behavior_style TEXT DEFAULT 'helpful',
                    background_color TEXT DEFAULT '#f8f9fa',
                    background_image TEXT,
                    background_pattern TEXT,
                    greeting_message TEXT,
                    custom_instructions TEXT,
                    expertise_focus TEXT DEFAULT 'general',
                    response_length TEXT DEFAULT 'medium',
                    emoji_usage TEXT DEFAULT 'moderate',
                    is_active BOOLEAN DEFAULT 0,
                    is_template BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            ''')
            
            # Enhanced chat history with session management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id TEXT PRIMARY KEY,
                    companion_id TEXT,
                    session_id TEXT,
                    user_message TEXT,
                    bot_response TEXT,
                    message_type TEXT DEFAULT 'chat',
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (companion_id) REFERENCES companions (id)
                )
            ''')
            
            # User sessions for better tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    companion_id TEXT,
                    user_id TEXT DEFAULT 'guest',
                    session_name TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    FOREIGN KEY (companion_id) REFERENCES companions (id)
                )
            ''')
            
            conn.commit()

    def _load_profiles(self):
        """Load companion profiles from JSON file with enhanced structure."""
        if not os.path.exists(self.profiles_path):
            default_profiles = self._get_default_profiles()
            self._save_profiles(default_profiles)
            return default_profiles
        
        try:
            with open(self.profiles_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            default_profiles = self._get_default_profiles()
            self._save_profiles(default_profiles)
            return default_profiles

    def _get_default_profiles(self):
        """Create enhanced default companion profiles."""
        return {
            "templates": {
                "beauty_guru": {
                    "id": "beauty_guru_template",
                    "name": "Luna",
                    "personality_type": "expert",
                    "tone": "knowledgeable",
                    "behavior_style": "professional",
                    "background_color": "#f8e8f0",
                    "background_pattern": "subtle-gradient",
                    "greeting_message": "Hello beauty! I'm Luna, your expert beauty advisor. Ready to discover your perfect look? ✨",
                    "custom_instructions": "You are a knowledgeable beauty expert with years of experience. Provide detailed, professional advice while being warm and encouraging.",
                    "expertise_focus": "skincare_makeup",
                    "response_length": "detailed",
                    "emoji_usage": "moderate",
                    "is_template": True
                },
                "friendly_companion": {
                    "id": "friendly_template",
                    "name": "Aria",
                    "personality_type": "friendly",
                    "tone": "casual",
                    "behavior_style": "supportive",
                    "background_color": "#fff2e6",
                    "background_pattern": "warm-gradient",
                    "greeting_message": "Hey gorgeous! I'm Aria, your beauty bestie. Let's chat about all things beauty! 💄✨",
                    "custom_instructions": "You are a friendly, enthusiastic beauty companion. Use casual language, be supportive, and make users feel confident.",
                    "expertise_focus": "trends_lifestyle",
                    "response_length": "medium",
                    "emoji_usage": "frequent",
                    "is_template": True
                },
                "luxury_consultant": {
                    "id": "luxury_template",
                    "name": "Victoria",
                    "personality_type": "sophisticated",
                    "tone": "elegant",
                    "behavior_style": "refined",
                    "background_color": "#f5f0ff",
                    "background_pattern": "luxury-gradient",
                    "greeting_message": "Good day. I'm Victoria, your luxury beauty consultant. How may I assist you in elevating your beauty routine?",
                    "custom_instructions": "You are a sophisticated luxury beauty consultant. Speak elegantly, recommend premium products, focus on high-end experiences.",
                    "expertise_focus": "luxury_premium",
                    "response_length": "detailed",
                    "emoji_usage": "minimal",
                    "is_template": True
                },
                "trendy_advisor": {
                    "id": "trendy_template",
                    "name": "Zoe",
                    "personality_type": "trendy",
                    "tone": "energetic",
                    "behavior_style": "innovative",
                    "background_color": "#ffe6f2",
                    "background_pattern": "vibrant-gradient",
                    "greeting_message": "OMG hey! I'm Zoe and I'm obsessed with the latest beauty trends! Let's get you looking absolutely stunning! 🔥💅",
                    "custom_instructions": "You are a trendy, energetic beauty advisor who knows all the latest trends. Use modern language and focus on viral looks and current trends.",
                    "expertise_focus": "trends_social",
                    "response_length": "medium",
                    "emoji_usage": "frequent",
                    "is_template": True
                }
            },
            "user_companions": {}
        }

    def _create_default_templates(self):
        """Create default companion templates in the database if they don't exist."""
        default_templates = [
            {
                'id': 'beauty_guru_template',
                'name': 'Luna',
                'personality_type': 'professional',
                'tone': 'knowledgeable',
                'behavior_style': 'helpful',
                'greeting_message': "Hello! I'm Luna, your professional beauty expert. How can I assist you today?",
                'custom_instructions': "You are a professional beauty expert with extensive knowledge. Provide detailed, accurate beauty advice.",
                'is_template': True
            },
            {
                'id': 'friendly_template', 
                'name': 'Aria',
                'personality_type': 'friendly',
                'tone': 'warm',
                'behavior_style': 'supportive',
                'greeting_message': "Hey there! I'm Aria, your friendly beauty bestie! Ready to explore some amazing beauty tips together? 💕",
                'custom_instructions': "You are a friendly, supportive beauty companion. Be encouraging and make users feel confident.",
                'is_template': True
            },
            {
                'id': 'luxury_template',
                'name': 'Victoria', 
                'personality_type': 'sophisticated',
                'tone': 'elegant',
                'behavior_style': 'refined',
                'greeting_message': "Good day. I'm Victoria, your luxury beauty consultant. How may I assist you in elevating your beauty routine?",
                'custom_instructions': "You are a sophisticated luxury beauty consultant. Speak elegantly and focus on premium experiences.",
                'is_template': True
            },
            {
                'id': 'trendy_template',
                'name': 'Zoe',
                'personality_type': 'trendy', 
                'tone': 'energetic',
                'behavior_style': 'innovative',
                'greeting_message': "Hey! I'm Zoe and I'm obsessed with the latest beauty trends! Let's get you looking stunning! 🔥",
                'custom_instructions': "You are a trendy beauty advisor who knows all the latest trends. Use modern language and focus on viral looks.",
                'is_template': True
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for template in default_templates:
                cursor.execute('''
                    INSERT OR IGNORE INTO companions (
                        id, name, personality_type, tone, behavior_style, 
                        greeting_message, custom_instructions, is_template
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template['id'], template['name'], template['personality_type'],
                    template['tone'], template['behavior_style'], template['greeting_message'],
                    template['custom_instructions'], template['is_template']
                ))
            conn.commit()

    def get_all_profiles(self):
        return list(self.profiles.values())

    def get_profile(self, profile_id):
        return self.profiles.get(profile_id)

    def create_profile(self, profile_data):
        profile_id = str(uuid.uuid4())
        new_profile = {
            "id": profile_id,
            "name": profile_data.get("name", "New Companion"),
            "personality": profile_data.get("personality", "friendly"),
            "greeting": profile_data.get("greeting", "Hello! How can I help?"),
            "bgColor": profile_data.get("bgColor", "#ffffff"),
            "bgImage": profile_data.get("bgImage", ""),
            "history": []
        }
        self.profiles[profile_id] = new_profile
        self._save_profiles(self.profiles)
        return new_profile

    def update_profile(self, profile_id, update_data):
        if profile_id in self.profiles:
            # Prevent changing the ID or history directly
            update_data.pop('id', None)
            update_data.pop('history', None)
            
            self.profiles[profile_id].update(update_data)
            self._save_profiles(self.profiles)
            return self.profiles[profile_id]
        return None

    def delete_profile(self, profile_id):
        if profile_id in self.profiles and profile_id != 'default':
            del self.profiles[profile_id]
            self._save_profiles(self.profiles)
            return True
        return False

    def save_chat_message(self, profile_id, session_id, user_message, bot_response):
        if profile_id in self.profiles:
            chat_item = {
                "session_id": session_id,
                "user": user_message,
                "bot": bot_response,
                "timestamp": str(datetime.now())
            }
            # Ensure history is a list
            if 'history' not in self.profiles[profile_id] or not isinstance(self.profiles[profile_id]['history'], list):
                self.profiles[profile_id]['history'] = []
            
            self.profiles[profile_id]['history'].append(chat_item)
            self._save_profiles(self.profiles)

    def generate_personalized_prompt(self, profile_id, user_message):
        profile = self.get_profile(profile_id)
        if not profile:
            # Fallback to a generic prompt if profile_id is not found
            profile = {
                'name': 'Sephora Assistant',
                'personality': 'friendly'
            }

        # Base prompt
        base_prompt = (
            "You are a helpful and knowledgeable shopping assistant for Sephora, a skincare and cosmetics brand. "
            "Answer the user's question based ONLY on the following product information. "
            "If the provided product information isn't sufficient or doesn't directly answer the question, "
            "clearly state that you don't have the specific detail based on the provided context, but you can help with other product questions. "
            "Do not make up information not present in the context. Prices are in USD."
        )

        # Personality adjustments
        personality = profile.get('personality', 'friendly')
        if personality == 'professional':
            personality_prompt = "Your tone should be formal and professional."
        elif personality == 'humorous':
            personality_prompt = "Your tone should be light-hearted and include some humor."
        elif personality == 'witty':
            personality_prompt = "Your tone should be witty and a bit sassy."
        else: # friendly
            personality_prompt = "Your tone should be warm, friendly, and encouraging."

        # Construct the full prompt
        full_prompt = f"{base_prompt}\n\nYour name is {profile.get('name', 'Sephora Assistant')}. {personality_prompt}"
        
        return full_prompt
