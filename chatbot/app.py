# Flask backend for the chatbot with RAG

import os
import sys
import subprocess
import uuid
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
import numpy as np
import google.generativeai as genai
import faiss
import pickle
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from flask_socketio import SocketIO
from flask import send_from_directory
from routes.main_routes import main_bp
from routes.store_routes import store_bp
from routes.studio_routes import studio_bp
from services.extensions import socketio

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables from root .env file
root_env_path = os.path.join(project_root, '.env')
if os.path.exists(root_env_path):
    load_dotenv(root_env_path, override=True)
    print(f"Loaded environment variables from: {root_env_path}")
else:
    print(f"Warning: Could not find .env file at {root_env_path}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    ]
)
logger = logging.getLogger(__name__)

# Import the function from embedFunc.py
# Import from parent directory's renamed Vector_Store folder
try:
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    vector_store_path = os.path.join(parent_dir, 'Vector_Store')
    
    # Add paths to sys.path for import resolution
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    if vector_store_path not in sys.path:
        sys.path.insert(0, vector_store_path)
    
    # Import the function
    from embedFunc import generate_embeddings_and_cache  # type: ignore
    print("[OK] Successfully imported generate_embeddings_and_cache from Vector_Store directory")
except ImportError as e:
    print(f"[ERROR] Failed to import generate_embeddings_and_cache: {e}")
    print("[WARNING] RAG functionality will not work.")
    # Define a dummy function to prevent runtime errors
    def generate_embeddings_and_cache():
        print("Warning: embedFunc module not available, skipping embedding generation")
        return True

# Import custom service modules with error handling
try:
    from services.email_service import EmailService
    from services.chat_service import ChatService
    from services.gemini_service import GeminiManager
    print("[OK] Successfully imported core services")
except ImportError as e:
    print(f"[WARNING] Failed to import some services: {e}")
    # Create dummy classes to prevent crashes
    class EmailService:
        def send_agent_notification(self, session_id, host_url):
            return False, "Email service not available"
    
    class ChatService:
        def __init__(self, socketio):
            pass
        def handle_join(self, data, sid):
            pass
        def handle_leave(self, data, sid):
            pass
        def handle_message(self, data):
            pass
        def handle_end_chat(self, data, sid):
            pass
        def get_room_status(self, room_id):
            return {"status": "Service unavailable"}
    
    class GeminiManager:
        def __init__(self, dotenv_path=None):
            self.is_configured = False
        def setup(self):
            return False
        def generate_content(self, prompt):
            return "Sorry, AI service is not available."

# Import personalized agent blueprint with error handling
try:
    from services.personalized_agent.routes import personalized_agent_bp
    personalized_agent_available = True
    print("[OK] Successfully imported personalized agent blueprint")
except ImportError as e:
    print(f"[WARNING] Failed to import personalized agent: {e}")
    # Create a dummy blueprint
    from flask import Blueprint
    personalized_agent_bp = Blueprint('personalized_agent', __name__)
    personalized_agent_available = False

# Load environment variables from .env file with absolute path
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

# Check for agents.txt in both chatbot directory and parent directory
agents_file_local = os.path.join(os.path.dirname(__file__), 'agents.txt')
agents_file_parent = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agents.txt')

# Determine which agents file to use without copying
agents_file_path = None
if os.path.exists(agents_file_local):
    agents_file_path = agents_file_local
    print(f"Using agents.txt file at: {agents_file_local}")
elif os.path.exists(agents_file_parent):
    agents_file_path = agents_file_parent
    print(f"Using agents.txt file at: {agents_file_parent}")
else:
    print("Warning: agents.txt file not found. No agents will be notified.")

# Store the agents file path for use by the email service
if agents_file_path:
    os.environ['AGENTS_FILE_PATH'] = agents_file_path

app = Flask(__name__, template_folder='templates')
# Configure CORS to allow all origins for development and network access
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
        "supports_credentials": True
    }
})
socketio.init_app(app, 
                 cors_allowed_origins="*", 
                 async_mode='threading',
                 engineio_logger=False,
                 socketio_logger=False)

# Configure session secret key for the personalized agent feature
app.secret_key = os.environ.get('SECRET_KEY', 'sephora-beauty-companion-secret-key-2024')
# --- Initialize Services ---
email_service = EmailService()
chat_service = ChatService(socketio)
app.email_service = email_service

# Register the personalized agent blueprint
app.register_blueprint(personalized_agent_bp)
app.register_blueprint(main_bp)
app.register_blueprint(store_bp)
app.register_blueprint(studio_bp)

# Add health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "rag_available": faiss_index is not None and len(product_contexts_for_llm) > 0,
        "gemini_available": gemini_manager is not None and gemini_manager.is_configured,
        "sentence_model_available": sentence_model is not None
    })

# Add test endpoint for network connectivity
@app.route('/test-connection', methods=['GET', 'POST'])
def test_connection():
    return jsonify({
        "status": "success",
        "message": "Connection test successful",
        "client_ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'Unknown'),
        "timestamp": str(pd.Timestamp.now())
    })

# Add CORS preflight handler for all routes
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Access-Control-Allow-Origin")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

# --- Global Variables for RAG ---
# product_df is loaded if cache is hit or after embedding generation
product_df = pd.DataFrame() 
sentence_model = None # For query embedding
faiss_index = None
product_contexts_for_llm = []


# --- Initialize Gemini Manager ---
gemini_manager = None
try:
    print("Setting up Gemini API...")
    gemini_manager = GeminiManager(dotenv_path=dotenv_path)
    if gemini_manager.setup():
        print("Gemini API and model ready")
    else:
        print("Failed to setup Gemini API")
        gemini_manager = None
except Exception as e:
    print(f"Error setting up Gemini: {e}")
    gemini_manager = None

# --- RAG Setup: Load data from cache or trigger embedding generation ---
def initialize_rag_components():
    global product_df, sentence_model, faiss_index, product_contexts_for_llm
    
    # Define cache directory and file paths
    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
    parent_cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
    
    if os.path.exists(parent_cache_dir):
        cache_dir = parent_cache_dir
        print(f"app.py: Using parent directory cache at {parent_cache_dir}")
    else:
        print(f"app.py: Using local cache at {cache_dir}")
        
    faiss_index_path = os.path.join(cache_dir, "faiss_index.idx")
    contexts_path = os.path.join(cache_dir, "product_contexts.pkl")

    # 1. Initialize Sentence Transformer model
    try:
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("app.py: SentenceTransformer model loaded successfully.")
    except Exception as e:
        print(f"app.py: CRITICAL: Failed to load SentenceTransformer model: {e}")
        sentence_model = None
        # If model fails, RAG cannot work. Exit the initialization.
        return

    # 2. Attempt to load from cache
    if os.path.exists(faiss_index_path) and os.path.exists(contexts_path):
        print(f"app.py: Loading from cache: {cache_dir}...")
        try:
            faiss_index = faiss.read_index(faiss_index_path)
            with open(contexts_path, 'rb') as f:
                product_contexts_for_llm = pickle.load(f)
            print(f"app.py: FAISS index ({faiss_index.ntotal} vectors) and contexts loaded from cache.")
            return # Success
        except Exception as e_cache:
            print(f"app.py: Error loading from cache: {e_cache}. Will try to regenerate.")
            faiss_index = None
            product_contexts_for_llm = []

    # 3. If cache fails or doesn't exist, generate new embeddings
    print("app.py: No valid cache found. Calling embedFunc.py to generate embeddings...")
    try:
        generate_embeddings_and_cache() # This function should create and save the cache files
        print("app.py: embedFunc.py completed. Attempting to load newly generated cache...")
        
        # After generation, try to load them again
        if os.path.exists(faiss_index_path) and os.path.exists(contexts_path):
            faiss_index = faiss.read_index(faiss_index_path)
            with open(contexts_path, 'rb') as f:
                product_contexts_for_llm = pickle.load(f)
            print(f"app.py: Successfully loaded newly generated FAISS index and contexts.")
        else:
            print("app.py: CRITICAL ERROR - Cache files not found after generation. RAG will not work.")
            faiss_index = None
            product_contexts_for_llm = []

    except Exception as e_embed_func:
        print(f"app.py: CRITICAL ERROR during embedding generation or loading: {e_embed_func}")
        faiss_index = None
        product_contexts_for_llm = []


@app.route('/request-agent', methods=['POST'])
def request_agent():
    try:
        # Generate a unique chat session ID
        session_id = str(uuid.uuid4())
        
        # Log the request for debugging
        logger.info(f"Agent request from {request.remote_addr} with session {session_id}")
        
        # Use the email service to send the notification
        success, error_message = email_service.send_agent_notification(session_id, request.host_url)
        
        if not success:
            logger.error(f"Failed to send agent notification: {error_message}")
            return jsonify({"error": f"Error sending notification: {error_message}"}), 500
        
        logger.info(f"Successfully processed agent request for session {session_id}")
        return jsonify({"message": "An agent has been notified. You will be connected shortly.", "session_id": session_id})
        
    except Exception as e:
        logger.error(f"Unexpected error in request_agent: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500


# Add a new endpoint to check room status
@app.route('/room-status/<room_id>')
def room_status(room_id):
    """Check if a room has staff and other status info"""
    try:
        status = chat_service.get_room_status(room_id)
        logger.info(f"Room status request for {room_id}: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting room status for {room_id}: {e}")
        return jsonify({"error": "Failed to get room status"}), 500


# Initialize AI Service
ai_service = None
try:
    from services.ai_service import AIService
    # Import requests for API testing
    import requests
    
    # Test Local AI connection if URL is configured
    local_ai_url = os.getenv('LOCAL_AI_URL')
    if local_ai_url:
        try:
            logger.info(f"Testing connection to Local AI at {local_ai_url}")
            response = requests.get(local_ai_url.replace('/api/generate', '/api/tags'), timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to Local AI service")
            else:
                logger.warning(f"Local AI service returned status code {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Local AI service at {local_ai_url}: {str(e)}")
    
    ai_service = AIService()
    logger.info("AI Service initialized")
except Exception as e:
    logger.error(f"Error initializing AI Service: {e}", exc_info=True)
    ai_service = None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not ai_service:
            return jsonify({
                "reply": "I'm sorry, the AI service is not properly configured. Please contact support.",
                "session_id": str(uuid.uuid4())
            }), 500
            
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_message = data.get('message')
        user_id = data.get('user_id')
        session_id = data.get('session_id', str(uuid.uuid4()))
        model = data.get('model', 'gemini')  # Default to 'gemini' if not specified
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
            
        # Check if the selected model is available
        if model == 'gemini' and (not gemini_manager or not gemini_manager.is_configured):
            return jsonify({
                "reply": "I'm sorry, the Gemini AI service is currently unavailable. Please try again later or switch to Local AI.",
                "session_id": session_id
            })

        # Initialize personalized prompt if user_id is provided
        personalized_prompt = None
        if user_id:
            try:
                from services.personalized_agent.agent_manager import PersonalizedAgentManager
                agent_manager = PersonalizedAgentManager()
                personalized_prompt = agent_manager.generate_personalized_prompt(user_id, user_message)
            except Exception as e:
                print(f"Error getting personalized prompt: {e}")
                # Continue with standard flow
                
        # Generate response using the selected model with RAG support
        try:
            response = ai_service.generate_response(
                message=user_message,
                model=model,
                gemini_manager=gemini_manager if model == 'gemini' else None,
                personalized_prompt=personalized_prompt,
                session_id=session_id
            )
            
            return jsonify({
                "reply": response.get("reply", "I'm sorry, I couldn't generate a response."),
                "session_id": session_id,
                "model": response.get("model", model)
            })
            
        except Exception as e:
            error_msg = f"Error generating AI response: {e}"
            logger.error(error_msg, exc_info=True)
            return jsonify({
                "reply": f"I'm sorry, I encountered an error processing your request: {str(e)}",
                "session_id": session_id,
                "error": str(e)
            }), 500

        # If we reach here, it means there was an issue with the AI service
        # Fallback to a basic response
        fallback_response = "I'm sorry, I'm having technical difficulties right now. Please try again later."
        return jsonify({
            "reply": fallback_response,
            "session_id": session_id
        })

    except Exception as e:
        print(f"Unexpected error in chat endpoint: {e}")
        return jsonify({
            "reply": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            "session_id": session_id if 'session_id' in locals() else str(uuid.uuid4())
        }), 500

# Add basic chatbot route for simple interface
@app.route('/chatbot')
def chatbot():
    try:
        return render_template('beauty_companion.html')
    except Exception as e:
        # Fallback to a simple HTML page if template doesn't exist
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Beauty Companion Chatbot</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .chat-app { 
                    width: 90%;
                    max-width: 800px; 
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                .chat-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .chat-container { 
                    height: 500px; 
                    overflow-y: auto; 
                    padding: 20px; 
                    background: #f8f9fa;
                }
                .message {
                    margin-bottom: 15px;
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 80%;
                    word-wrap: break-word;
                }
                .user-message {
                    background: #007bff;
                    color: white;
                    margin-left: auto;
                    text-align: right;
                }
                .bot-message {
                    background: #e9ecef;
                    color: #333;
                    margin-right: auto;
                }
                .input-container { 
                    display: flex; 
                    padding: 20px;
                    background: white;
                    border-top: 1px solid #eee;
                }
                #userInput { 
                    flex: 1; 
                    padding: 12px 16px; 
                    border: 2px solid #e9ecef;
                    border-radius: 25px;
                    font-size: 16px;
                    outline: none;
                    transition: border-color 0.3s;
                }
                #userInput:focus {
                    border-color: #007bff;
                }
                #sendBtn { 
                    padding: 12px 24px; 
                    margin-left: 10px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background 0.3s;
                }
                #sendBtn:hover {
                    background: #0056b3;
                }
                #sendBtn:disabled {
                    background: #6c757d;
                    cursor: not-allowed;
                }
                .typing-indicator {
                    display: none;
                    padding: 12px 16px;
                    background: #e9ecef;
                    border-radius: 18px;
                    max-width: 80%;
                    margin-bottom: 15px;
                    color: #666;
                }
                .loading-dots {
                    display: inline-block;
                }
                .loading-dots::after {
                    content: '';
                    animation: dots 1.5s infinite;
                }
                @keyframes dots {
                    0%, 20% { content: ''; }
                    40% { content: '.'; }
                    60% { content: '..'; }
                    80%, 100% { content: '...'; }
                }
            </style>
        </head>
        <body>
            <div class="chat-app">
                <div class="chat-header">
                    <h1>🌸 Beauty Companion</h1>
                    <p>Your AI-powered beauty advisor</p>
                </div>
                <div id="chatContainer" class="chat-container"></div>
                <div class="typing-indicator" id="typingIndicator">
                    Bot is typing<span class="loading-dots"></span>
                </div>
                <div class="input-container">
                    <input type="text" id="userInput" placeholder="Ask about skincare, makeup, or beauty tips..." />
                    <button id="sendBtn">Send</button>
                </div>
            </div>
            
            <script>
                const chatContainer = document.getElementById('chatContainer');
                const userInput = document.getElementById('userInput');
                const sendBtn = document.getElementById('sendBtn');
                const typingIndicator = document.getElementById('typingIndicator');
                
                function addMessage(message, isUser) {
                    const div = document.createElement('div');
                    div.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
                    div.textContent = message;
                    chatContainer.appendChild(div);
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                
                function showTyping() {
                    typingIndicator.style.display = 'block';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
                
                function hideTyping() {
                    typingIndicator.style.display = 'none';
                }
                
                function sendMessage() {
                    const message = userInput.value.trim();
                    if (!message) return;
                    
                    addMessage(message, true);
                    userInput.value = '';
                    sendBtn.disabled = true;
                    showTyping();
                    
                    fetch('/chat', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({ message: message })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        hideTyping();
                        addMessage(data.reply || 'Sorry, I encountered an error.', false);
                        sendBtn.disabled = false;
                        userInput.focus();
                    })
                    .catch(error => {
                        hideTyping();
                        console.error('Error:', error);
                        addMessage('Sorry, I could not connect to the server. Please try again.', false);
                        sendBtn.disabled = false;
                        userInput.focus();
                    });
                }
                
                sendBtn.addEventListener('click', sendMessage);
                userInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !sendBtn.disabled) {
                        sendMessage();
                    }
                });
                
                // Initial message
                addMessage('Hello! I\'m your beauty companion. Ask me about skincare routines, makeup tips, product recommendations, or any beauty-related questions!', false);
                
                // Focus on input
                userInput.focus();
            </script>
        </body>
        </html>
        """

# Add route to serve static files from parent directory
@app.route('/chatbot/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    from flask import send_from_directory
    return send_from_directory(static_dir, filename)

def run_pre_flight_tests():
    """Run pre-flight tests to ensure all components work before starting the app"""
    print("Running Pre-Flight System Check...")
    print("=" * 60)
    
    try:
        # Run the comprehensive test suite
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        test_path = os.path.join(parent_dir, "tests", "run_all_tests.py")
        
        if os.path.exists(test_path):
            result = subprocess.run([
                sys.executable, 
                test_path, 
                "test-only"
            ], capture_output=True, text=True)
            
            # Print the test output
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            # Return True if tests passed (exit code 0)
            return result.returncode == 0
        else:
            print("Test suite not found, skipping pre-flight tests...")
            return True
        
    except Exception as e:
        print(f"Error running test suite: {e}")
        print("Continuing without pre-flight tests...")
        return True

# Initialize the RAG components when the app starts
# Moved to the main block for better control

if __name__ == '__main__':
    print("🌸 Sephora Beauty Companion Chatbot 🌸")
    print("=" * 60)
    
    print("Initializing application...")
    
    # Initialize the RAG components when the app starts
    print("Setting up RAG components...")
    try:
        initialize_rag_components()
        print("✅ RAG components initialized successfully")
    except Exception as e:
        print(f"⚠️ Warning: RAG initialization failed: {e}")
        print("App will continue with basic functionality")
    
    print("\n🚀 Starting Flask application...")
    print("Available routes:")
    print("  - http://localhost:5000/ (Home page)")
    print("  - http://localhost:5000/chatbot (Chatbot interface)")
    print("  - http://localhost:5000/enhanced (Enhanced experience)")
    print("  - http://localhost:5000/chat (API endpoint)")
    print("  - http://localhost:5000/health (Health check)")
    print("=" * 60)
    
    try:
        # Start the Flask-SocketIO app with more robust settings
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=False,  # Set to False for stability
                    allow_unsafe_werkzeug=True,
                    use_reloader=False)  # Disable reloader to prevent double initialization
    except Exception as e:
        print(f"❌ Error starting SocketIO application: {e}")
        print("🔄 Trying to start with basic Flask...")
        try:
            app.run(host='127.0.0.1', port=5000, debug=False)
        except Exception as e2:
            print(f"❌ Failed to start application: {e2}")
            print("💡 Try running: pip install flask flask-socketio flask-cors python-dotenv")
            sys.exit(1)
