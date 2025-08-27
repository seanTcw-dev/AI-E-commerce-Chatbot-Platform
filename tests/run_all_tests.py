import os
import sys

# Add the parent directory to the path so we can import the test modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from test_gmail_smtp import test_gmail_smtp
from test_gemini_api import test_gemini_api

def run_all_tests():
    """Run all component tests before starting the main application"""
    
    print("[TEST] Running Pre-Flight Tests for Sephora Chatbot")
    print("------------------------")
    
    # Test Gmail SMTP
    print("\n[1] Testing Gmail SMTP Configuration...")
    smtp_success = test_gmail_smtp()
    
    print("\n------------------------")
    
    # Test Gemini API
    print("\n[2] Testing Gemini API Configuration...")
    gemini_success = test_gemini_api()
    
    print("\n------------------------")
    
    # Summary
    print("\n[SUMMARY] TEST RESULTS:")
    print(f"   Gmail SMTP: {'PASS' if smtp_success else 'FAIL'}")
    print(f"   Gemini API: {'PASS' if gemini_success else 'FAIL'}")
    
    if smtp_success and gemini_success:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("[OK] Your application is ready to run.")
        return True
    else:
        print("\n[FAILED] SOME TESTS FAILED!")
        print("[ERROR] Application will NOT start until all tests pass.")
        if not smtp_success:
            print("   [FIX] Fix Gmail SMTP issues first")
        if not gemini_success:
            print("   [FIX] Fix Gemini API issues first")
        print("\n[DEBUG] Run individual tests to debug:")
        print("   python tests\\test_gmail_smtp.py")
        print("   python tests\\test_gemini_api.py")
        return False

def run_tests_only():
    """Run tests without starting the app"""
    print("[TEST] Running Component Tests Only")
    print("------------------------")
    
    # Test Gmail SMTP
    print("\n[1] Testing Gmail SMTP Configuration...")
    smtp_success = test_gmail_smtp()
    
    print("\n------------------------")
    
    # Test Gemini API
    print("\n[2] Testing Gemini API Configuration...")
    gemini_success = test_gemini_api()
    
    print("\n------------------------")
    
    # Summary
    print("\n[SUMMARY] TEST RESULTS:")
    print(f"   Gmail SMTP: {'PASS' if smtp_success else 'FAIL'}")
    print(f"   Gemini API: {'PASS' if gemini_success else 'FAIL'}")
    
    return smtp_success and gemini_success

if __name__ == "__main__":
    # Check if user wants to run tests only or tests + app
    if len(sys.argv) > 1 and sys.argv[1] == "test-only":
        run_tests_only()
    else:
        run_all_tests()
