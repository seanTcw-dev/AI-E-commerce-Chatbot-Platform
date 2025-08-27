"""
Telegram Bot Test Script
测试Telegram机器人的所有组件和依赖
"""
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_telegram_imports():
    """测试Telegram相关库的导入"""
    print("📦 Testing Telegram library imports...")
    
    try:
        import telegram
        print("   ✅ telegram library imported successfully")
        
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        print("   ✅ telegram.ext components imported successfully")
        
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import telegram library: {e}")
        print("   💡 Run: pip install python-telegram-bot")
        return False

def test_token_validation():
    """测试Telegram Bot Token"""
    print("\n🔑 Testing Telegram Bot Token...")
    
    TOKEN = "7983101849:AAGWCJawxD001gQmlXbU14v7DwBNuzMUFJg"
    
    try:
        from telegram.ext import Application
        
        # Test creating application
        app = Application.builder().token(TOKEN).build()
        print(f"   ✅ Token configured: {TOKEN[:15]}...")
        print("   ✅ Application created successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Token validation failed: {e}")
        return False

def test_bot_info():
    """测试获取Bot信息"""
    print("\n🤖 Testing Bot Information...")
    
    try:
        import requests
        TOKEN = "7983101849:AAGWCJawxD001gQmlXbU14v7DwBNuzMUFJg"
        
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info['ok']:
                bot_data = bot_info['result']
                print(f"   ✅ Bot verified: @{bot_data['username']}")
                print(f"   ✅ Bot name: {bot_data['first_name']}")
                print(f"   🔗 Direct link: https://t.me/{bot_data['username']}")
                return True
            else:
                print(f"   ❌ Bot API error: {bot_info}")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to get bot info: {e}")
        return False

def test_telegram_service():
    """测试TelegramBotService类"""
    print("\n🔧 Testing TelegramBotService...")
    
    try:
        from chatbot.services.telegram_service import TelegramBotService
        print("   ✅ TelegramBotService imported successfully")
        
        TOKEN = "7983101849:AAGWCJawxD001gQmlXbU14v7DwBNuzMUFJg"
        
        # Create service instance (this will load RAG components)
        service = TelegramBotService(TOKEN)
        print("   ✅ TelegramBotService created successfully")
        
        # Test if RAG components loaded
        if hasattr(service, 'index') and service.index is not None:
            print("   ✅ FAISS index loaded successfully")
        else:
            print("   ⚠️ FAISS index not loaded (this is OK for testing)")
            
        if hasattr(service, 'product_contexts') and service.product_contexts:
            print(f"   ✅ Product contexts loaded: {len(service.product_contexts)} items")
        else:
            print("   ⚠️ Product contexts not loaded (this is OK for testing)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ TelegramBotService error: {e}")
        print("   💡 Will use fallback simple bot")
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n📋 Testing Dependencies...")
    
    dependencies = [
        ('sentence_transformers', 'SentenceTransformer'),
        ('faiss', 'FAISS vector database'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('requests', 'HTTP requests')
    ]
    
    all_good = True
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {description}")
        except ImportError:
            print(f"   ⚠️ {description} not available")
            all_good = False
    
    return all_good

def run_telegram_bot_tests():
    """运行所有Telegram机器人测试"""
    print("🧪 TELEGRAM BOT COMPREHENSIVE TESTS")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("Telegram Imports", test_telegram_imports()))
    test_results.append(("Token Validation", test_token_validation()))
    test_results.append(("Bot Information", test_bot_info()))
    test_results.append(("TelegramBotService", test_telegram_service()))
    test_results.append(("Dependencies", test_dependencies()))
    
    # 显示测试结果
    print("\n📊 TEST SUMMARY")
    print("-" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your Telegram bot is ready!")
        print("🚀 Run: python telegram_bot.py")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_telegram_bot_tests()
    
    if success:
        print("\n✅ Telegram bot system is ready for deployment!")
    else:
        print("\n❌ Please fix the issues before running the bot.")
