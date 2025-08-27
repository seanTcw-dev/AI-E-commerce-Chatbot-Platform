import os
import sys

# Add parent directory to import paths
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

# Direct import with full path
from chatbot.services.gemini_service import GeminiManager

def test_gemini_api():
    """Test Gemini API configuration and basic functionality"""
    
    print("--- Testing Gemini API Configuration ---")
    print("-" * 50)
    
    try:
        # Find the root .env file
        root_env_path = os.path.join(parent_dir, '.env')
        print(f"[INFO] Using .env file at: {root_env_path}")
        
        # Initialize Gemini Manager with explicit .env path
        print("[INFO] Initializing Gemini Manager...")
        gemini = GeminiManager(dotenv_path=root_env_path)
        
        # Setup (configure API and initialize model)
        print("[INFO] Setting up Gemini API and model...")
        if not gemini.setup():
            print("[ERROR] Failed to setup Gemini API")
            return False
        
        # Test content generation
        print("[INFO] Testing content generation...")
        success, result = gemini.test_generation()
        
        if success:
            print("[SUCCESS] Content generation successful!")
            print(f"[RESPONSE] {result}")
            return True
        else:
            print(f"[ERROR] Content generation failed: {result}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error with Gemini API: {type(e).__name__} - {e}")
        print("[TIPS] Possible solutions:")
        print("   1. Check your API key is correct")
        print("   2. Make sure the API key has proper permissions")
        print("   3. Check your internet connection")
        print("   4. Verify the GEMINI_API_KEY in your .env file")
        print("   5. Make sure google-generativeai is installed")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n[SUCCESS] Gemini API test completed successfully!")
        print("[OK] Your Gemini AI configuration is ready for the main app.")
    else:
        print("\n[FAILED] Gemini API test failed!")
        print("[ERROR] Please fix the issues above before running the main app.")
