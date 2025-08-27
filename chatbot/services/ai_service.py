"""
AI Service Module
Handles interactions with different AI models (Gemini, Local AI, etc.)
with RAG (Retrieval-Augmented Generation) support
"""
import os
import requests
import logging
import numpy as np
import faiss
from typing import Optional, Dict, Any, List
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.local_ai_url = os.environ.get('LOCAL_AI_URL')
        self.faiss_index = None
        self.product_contexts = []
        self.sentence_model = None
        self._test_local_ai_connection()
        self._initialize_rag_components()
        
    def _initialize_rag_components(self):
        """Initialize RAG components (FAISS index, sentence model, etc.)"""
        try:
            # Load sentence transformer model
            logger.info("Loading sentence transformer model...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create cache directory if it doesn't exist
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            logger.info(f"Using cache directory: {cache_dir}")
            
            # Load or create FAISS index and product contexts
            self._load_rag_components()
            
            if self.faiss_index is not None and self.product_contexts:
                logger.info(f"RAG components initialized successfully with {len(self.product_contexts)} product contexts")
            else:
                logger.warning("RAG components not fully initialized. Some features may be limited.")
                
        except Exception as e:
            logger.error(f"Error initializing RAG components: {e}", exc_info=True)
            logger.warning("RAG features will be disabled due to initialization error")
    
    def _load_rag_components(self):
        """Load FAISS index and product contexts from cache"""
        # Initialize to empty values
        self.faiss_index = None
        self.product_contexts = []
        
        # Define possible cache locations (in order of priority)
        possible_cache_dirs = [
            # 1. Check in the chatbot/cache directory (current expected location)
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache'),
            # 2. Check in the root cache directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cache'),
        ]
        
        for cache_dir in possible_cache_dirs:
            try:
                faiss_index_path = os.path.join(cache_dir, "faiss_index.idx")
                contexts_path = os.path.join(cache_dir, "product_contexts.pkl")
                
                # Check if both required files exist in this location
                if os.path.exists(faiss_index_path) and os.path.exists(contexts_path):
                    logger.info(f"Found RAG cache files in: {cache_dir}")
                    
                    # Load FAISS index
                    logger.info(f"Loading FAISS index from {faiss_index_path}")
                    self.faiss_index = faiss.read_index(faiss_index_path)
                    logger.info(f"Loaded FAISS index with {self.faiss_index.ntotal} vectors")
                    
                    # Load product contexts
                    logger.info(f"Loading product contexts from {contexts_path}")
                    import pickle
                    with open(contexts_path, 'rb') as f:
                        self.product_contexts = pickle.load(f)
                    logger.info(f"Loaded {len(self.product_contexts)} product contexts")
                    
                    # Validate that the number of contexts matches the FAISS index
                    if self.faiss_index.ntotal != len(self.product_contexts):
                        logger.error(f"Mismatch between FAISS index size ({self.faiss_index.ntotal}) "
                                   f"and number of contexts ({len(self.product_contexts)}). ")
                        self.faiss_index = None
                        self.product_contexts = []
                        continue  # Try next location
                        
                    # If we got here, we successfully loaded both files
                    logger.info(f"Successfully loaded RAG components from {cache_dir}")
                    return
                    
            except Exception as e:
                logger.warning(f"Error loading RAG cache from {cache_dir}: {e}")
                self.faiss_index = None
                self.product_contexts = []
                continue  # Try next location
        
        # If we get here, we couldn't load from any location
        logger.warning("Could not load RAG cache from any known location. RAG features will be disabled.")
        logger.info("To enable RAG, ensure the following files exist in a cache directory:")
        logger.info("  - faiss_index.idx")
        logger.info("  - product_contexts.pkl")
        
        # No need for a separate except block here as we're already in a try-except in _initialize_rag_components
    
    def _search_rag(self, query: str, top_k: int = 3) -> List[str]:
        """Search for relevant documents using RAG"""
        # Check if RAG components are available
        if not all([self.faiss_index, self.product_contexts, self.sentence_model]):
            logger.warning("RAG components not fully initialized - falling back to empty context")
            return []
            
        try:
            logger.debug(f"Performing RAG search for query: {query[:50]}...")
            
            # Encode query
            query_embedding = self.sentence_model.encode([query], show_progress_bar=False).astype('float32')
            
            # Search FAISS index
            distances, indices = self.faiss_index.search(query_embedding, top_k)
            
            # Get relevant contexts
            relevant_contexts = []
            for i, idx in enumerate(indices[0]):
                if 0 <= idx < len(self.product_contexts):
                    distance = distances[0][i]
                    logger.debug(f"Found relevant context at index {idx} with distance {distance:.4f}")
                    relevant_contexts.append(self.product_contexts[idx])
                
            logger.debug(f"Found {len(relevant_contexts)} relevant contexts")
            return relevant_contexts
            
        except Exception as e:
            logger.error(f"Error in RAG search: {e}", exc_info=True)
            return []
        
    def _test_local_ai_connection(self):
        """Test the connection to the Local AI service"""
        if not self.local_ai_url:
            logger.warning("LOCAL_AI_URL is not set in environment variables")
            return False
            
        test_url = self.local_ai_url.replace('/api/generate', '/api/tags')
        try:
            logger.info(f"Testing connection to Local AI at {test_url}")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                logger.info("Successfully connected to Local AI service")
                return True
            else:
                logger.warning(f"Local AI service returned status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Local AI service at {test_url}: {str(e)}")
            return False
        
    def generate_response(self, 
                        message: str, 
                        model: str = 'gemini', 
                        gemini_manager = None,
                        personalized_prompt: Optional[str] = None,
                        **kwargs) -> Dict[str, Any]:
        """
        Generate a response using the specified model with RAG support
        
        Args:
            message: The user's message
            model: The model to use ('gemini' or 'local-ai')
            gemini_manager: GeminiManager instance (required for 'gemini' model)
            personalized_prompt: Optional personalized prompt to include in the context
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict containing the response and metadata
        """
        # Check for simple greetings
        greetings = [
            'hi', 'hello', 'hey', 'hi there', 'hello there', 'hey there',
            'good morning', 'good afternoon', 'good evening', 'greetings',
            'hi!', 'hello!', 'hey!', 'hi there!', 'hello there!', 'hey there!'
        ]
        
        # Clean the message for comparison
        clean_message = message.lower().strip(" .,!?")
        
        # If it's just a greeting, return a friendly response
        if clean_message in greetings:
            return {
                "reply": "Hello! I'm your Sephora beauty assistant. How can I help you with your beauty and skincare needs today?",
                "model": model
            }
            
        # Get relevant context using RAG
        relevant_contexts = self._search_rag(message)
        
        # Prepare context for the prompt
        rag_context = ""
        if relevant_contexts:
            rag_context = "\n\nHere is some product information that might be relevant:\n\n"
            for i, context in enumerate(relevant_contexts, 1):
                rag_context += f"--- Context {i} ---\n{context}\n\n"
        
        # Add personalized prompt if provided
        if personalized_prompt:
            context = personalized_prompt
        else:
            context = (
                "You are a helpful and knowledgeable shopping assistant for Sephora, a skincare and cosmetics brand. "
                "Answer the user's question based on the provided context and your knowledge. "
                "Be friendly, helpful, and knowledgeable about beauty and skincare. "
                "If the provided context isn't sufficient, use your general knowledge to answer."
            )
        
        # Add RAG context to the prompt
        context += rag_context
        
        # Generate response based on the selected model
        if model.lower() == 'gemini':
            if not gemini_manager:
                raise ValueError("Gemini manager is required for 'gemini' model")
            return self._generate_gemini_response(
                message=message, 
                gemini_manager=gemini_manager, 
                context=context,
                **kwargs
            )
        elif model.lower() in ['local', 'local-ai', 'local_ai']:
            return self._generate_local_ai_response(
                message=message,
                context=context,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _generate_gemini_response(self, 
                                message: str, 
                                gemini_manager,
                                context: str,
                                personalized_prompt: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """Generate response using Gemini model"""
        if not gemini_manager or not hasattr(gemini_manager, 'generate_content'):
            raise ValueError("Gemini manager is not properly configured")
            
        try:
            # Use personalized prompt if available, otherwise use default
            if personalized_prompt:
                prompt = personalized_prompt
            else:
                prompt = (
                    "You are a helpful and knowledgeable shopping assistant for Sephora, a skincare and cosmetics brand. "
                    "Answer the user's question based on your knowledge. "
                    "Be friendly, helpful, and knowledgeable about beauty and skincare."
                    f"\n\nUser: {message}\n\nAssistant:"
                )
            
            response = gemini_manager.generate_content(prompt)
            return {
                "reply": response,
                "model": "gemini"
            }
            
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return {
                "reply": "I'm sorry, I encountered an error processing your request with Gemini.",
                "error": str(e),
                "model": "gemini"
            }
    
    def _generate_local_ai_response(self, 
                                  message: str, 
                                  context: str = "",
                                  **kwargs) -> Dict[str, Any]:
        """
        Generate response using local AI model with RAG support
        
        Args:
            message: User's message
            context: Additional context for the model (e.g., from RAG)
            **kwargs: Additional parameters for the model
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.local_ai_url:
            error_msg = "Local AI URL is not configured. Please set LOCAL_AI_URL environment variable."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Construct the full prompt with context - requesting concise responses
            full_prompt = f"""{context}
            
            User question: {message}
            
            Please provide a concise and helpful response (2-3 sentences maximum) based on the context above.
            Be direct and to the point while still being helpful.
            If the context doesn't contain the answer, use your general knowledge to help.
            
            Assistant (be brief):"""
            
            # Prepare the payload according to the Local AI API format
            payload = {
                "model": "openhermes-gpu:latest",  # Using the GPU boosted model from the API
                "prompt": full_prompt.strip(),
                "stream": False,
                "options": {
                    "temperature": 0.5,  # Slightly lower temperature for more focused responses
                    "top_p": 0.8,        # Slightly lower for less randomness
                    "top_k": 30,         # Reduced top_k for more focused responses
                    "repeat_penalty": 1.2, # Increased to reduce repetition
                    "num_predict": 200,   # Reduced max tokens for shorter responses
                    "stop": ["\nUser:", "\n### User:", "</s>"]
                },
                **kwargs
            }
            
            logger.debug(f"Sending request to Local AI: {payload}")
            
            response = requests.post(
                self.local_ai_url,
                headers=headers,
                json=payload,
                timeout=30  # 30 seconds timeout
            )
            
            logger.debug(f"Local AI response status: {response.status_code}")
            logger.debug(f"Local AI response: {response.text[:500]}...")  # Log first 500 chars
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the response text based on the Local AI API format
            reply = response_data.get("response", "")
            
            if not reply and isinstance(response_data.get("message"), str):
                reply = response_data.get("message")
                
            if not reply:
                logger.warning(f"Unexpected Local AI response format: {response_data}")
                reply = "I'm sorry, I couldn't process the Local AI response."
            
            return {
                "reply": reply.strip(),
                "model": "local-ai",
                "raw_response": response_data
            }
            
        except requests.exceptions.Timeout:
            error_msg = "Local AI service request timed out. The service might be busy or unavailable."
            logger.error(error_msg)
            return {
                "reply": "I'm sorry, the Local AI service is taking too long to respond. Please try again later.",
                "error": "Request timeout",
                "model": "local-ai"
            }
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from Local AI service: {str(e)}"
            logger.error(f"{error_msg}. Status code: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
            return {
                "reply": "I'm sorry, there was an error processing your request with the Local AI service.",
                "error": error_msg,
                "model": "local-ai"
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Local AI service: {str(e)}"
            logger.error(error_msg)
            return {
                "reply": "I'm sorry, I couldn't connect to the Local AI service. Please check if the service is running.",
                "error": error_msg,
                "model": "local-ai"
            }
        except Exception as e:
            error_msg = f"Unexpected error with Local AI service: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "reply": "I'm sorry, I encountered an unexpected error while processing your request with the Local AI.",
                "error": error_msg,
                "model": "local-ai"
            }
