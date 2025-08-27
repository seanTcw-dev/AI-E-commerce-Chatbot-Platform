"""
Comprehensive Pre-Launch Test Suite
"""
import os
import sys
import time

# Add current directory to path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def run_gemini_tests():
    """run Gemini API tests"""
    print("🤖 TESTING GEMINI API")
    print("-" * 30)
    
    try:
        # Import and run Gemini tests
        sys.path.append('tests')
        from test_gemini_api import test_gemini_api
        
        result = test_gemini_api()
        if result:
            print("✅ Gemini API tests passed")
            return True
        else:
            print("❌ Gemini API tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test error: {e}")
        return False

def run_telegram_tests():
    """run Telegram Bot tests"""
    print("\n📱 TESTING TELEGRAM BOT")
    print("-" * 30)
    
    try:
        # Import and run Telegram tests
        sys.path.append('tests')
        from test_telegram_bot import run_telegram_bot_tests
        
        result = run_telegram_bot_tests()
        if result:
            print("✅ Telegram bot tests passed")
            return True
        else:
            print("❌ Telegram bot tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Telegram bot test error: {e}")
        return False

def run_system_health_check():
    """system health check"""
    print("\n🔍 SYSTEM HEALTH CHECK")
    print("-" * 30)
    
    checks = []
    
    # 检查关键文件
    critical_files = [
        'chatbot/app.py',
        'chatbot/services/gemini_service.py',
        'chatbot/services/telegram_service.py',
        'cache/faiss_index.idx',
        'cache/product_contexts.pkl'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
            checks.append(True)
        else:
            print(f"   ⚠️ {file_path} not found")
            checks.append(False)
    
    # 检查环境变量文件
    env_files = ['chatbot/.env', '.env']
    env_found = False
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   ✅ Environment file: {env_file}")
            env_found = True
            break
    
    if not env_found:
        print("   ⚠️ No .env file found")
    
    checks.append(env_found)
    
    return all(checks)

def main():
    """主测试函数"""
    print("🚀 SEPHORA TELEGRAM BOT - PRE-LAUNCH TESTS")
    print("=" * 60)
    print("Running comprehensive tests before starting the bot...\n")
    
    # 记录开始时间
    start_time = time.time()
    
    # 运行测试套件
    test_results = []
    
    # 1. 系统健康检查
    health_check = run_system_health_check()
    test_results.append(("System Health", health_check))
    
    # 2. Gemini API测试
    gemini_test = run_gemini_tests()
    test_results.append(("Gemini API", gemini_test))
    
    # 3. Telegram Bot测试
    telegram_test = run_telegram_tests()
    test_results.append(("Telegram Bot", telegram_test))
    
    # 计算测试时间
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    
    # 显示最终结果
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} passed")
    print(f"Duration: {duration} seconds")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS GO!")
        print("✅ Your Sephora Telegram Bot is ready for launch!")
        print("\n🚀 Next steps:")
        print("   1. Run: python telegram_bot.py")
        print("   2. Open Telegram and search: @AiSephora_bot")
        print("   3. Start chatting!")
        
        return True
    else:
        print(f"\n⚠️ {total - passed} system(s) need attention!")
        print("Please resolve the issues above before launching the bot.")
        
        # 提供具体建议
        if not test_results[0][1]:  # System Health
            print("\n💡 System Health Issues:")
            print("   - Check if all required files exist")
            print("   - Verify cache directory and RAG files")
        
        if not test_results[1][1]:  # Gemini API
            print("\n💡 Gemini API Issues:")
            print("   - Check API key in .env file")
            print("   - Verify internet connection")
        
        if not test_results[2][1]:  # Telegram Bot
            print("\n💡 Telegram Bot Issues:")
            print("   - Check Telegram bot token")
            print("   - Install: pip install python-telegram-bot")
        
        return False

if __name__ == "__main__":
    print("Starting pre-launch tests...")
    print("Please wait while we verify all systems...\n")
    
    success = main()
    
    print("\n" + "-" * 60)
    if success:
        print("🔥 READY TO LAUNCH! 🔥")
    else:
        print("🔧 NEEDS ATTENTION 🔧")
    print("-" * 60)
