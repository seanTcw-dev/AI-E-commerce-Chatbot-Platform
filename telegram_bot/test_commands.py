import asyncio
import sys
import io
from telegram import Bot
from dotenv import load_dotenv
import os

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

async def test_commands():
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    commands = await bot.get_my_commands()
    print("Current bot commands:")
    for cmd in commands:
        # Use .encode().decode() to handle any encoding issues
        cmd_str = f"/{cmd.command} - {cmd.description}"
        try:
            print(cmd_str)
        except UnicodeEncodeError:
            print(cmd_str.encode('utf-8', 'replace').decode('utf-8', 'replace'))

if __name__ == "__main__":
    asyncio.run(test_commands())
