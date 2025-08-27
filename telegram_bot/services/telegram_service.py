"""
Telegram Bot Service Module for integrating chatbot with Telegram
"""
import asyncio
import logging
import os
import sys
import time
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict, TimedOut, NetworkError
import socketio

# Import GeminiManager from the original chatbot folder
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(os.path.dirname(current_dir))
chatbot_services_path = os.path.join(parent_dir, 'chatbot', 'services')
if chatbot_services_path not in sys.path:
    sys.path.insert(0, chatbot_services_path)

from gemini_service import GeminiManager
from services.telegram_email_service import TelegramEmailService

import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self, token: str):
        """
        Initialize the Telegram bot service
        
        Args:
            token (str): Telegram bot token
        """
        self.token = token
        self.application = (
            Application.builder()
            .token(token)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .write_timeout(30.0)
            .build()
        )
        
        # Initialize AI components
        try:
            self.gemini_manager = GeminiManager()
        except:
            logger.warning("GeminiManager not available, using fallback responses")
            self.gemini_manager = None
            
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load RAG components
        self.load_rag_components()
        
        # Product image mapping for automatic image sending
        self.product_images = {
            'serum': 'Hydra-Essence Serum.png',
            'hydra': 'Hydra-Essence Serum.png',
            'essence': 'Hydra-Essence Serum.png',
            'eye cream': 'Radiance Eye Cream.png',
            'radiance': 'Radiance Eye Cream.png',
            'eye': 'Radiance Eye Cream.png',
            'moisturizer': 'Daily Moisturizer SPF 30.png',
            'spf': 'Daily Moisturizer SPF 30.png',
            'sunscreen': 'Daily Moisturizer SPF 30.png',
            'mask': 'Overnight Repair Mask.png',
            'overnight': 'Overnight Repair Mask.png',
            'repair': 'Overnight Repair Mask.png',
            'cleanser': 'Gentle Cleansing Foam.png',
            'cleansing': 'Gentle Cleansing Foam.png',
            'foam': 'Gentle Cleansing Foam.png',
            'wash': 'Gentle Cleansing Foam.png',
            'oil': 'Botanical Face Oil.png',
            'botanical': 'Botanical Face Oil.png',
            'face oil': 'Botanical Face Oil.png'
        }
        
        # Set up images directory path
        self.images_dir = os.path.join(parent_dir, 'chatbot', 'static', 'images')
        
        # Add handlers
        self.setup_handlers()
        self.email_service = TelegramEmailService()

        # Socket.IO client for agent chat
        self.sio = socketio.Client()
        self.active_agent_chats = {}  # Maps user_id to session_id
        self.sio_connected = False
        self.setup_sio_handlers()
        
    def load_rag_components(self):
        """Load FAISS index and product contexts for RAG"""
        try:
            # Get the parent directory path
            parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            cache_dir = os.path.join(parent_dir, 'cache')
            
            # Load FAISS index
            faiss_path = os.path.join(cache_dir, 'faiss_index.idx')
            if os.path.exists(faiss_path):
                self.index = faiss.read_index(faiss_path)
                logger.info("FAISS index loaded successfully")
            else:
                logger.warning(f"FAISS index not found at {faiss_path}")
                self.index = None
            
            # Load product contexts
            contexts_path = os.path.join(cache_dir, 'product_contexts.pkl')
            if os.path.exists(contexts_path):
                with open(contexts_path, 'rb') as f:
                    self.product_contexts = pickle.load(f)
                logger.info("Product contexts loaded successfully")
            else:
                logger.warning(f"Product contexts not found at {contexts_path}")
                self.product_contexts = []
                
        except Exception as e:
            logger.error(f"Error loading RAG components: {e}")
            self.index = None
            self.product_contexts = []
    
    def setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("products", self.products_command))
        self.application.add_handler(CommandHandler("gallery", self.gallery_command))
        self.application.add_handler(CommandHandler("agent", self.agent_command))
        self.application.add_handler(CommandHandler("end", self.end_agent_chat))
        
        # Message handler for text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        welcome_message = (
            "🌟 *Welcome to Sephora Skincare!* 🌟\n\n"
            "I'm Luna, your personal AI skincare assistant! 💫\n\n"
            "✨ *How can I help you today?* ✨\n\n"
            "Here are some things you can do:\n"
            "• Ask me about our products and get recommendations 🛍️\n"
            "• Get personalized skincare advice 💄\n"
            "• View our product gallery with /gallery 📸\n"
            "• Chat with a live agent using /agent 💬\n\n"
            "*Quick Commands:*\n"
            "/help* - Show all available commands\n"
            "/products* - View our bestsellers\n"
            "/gallery* - Browse products with images\n"
            "/agent* - Connect with a live agent\n\n"
            "Just type your question or use one of the commands above to get started! 💖"
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_message = (
            "💡 *Sephora Skincare Bot Help* 💡\n\n"
            "*Main Commands:*\n"
            "• /start - Show welcome message and main menu\n"
            "• /help - Show this help message\n"
            "• /products - View our bestselling products\n"
            "• /gallery - Browse products with images\n"
            "• /agent - Connect with a live agent\n\n"
            "*What Can I Help You With?*\n"
            "• Product recommendations and information 🛍️\n"
            "• Skincare routines and advice 💆‍♀️\n"
            "• Ingredient explanations 📚\n"
            "• Skin type analysis 🔍\n"
            "• Order status and tracking 📦\n"
            "• And much more! Just ask away! 💬\n\n"
            "*Need Human Assistance?*\n"
            "Type /agent to be connected with one of our beauty experts for personalized help! 💖"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def products_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /products command"""
        products_message = (
            "🛍️ Our Bestselling Products:\n\n"
            "1. 💧 **Hydra-Essence Serum** - RM48.00\n"
            "   Intense hydration with hyaluronic acid\n\n"
            "2. 👁️ **Radiance Eye Cream** - RM36.00\n"
            "   Brightening eye cream with vitamin C\n\n"
            "3. ☀️ **Daily Moisturizer SPF 30** - RM42.00\n"
            "   Lightweight daily protection\n\n"
            "4. 🌙 **Overnight Repair Mask** - RM55.00\n"
            "   Intensive overnight treatment\n\n"
            "5. 🧼 **Gentle Cleansing Foam** - RM28.00\n"
            "   Sulfate-free gentle cleanser\n\n"
            "6. 🌿 **Botanical Face Oil** - RM60.00\n"
            "   Nourishing face oil with rosehip\n\n"
            "Ask me about any of these products for more details! 💫"
        )
        await update.message.reply_text(products_message, parse_mode='Markdown')
    
    async def agent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /agent command to start a live chat session."""
        user_id = update.effective_user.id

        if user_id in self.active_agent_chats:
            await update.message.reply_text('You are already in a chat with an agent.')
            return

        # Connect to the agent chat server on-demand
        if not self.sio_connected:
            try:
                self.sio.connect('http://127.0.0.1:8001', wait_timeout=5)
            except socketio.exceptions.ConnectionError:
                await update.message.reply_text('Sorry, the agent chat service is currently unavailable. Please make sure it is running and try again.')
                return

        session_id = str(uuid.uuid4())
        self.active_agent_chats[user_id] = session_id

        # Join the Socket.IO room for this session
        self.sio.emit('join', {'room': session_id})

        # Notify agents via email
        host_url = "http://127.0.0.1:8001/"
        success, message = self.email_service.send_agent_notification(session_id, host_url)

        if success:
            await update.message.reply_text(
                'You are now connected to a live agent. Please send your message. Type /end to finish the chat.'
            )
            logger.info(f"User {user_id} started agent chat session {session_id}")
        else:
            self.active_agent_chats.pop(user_id) # Clean up
            await update.message.reply_text('Sorry, there was an error notifying an agent. Please try again later.')

    async def gallery_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /gallery command - showcase all product images with details"""
        await update.message.reply_text(
            "🖼️ *Product Gallery* 📸\n\n"
            "Sending you our premium skincare collection... 🌟\n"
            "Tap on any product to learn more! 👇",
            parse_mode='Markdown'
        )
        
        # Product details including descriptions and key benefits
        product_details = {
            'serum': {
                'name': 'Hydra-Essence Serum',
                'price': 'RM48.00',
                'description': 'A lightweight, fast-absorbing serum that delivers intense hydration with hyaluronic acid and vitamin B5.',
                'key_benefits': [
                    'Deeply hydrates for 72 hours',
                    'Plumps and smooths fine lines',
                    'Suitable for all skin types',
                    'Fragrance-free and non-comedogenic'
                ]
            },
            'eye cream': {
                'name': 'Radiance Eye Cream',
                'price': 'RM36.00',
                'description': 'Brightening eye cream with vitamin C and caffeine to reduce dark circles and puffiness.',
                'key_benefits': [
                    'Reduces appearance of dark circles',
                    'Diminishes puffiness',
                    'Hydrates delicate eye area',
                    'Suitable for sensitive skin'
                ]
            },
            'moisturizer': {
                'name': 'Daily Moisturizer SPF 30',
                'price': 'RM42.00',
                'description': 'Lightweight daily moisturizer with broad-spectrum SPF 30 protection and antioxidant benefits.',
                'key_benefits': [
                    'Broad spectrum UVA/UVB protection',
                    'Non-greasy formula',
                    'Antioxidant-rich',
                    'Ideal for daily use'
                ]
            },
            'mask': {
                'name': 'Overnight Repair Mask',
                'price': 'RM55.00',
                'description': 'Intensive overnight treatment mask that works while you sleep to repair and rejuvenate skin.',
                'key_benefits': [
                    'Deeply nourishes overnight',
                    'Reduces appearance of fine lines',
            
                ]
            },
            'cleanser': {
                'name': 'Gentle Cleansing Foam',
                'price': 'RM28.00',
                'description': 'Sulfate-free foaming cleanser that gently removes impurities without stripping skin.',
                'key_benefits': [
                    'Removes makeup and impurities',
                    'Maintains skin\'s natural moisture',
                    'pH balanced',
                    'Suitable for all skin types'
                ]
            },
            'oil': {
                'name': 'Botanical Face Oil',
                'price': 'RM60.00',
                'description': 'Nourishing face oil with rosehip and jojoba oils to restore skin\'s natural radiance.',
                'key_benefits': [
                    'Deeply nourishes dry skin',
                    'Rich in antioxidants',
                    'Helps reduce appearance of scars',
                    'Non-greasy absorption'
                ]
            }
        }
        
        # Send each product with detailed information
        for product_key, details in product_details.items():
            try:
                image_file = self.product_images.get(product_key)
                if not image_file:
                    continue
                    
                image_path = os.path.join(self.images_dir, image_file)
                if not os.path.exists(image_path):
                    logger.warning(f"Image not found: {image_path}")
                    continue
                
                # Format the caption with product details
                benefits = '\n'.join([f'• {benefit}' for benefit in details['key_benefits']])
                
                caption = (
                    f"✨ *{details['name']}* ✨\n\n"
                    f"💵 *Price:* {details['price']}\n\n"
                    f"📝 *Description:*\n{details['description']}\n\n"
                    f"🌟 *Key Benefits:*\n{benefits}\n\n"
                    "💡 *Tip:* Type the product name to learn more or ask for a recommendation!"
                )
                
                # Send the product image with caption
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                
                # Small delay to prevent flooding
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error sending product {product_key}: {e}")
        
        # Send a final message with next steps
        await update.message.reply_text(
            "🎉 *That's our complete collection!* 🎉\n\n"
            "*What would you like to do next?*\n"
            "• Type a product name for more details\n"
            "• Use */products* to see our bestsellers\n"
            "• Try */agent* to chat with a beauty expert\n"
            "• Or just ask me anything about skincare! 💖",
            parse_mode='Markdown'
        )
    
    def detect_product_from_message(self, message: str):
        """
        Detect which product the user is asking about based on keywords
        
        Args:
            message (str): User's message
            
        Returns:
            str or None: Image filename if product detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check for product keywords
        for keyword, image_file in self.product_images.items():
            if keyword in message_lower:
                logger.info(f"Detected product keyword '{keyword}' -> {image_file}")
                return image_file
        
        return None
    
    async def send_product_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE, image_filename: str):
        """
        Send product image to the user
        
        Args:
            update: Telegram update object
            context: Telegram context
            image_filename: Name of the image file to send
        """
        try:
            image_path = os.path.join(self.images_dir, image_filename)
            
            if os.path.exists(image_path):
                # Send the image with a caption
                product_name = image_filename.replace('.png', '').replace('.jpg', '')
                caption = f"📸 Here's our {product_name}! ✨"
                
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=caption
                    )
                logger.info(f"Sent image: {image_filename}")
                return True
            else:
                logger.warning(f"Image not found: {image_path}")
                return False
        except Exception as e:
            logger.error(f"Error sending image {image_filename}: {e}")
            return False

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages, relaying to agent if in an active chat."""
        user_id = update.message.from_user.id
        message_text = update.message.text

        # If user is in an active agent chat, relay the message to the web service.
        if user_id in self.active_agent_chats:
            session_id = self.active_agent_chats[user_id]
            if self.sio_connected:
                # This event is handled by the web service to show the user's message to the agent.
                self.sio.emit('user_to_agent', {
                    'session_id': session_id,
                    'message': message_text,
                    'sender': 'User'
                })
                logger.info(f"BOT_SERVICE: Relayed message from user {user_id} to agent via session {session_id}")
            else:
                await update.message.reply_text("Agent service is not connected. Please wait or try /end.")
            return

        # --- Standard AI Chatbot Logic ---
        logger.info(f"Received message from {update.message.from_user.first_name}: {message_text}")

        image_filename = self.detect_product_from_message(message_text)
        
        if self.gemini_manager:
            try:
                similar_products = self.search_similar_products(message_text)
                response = self.gemini_manager.generate_response(message_text, context=similar_products)
                await update.message.reply_text(response)
                if image_filename:
                    await self.send_product_image(update, context, image_filename)
            except Exception as e:
                logger.error(f"Error with Gemini, using fallback: {e}")
                fallback_response = self.get_fallback_response(message_text)
                await update.message.reply_text(fallback_response)
                if image_filename:
                    await self.send_product_image(update, context, image_filename)
        else:
            fallback_response = self.get_fallback_response(message_text)
            await update.message.reply_text(fallback_response)
            if image_filename:
                await self.send_product_image(update, context, image_filename)

    def search_similar_products(self, query: str, top_k: int = 3):
        """Search for similar products using RAG"""
        try:
            if self.index is None or not self.product_contexts:
                logger.warning("RAG components not loaded. Skipping search.")
                return []

            # Generate embedding for the query
            query_embedding = self.model.encode([query])

            # Search in FAISS index
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)

            # Get relevant contexts
            relevant_contexts = []
            for idx in indices[0]:
                if idx < len(self.product_contexts):
                    relevant_contexts.append(self.product_contexts[idx])

            logger.info(f"Found {len(relevant_contexts)} relevant contexts for query: '{query}'")
            return relevant_contexts

        except Exception as e:
            logger.error(f"Error in RAG search: {e}")
            return []

    def setup_sio_handlers(self):
        """Set up Socket.IO event handlers."""
        @self.sio.on('connect')
        def connect():
            logger.info("BOT_SERVICE: Successfully connected to WebSocket server.")
            self.sio_connected = True

        @self.sio.on('disconnect')
        def disconnect():
            logger.info("BOT_SERVICE: Disconnected from WebSocket server.")
            self.sio_connected = False

        @self.sio.on('agent_to_user')
        def on_agent_to_user(data):
            """Receives a message from the web service (sent by an agent) and relays it to the Telegram user."""
            try:
                session_id = data.get('session_id')
                message = data.get('message')
                
                if not session_id or not message:
                    logger.warning(f"BOT_SERVICE: Received incomplete message from web service: {data}")
                    return
                
                logger.info(f"BOT_SERVICE: Received message for session {session_id}: {message}")
                
                # Find the user_id associated with this session
                user_id = None
                for uid, sid in list(self.active_agent_chats.items()):
                    if sid == session_id:
                        user_id = uid
                        break
                
                if user_id:
                    try:
                        # Create a new event loop for the async operation
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Send the message to the user
                        loop.run_until_complete(
                            self.application.bot.send_message(
                                chat_id=user_id,
                                text=f"💬 *Agent:* {message}",
                                parse_mode='Markdown'
                            )
                        )
                        logger.info(f"BOT_SERVICE: Successfully sent message to user {user_id} in session {session_id}")
                        
                    except Exception as e:
                        logger.error(f"BOT_SERVICE: Error sending message to user {user_id}: {e}")
                        # If there's an error, try to notify the agent
                        self.sio.emit('status', {
                            'msg': f'Failed to send message to user: {str(e)}',
                            'session_id': session_id
                        })
                    finally:
                        loop.close()
                else:
                    logger.warning(f"BOT_SERVICE: Received message for unknown session_id: {session_id}")
                    
            except Exception as e:
                logger.error(f"BOT_SERVICE: Error in on_agent_to_user: {e}", exc_info=True)

    async def end_agent_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """End the active agent chat session for a user."""
        user_id = update.effective_user.id
        
        if user_id in self.active_agent_chats:
            session_id = self.active_agent_chats.pop(user_id) # pop to remove
            
            # Notify agent web client that the user has left
            self.sio.emit('status', {'msg': 'The user has ended the chat.'}, room=session_id)
            self.sio.emit('leave', {'room': session_id})
            
            logger.info(f"User {user_id} ended chat session {session_id}")
            
            await update.message.reply_text(
                'You have disconnected from the live agent. You can now continue chatting with me (Luna). ✨'
            )
        else:
            await update.message.reply_text('You are not currently in a chat with an agent.')

    def get_fallback_response(self, user_message: str) -> str:
        """Get a fallback response when Gemini is not available"""
        message_lower = user_message.lower()
        
        # Product-specific responses with image mention
        if any(word in message_lower for word in ['serum', 'hydration', 'dry skin']):
            return ("🌊 For hydration concerns, I recommend our **Hydra-Essence Serum** (RM48.00)! "
                   "It contains hyaluronic acid for intense moisture. Perfect for dry skin! 💧\n"
                   "📸 Let me show you the product image!")
        
        elif any(word in message_lower for word in ['eye cream', 'dark circles', 'wrinkles']):
            return ("👁️ Try our **Radiance Eye Cream** (RM36.00)! It's enriched with vitamin C "
                   "to brighten and reduce the appearance of dark circles. ✨\n"
                   "📸 Here's what it looks like!")
        
        elif any(word in message_lower for word in ['moisturizer', 'spf', 'sun protection']):
            return ("☀️ Our **Daily Moisturizer SPF 30** (RM42.00) is perfect! It provides "
                   "lightweight hydration plus sun protection in one step. 🌞\n"
                   "📸 Check out the product image!")
        
        elif any(word in message_lower for word in ['cleanser', 'wash', 'cleansing']):
            return ("🧼 I recommend our **Gentle Cleansing Foam** (RM28.00)! It's sulfate-free "
                   "and suitable for all skin types. Gentle yet effective! 💫\n"
                   "📸 See the product below!")
        
        elif any(word in message_lower for word in ['mask', 'overnight', 'treatment']):
            return ("🌙 Our **Overnight Repair Mask** (RM55.00) works while you sleep! "
                   "Wake up to glowing, renewed skin. Perfect for intensive care! ✨\n"
                   "📸 Here's the product image!")
        
        elif any(word in message_lower for word in ['oil', 'nourishing', 'botanical']):
            return ("🌿 The **Botanical Face Oil** (RM60.00) is amazing! Made with rosehip and "
                   "jojoba oils for deep nourishment and a healthy glow. 💚\n"
                   "📸 Let me show you this beautiful product!")
        
        # General responses
        elif any(word in message_lower for word in ['routine', 'skincare routine']):
            return ("✨ A good skincare routine includes: cleanser → serum → moisturizer → SPF! "
                   "I can recommend specific products for each step. What's your skin type? 💫")
        
        else:
            return ("Thank you for your message! 💖 I'm Luna, your Sephora skincare assistant. "
                   "I can help with product recommendations, skincare advice, and beauty tips! "
                   "Use /products to see our bestsellers or ask me anything about skincare! ✨")
    
    async def _initialize_bot(self):
        """Initialize the bot with proper async initialization"""
        try:
            # Initialize the bot
            bot = self.application.bot
            await bot.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            return False

    def run(self):
        """Start the Telegram bot with conflict handling"""
        # The Socket.IO connection is now handled on-demand in the agent_command.
        logger.info("Starting Telegram bot...")
        max_retries = 3
        retry_delay = 10
        
        # Create a new event loop for the current thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the bot
        if not loop.run_until_complete(self._initialize_bot()):
            logger.error("Failed to initialize bot")
            return
        
        for attempt in range(max_retries):
            try:
                self.application.run_polling(
                    drop_pending_updates=True,
                    close_loop=False,
                    stop_signals=None
                )
                break
            except Conflict as e:
                logger.warning(f"Conflict detected (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Please wait a few minutes and try again.")
                    raise
            except (TimedOut, NetworkError) as e:
                logger.warning(f"Network error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise
