// Function to update chat header based on selected model
function updateHeaderColor(model) {
    const header = document.querySelector('.chatbot-header');
    if (!header) return;
    
    // Remove all color classes
    header.classList.remove('model-gemini', 'model-local');
    
    // Add appropriate class based on model
    if (model === 'gemini') {
        header.classList.add('model-gemini');
    } else if (model === 'local') {
        header.classList.add('model-local');
    }
    
    // Save to localStorage for persistence
    localStorage.setItem('selectedModel', model);
}

document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Elements ---
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.getElementById('chatbotContainer');
    const chatbotMinimize = document.querySelector('.chatbot-minimize');
    const chatbotMessages = document.getElementById('chatbotMessages');
    const chatbotInput = document.getElementById('chatbotInput');
    const sendButton = document.querySelector('.chatbot-send');
    const talkToAgentButton = document.querySelector('.talk-to-agent');
    const quickActionButtons = document.querySelectorAll('.quick-btn');
    
    // Initialize model selector
    const modelSelect = document.getElementById('modelSelect');
    if (modelSelect) {
        // Load saved model preference or default to 'gemini'
        const savedModel = localStorage.getItem('selectedModel') || 'gemini';
        modelSelect.value = savedModel;
        updateHeaderColor(savedModel);
        
        // Add change event listener
        modelSelect.addEventListener('change', function() {
            updateHeaderColor(this.value);
        });
    }

    // --- Live Agent Chat Variables ---
    let socket = null;
    let liveChatSessionId = null;
    let isLiveChatActive = false;

    // --- UI Interaction ---
    function toggleChatbot() {
        chatbotContainer.classList.toggle('active');
        chatbotToggle.classList.toggle('active');
    }

    chatbotToggle.addEventListener('click', toggleChatbot);
    chatbotMinimize.addEventListener('click', toggleChatbot);

    quickActionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const message = button.getAttribute('data-message');
            chatbotInput.value = message;
            sendMessage();
        });
    });

    // --- Core Chat Functionality ---
    // Get the current host and port for dynamic API calls
    const currentHost = window.location.hostname;
    const currentPort = window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
    const baseUrl = `${window.location.protocol}//${currentHost}:${currentPort}`;
    
    async function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message === '') return;

        const modelSelect = document.getElementById('modelSelect');
        const selectedModel = modelSelect ? modelSelect.value : 'gemini';

        addMessage(message, 'user');
        chatbotInput.value = '';

        if (isLiveChatActive && socket) {
            socket.emit('message', { 
                room: liveChatSessionId, 
                msg: message, 
                sender: 'Customer', 
                user_type: 'customer',
                model: selectedModel
            });
            return;
        }

        showTypingIndicator();
        try {
            const response = await fetch(`${baseUrl}/chat`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify({ 
                    message: message,
                    model: selectedModel
                })
            });
            const data = await response.json();
            removeTypingIndicator();
            if (data.reply) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage('Sorry, I encountered an error.', 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            removeTypingIndicator();
            addMessage('Sorry, I could not connect to the server.', 'bot');
        }
    }

    sendButton.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', e => e.key === 'Enter' && sendMessage());

    // --- Live Agent and Session Management ---
    talkToAgentButton.addEventListener('click', async function() {
        if (isLiveChatActive) {
            endChat();
            return;
        }

        showTypingIndicator();
        try {
            const response = await fetch(`${baseUrl}/request-agent`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'Accept': 'application/json'
                },
                mode: 'cors'
            });

            removeTypingIndicator();
            if (!response.ok) throw new Error(`Status ${response.status}`);
            
            const data = await response.json();
            isLiveChatActive = true;
            liveChatSessionId = data.session_id;

            talkToAgentButton.textContent = "End Live Chat";
            talkToAgentButton.style.backgroundColor = "#e74c3c";

            addMessage(data.message, 'bot');
            connectToSocket();
        } catch (error) {
            console.error('Talk to Agent error:', error);
            removeTypingIndicator();
            addMessage(`Failed to connect to an agent. Please try again later. Error: ${error.message}`, 'bot');
        }
    });

    function connectToSocket() {
        if (typeof io === 'undefined') {
            addMessage("Error: Live chat service is unavailable.", 'bot');
            return;
        }
        socket = io(baseUrl);
        setupSocketHandlers();
    }

    function setupSocketHandlers() {
        socket.on('connect', () => {
            socket.emit('join', { 
                room: liveChatSessionId, 
                user_type: 'customer', 
                user_name: 'Customer' 
            });
        });

        socket.on('message', (data) => {
            console.log('Received message:', data); // Debug log
            
            // Determine if this message is from an agent or customer
            const isFromAgent = data.user_type === 'staff' || data.user_type === 'agent';
            const isFromCurrentUser = data.user_type === 'customer' && data.sender === 'Customer';
            
            // Don't display messages sent by the current user (they're already shown)
            if (!isFromCurrentUser) {
                const senderDisplay = isFromAgent ? `Agent (${data.sender})` : `Customer (${data.sender})`;
                const messageText = data.message || data.msg;
                
                // Add timestamp if available
                let finalMessage = messageText;
                if (data.timestamp) {
                    finalMessage = `[${data.timestamp}] ${messageText}`;
                }
                
                addMessage(finalMessage, isFromAgent ? 'agent' : 'customer', senderDisplay);
            }
        });

        socket.on('chat_ended', (data) => {
            addMessage(`Chat ended by ${data.ender_name}.`, 'bot');
            refreshChatbot();
        });

        socket.on('disconnect', () => {
            if (isLiveChatActive) {
                addMessage("Live chat connection lost. Please reconnect.", 'bot');
                refreshChatbot();
            }
        });
    }

    function endChat() {
        if (socket && liveChatSessionId) {
            socket.emit('end_chat', { room: liveChatSessionId, ender_name: 'Customer', user_type: 'customer' });
            addMessage("You have ended the chat.", 'bot');
            refreshChatbot();
        }
    }

    function refreshChatbot() {
        if (socket) {
            socket.disconnect();
            socket = null;
        }
        isLiveChatActive = false;
        liveChatSessionId = null;
        talkToAgentButton.textContent = "Talk to Agent";
        talkToAgentButton.style.backgroundColor = "";
    }

    // --- Helper Functions ---
    function addMessage(text, sender, senderDisplay = null) {
        const messageDiv = document.createElement('div');
        
        // Set classes based on sender type
        if (sender === 'user') {
            messageDiv.className = 'chatbot-message user-message';
        } else if (sender === 'agent') {
            messageDiv.className = 'chatbot-message agent-message';
        } else {
            messageDiv.className = 'chatbot-message'; // Default bot message
        }

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        // Set different icons and colors for different user types
        if (sender === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
            avatar.style.backgroundColor = '#007bff';
        } else if (sender === 'agent') {
            avatar.innerHTML = '<i class="fas fa-headset"></i>';
            avatar.style.backgroundColor = '#28a745';
        } else {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
            avatar.style.backgroundColor = '#6c757d';
        }

        const content = document.createElement('div');
        content.className = 'message-content';
        
        // Add sender label if provided
        if (senderDisplay) {
            const senderLabel = document.createElement('div');
            senderLabel.className = 'message-sender';
            senderLabel.style.fontSize = '0.8em';
            senderLabel.style.fontWeight = 'bold';
            senderLabel.style.marginBottom = '4px';
            senderLabel.style.color = sender === 'agent' ? '#28a745' : '#007bff';
            senderLabel.textContent = senderDisplay;
            content.appendChild(senderLabel);
        }
        
        const messageText = document.createElement('div');
        messageText.textContent = text;
        content.appendChild(messageText);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
                <div class="typing-text">AI is typing...</div>
            </div>`;
        chatbotMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) typingIndicator.remove();
    }

    function scrollToBottom() {
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // --- Initial Welcome Message ---
    addMessage("Welcome to our Beauty Assistant! How can I help you today?", 'bot');
});