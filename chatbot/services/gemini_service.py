"""
Gemini AI Service for managing Gemini API integration
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiManager:
    """Handles Gemini API configuration and model management"""
    
    def __init__(self, dotenv_path=None):
        """Initialize Gemini manager with optional .env path"""
        self.api_key = None
        self.model = None
        self.is_configured = False
        
        # Load environment variables
        if dotenv_path:
            load_dotenv(dotenv_path=dotenv_path)
        else:
            # Default path - look for .env in parent directory
            default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
            load_dotenv(dotenv_path=default_path)
    
    def configure_api(self):
        """Configure Gemini API with the API key from environment"""
        try:
            self.api_key = os.environ.get("GOOGLE_API_KEY")
            if not self.api_key:
                raise KeyError("GOOGLE_API_KEY not found in environment variables")
            
            genai.configure(api_key=self.api_key)
            print("[OK] Gemini API configured successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error configuring Gemini API: {e}")
            return False
    
    def initialize_model(self, model_name='gemini-1.5-flash'):
        """Initialize the Gemini model"""
        try:
            if not self.api_key:
                raise Exception("API key not configured. Call configure_api() first.")
            
            self.model = genai.GenerativeModel(model_name)
            self.is_configured = True
            print(f"[OK] Gemini model '{model_name}' initialized successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error initializing Gemini model: {e}")
            self.is_configured = False
            return False
    
    def setup(self, model_name='gemini-1.5-flash'):
        """Complete setup: configure API and initialize model"""
        if self.configure_api() and self.initialize_model(model_name):
            return True
        return False
    
    def generate_content(self, prompt):
        """Generate content using the Gemini model"""
        if not self.is_configured or not self.model:
            raise Exception("Gemini model not properly configured. Call setup() first.")
        
        try:
            response = self.model.generate_content(prompt)
            
            # Extract response text (same logic as in app.py)
            response_text = ""
            if response.parts:
                for part in response.parts:
                    response_text += part.text
            elif hasattr(response, 'text') and response.text:
                response_text = response.text
            elif response.candidates:
                response_text = response.candidates[0].content.parts[0].text
            
            if not response_text:
                raise Exception("No response text received from Gemini")
            
            return response_text
            
        except Exception as e:
            raise Exception(f"Error generating content: {e}")
    
    def test_generation(self):
        """Test content generation with a simple prompt"""
        try:
            test_response = self.generate_content("Hello, please respond with 'Gemini API is working correctly!'")
            return True, test_response
        except Exception as e:
            return False, str(e)
    
    def get_model(self):
        """Get the initialized model (for backward compatibility with app.py)"""
        if not self.is_configured:
            raise Exception("Gemini model not configured")
        return self.model

# Convenience function for quick setup
def setup_gemini(dotenv_path=None, model_name='gemini-1.5-flash'):
    """Quick setup function that returns a configured GeminiManager"""
    manager = GeminiManager(dotenv_path=dotenv_path)
    if manager.setup(model_name=model_name):
        return manager
    return None
