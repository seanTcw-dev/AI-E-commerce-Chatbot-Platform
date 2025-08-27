import os
import logging
import multiprocessing
import sys
import asyncio
from dotenv import load_dotenv

# Add the services directory to the Python path
# This ensures that the service modules can be found
current_dir = os.path.dirname(__file__)
services_path = os.path.join(current_dir, 'services')
if services_path not in sys.path:
    sys.path.insert(0, services_path)

from telegram import Bot
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ExtBot
from telegram_service import TelegramBotService
from telegram_web_service import app, socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def set_bot_commands():
    """Set up the bot commands using the Telegram Bot API."""
    try:
        # Create a bot instance with HTTPX request object
        request = HTTPXRequest(connection_pool_size=8)
        bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'), request=request)
        
        # Initialize the bot
        await bot.initialize()
        
        commands = [
            ("start", "🚀 Start the bot and see welcome message"),
            ("help", "ℹ️ Show help information and commands"),
            ("products", "🛍️ View our best-selling products"),
            ("gallery", "📸 Browse products with images"),
            ("agent", "💬 Connect with a live agent"),
            ("end", "❌ End the current agent chat")
        ]
        
        # Convert to BotCommand objects
        from telegram import BotCommand
        bot_commands = [BotCommand(command=cmd[0], description=cmd[1]) for cmd in commands]
        
        await bot.set_my_commands(bot_commands)
        logger.info("Successfully set bot commands")
        return True
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}", exc_info=True)
        return False

async def send_welcome_message(bot_token: str, chat_id: str):
    """Send the welcome message directly, simulating the /start command."""
    try:
        # Create a bot instance with HTTPX request object
        request = HTTPXRequest(connection_pool_size=8)
        bot = Bot(token=bot_token, request=request)
        await bot.initialize()
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
        await bot.send_message(chat_id=chat_id, text=welcome_message, parse_mode='Markdown')
        logger.info(f"Sent welcome message to chat {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")
        return False

async def setup_bot():
    """Set up the Telegram bot and its commands."""
    load_dotenv()
    
    # Get bot token and chat ID
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Add your chat ID to .env file
    
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return None
    
    # Set up bot commands
    await set_bot_commands()
    
    # Send welcome message if chat_id is provided
    if chat_id:
        await send_welcome_message(bot_token, chat_id)
    else:
        logger.warning("TELEGRAM_CHAT_ID not found in environment variables. Welcome message will not be sent.")
    
    return TelegramBotService(bot_token)

def run_web_service():
    """Function to run the Flask-SocketIO web service in a separate process."""
    logger.info("Starting agent web service on http://127.0.0.1:8001")
    try:
        # Use allow_unsafe_werkzeug=True for development with newer Werkzeug versions
        socketio.run(app, host='127.0.0.1', port=8001, allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Web service failed: {e}", exc_info=True)

def main():
    """Main function to start the Telegram bot and web service."""
    # Set up the bot and its commands
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    telegram_bot = loop.run_until_complete(setup_bot())
    
    if not telegram_bot:
        logger.error("Failed to set up the Telegram bot")
        return

    print("🚀 SEPHORA TELEGRAM BOT - UNIFIED RUNNER")
    print("=" * 40)

    # Load environment variables from .env file
    # Assumes .env file is in the parent directory of the 'telegram_bot' folder
    env_path = os.path.join(os.path.dirname(current_dir), '.env')
    load_dotenv(dotenv_path=env_path)
    
    # Start the web service in a separate, daemonized process
    web_process = multiprocessing.Process(target=run_web_service, daemon=True)
    web_process.start()
    logger.info(f"Agent web service started with PID: {web_process.pid}")

    # Initialize and run the bot service in the main process
    try:
        # Get the bot token from environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
            return
            
        bot_service = TelegramBotService(token=bot_token)
        logger.info("🤖 Starting Telegram bot service...")
        bot_service.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot service stopped by user.")
    except Exception as e:
        logger.error(f"❌ Failed to start bot service: {e}", exc_info=True)
    finally:
        # Ensure the web service process is terminated when the bot stops
        logger.info("Terminating web service process...")
        web_process.terminate()
        web_process.join() # Wait for the process to finish
        logger.info("✅ Shutdown complete.")

if __name__ == '__main__':
    # This is crucial for multiprocessing to work correctly on Windows
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    main()
