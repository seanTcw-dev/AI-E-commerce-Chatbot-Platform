"""
Telegram Bot Reset Script - Use this to clear webhook conflicts
"""
import requests
import time

def reset_telegram_bot(token):
    """Reset the Telegram bot to clear any conflicts"""
    base_url = f"https://api.telegram.org/bot{token}"
    
    print("🔄 Resetting Telegram bot...")
    
    # Delete webhook
    webhook_response = requests.post(f"{base_url}/deleteWebhook")
    if webhook_response.status_code == 200:
        print("✅ Webhook deleted successfully")
    else:
        print(f"⚠️ Webhook deletion response: {webhook_response.status_code}")
    
    # Get bot info to verify connection
    me_response = requests.get(f"{base_url}/getMe")
    if me_response.status_code == 200:
        bot_info = me_response.json()
        if bot_info['ok']:
            print(f"✅ Bot verified: @{bot_info['result']['username']}")
            print(f"   Bot name: {bot_info['result']['first_name']}")
        else:
            print("❌ Bot verification failed")
    else:
        print(f"❌ Failed to get bot info: {me_response.status_code}")
    
    print("⏳ Waiting 5 seconds for changes to take effect...")
    time.sleep(5)
    print("✅ Reset complete! You can now start your bot.")

if __name__ == "__main__":
    TOKEN = "7983101849:AAHvi0-VMh4raf3H0E4rL32AoeuPTWP1tq4"
    reset_telegram_bot(TOKEN)
