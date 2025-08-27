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
    async function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message === '') return;

        addMessage(message, 'user');
        chatbotInput.value = '';

        if (isLiveChatActive && socket) {
            socket.emit('message', { room: liveChatSessionId, msg: message, sender: 'Customer', user_type: 'customer' });
            return;
        }

        showTypingIndicator();
        try {
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            removeTypingIndicator();
            if (data.reply) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage('Sorry, I encountered an error.', 'bot');
            }
        } catch (error) {
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
            const response = await fetch('http://127.0.0.1:5000/request-agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
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
            removeTypingIndicator();
            addMessage(`Failed to connect to an agent. Please try again later.`, 'bot');
        }
    });

    function connectToSocket() {
        if (typeof io === 'undefined') {
            addMessage("Error: Live chat service is unavailable.", 'bot');
            return;
        }
        socket = io("http://127.0.0.1:5000");
        setupSocketHandlers();
    }

    function setupSocketHandlers() {
        socket.on('connect', () => {
            socket.emit('join', { room: liveChatSessionId, user_type: 'customer', user_name: 'Customer' });
        });

        socket.on('message', (data) => {
            if (data.user_type !== 'customer') {
                addMessage(data.msg, 'bot');
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
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender === 'user' ? 'user-message' : ''}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = `<i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>`;

        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatbotMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message typing-indicator';
        typingDiv.innerHTML = `<div class="message-avatar"><i class="fas fa-robot"></i></div><div class="message-content"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
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

