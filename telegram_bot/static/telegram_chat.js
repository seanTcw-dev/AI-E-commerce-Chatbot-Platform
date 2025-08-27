document.addEventListener("DOMContentLoaded", function() {
    const messagesDiv = document.getElementById('messages');
    const messageInput = document.getElementById('message_input');
    const sendButton = document.getElementById('send_button');
    const endChatButton = document.getElementById('end-chat-btn');

    // The session_id is passed from the Flask template
    const sessionId = document.body.dataset.sessionId;
    let agentName = 'Agent'; // Default name
    let isChatActive = true;

    // --- Socket.IO Connection ---
    const socket = io();

    socket.on('connect', () => {
        console.log('Successfully connected to WebSocket server.');
        agentName = prompt("Please enter your name:") || "Agent";
        document.querySelector('.chat-header h2').textContent = `Live Chat - Agent: ${agentName}`;
        
        socket.emit('join', { 
            room: sessionId,
            sender: agentName
        });
        
        // Focus the input field when connected
        messageInput.focus();
    });

    socket.on('disconnect', () => {
        displaySystemMessage('You have been disconnected. Please refresh the page to reconnect.');
        disableChatInput();
    });

    // Handle messages from users (from Telegram)
    socket.on('message_from_user', (data) => {
        console.log('Received message from user:', data);
        displayMessage(data.sender || 'User', data.message, 'user');
    });

    // Handle regular messages (for backward compatibility)
    socket.on('message', (data) => {
        console.log('Received message:', data);
        displayMessage(data.sender || 'System', data.msg || data.message, 'system');
    });

    // Handle status updates
    socket.on('status', (data) => {
        console.log('Status update:', data);
        displaySystemMessage(data.msg || data.message);
    });

    socket.on('chat_ended', (data) => {
        displaySystemMessage(data.message || 'The chat has been ended.');
        endChat();
    });

    // --- UI Functions ---
    function sendMessage() {
        if (!isChatActive) return;
        
        const message = messageInput.value.trim();
        if (message && socket.connected) {
            const data = { 
                session_id: sessionId,
                message: message,
                sender: agentName || 'Agent'
            };
            
            // Emit to the server to relay to the Telegram user
            socket.emit('agent_to_user', data);
            
            // Display the agent's own message in the chat
            displayMessage(agentName || 'You', message, 'agent');
            messageInput.value = '';
            
            console.log('Message sent to server:', data);
        }
    }

    function endChat() {
        if (!isChatActive) return;
        
        isChatActive = false;
        socket.emit('agent_ends_chat', { session_id: sessionId });
        disableChatInput();
        
        // Change end chat button appearance
        endChatButton.innerHTML = '<i class="fas fa-times-circle"></i> Chat Ended';
        endChatButton.classList.add('chat-ended');
        endChatButton.disabled = true;
    }
    
    function disableChatInput() {
        messageInput.disabled = true;
        sendButton.disabled = true;
        endChatButton.disabled = true;
    }
    
    function displaySystemMessage(message) {
        displayMessage('System', message, 'system');
    }

    function formatTimestamp(date = new Date()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function displayMessage(sender, message, type) {
        // Create message container
        const messageContainer = document.createElement('div');
        messageContainer.style.display = 'flex';
        messageContainer.style.flexDirection = 'column';
        
        // Align container based on message type
        if (type === 'user') {
            messageContainer.style.alignItems = 'flex-start';
            messageContainer.style.marginRight = 'auto';
            messageContainer.style.maxWidth = '80%';
        } else if (type === 'agent') {
            messageContainer.style.alignItems = 'flex-end';
            messageContainer.style.marginLeft = 'auto';
            messageContainer.style.maxWidth = '80%';
        } else {
            // System message
            messageContainer.style.alignItems = 'center';
            messageContainer.style.width = '100%';
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        
        // Clear any conflicting styles
        messageElement.style.marginLeft = '0';
        messageElement.style.marginRight = '0';
        messageElement.style.float = 'none';
        messageElement.style.display = 'block';

        // Create sender element
        const senderElement = document.createElement('div');
        senderElement.classList.add('sender');
        
        // Add user icon based on message type
        let icon = '👤'; // Default icon
        if (type === 'agent') icon = '👨‍💼';
        if (type === 'system') icon = 'ℹ️';
        
        senderElement.innerHTML = `${icon} <span>${sender}</span>`;

        // Create message content
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = message;

        // Add timestamp
        const timestamp = document.createElement('span');
        timestamp.classList.add('timestamp');
        timestamp.textContent = formatTimestamp();

        // Add status indicator for agent messages
        if (type === 'agent') {
            const status = document.createElement('span');
            status.classList.add('status');
            status.textContent = '✓✓';
            messageContent.appendChild(status);
        }

        // Assemble the message
        messageElement.appendChild(senderElement);
        messageElement.appendChild(messageContent);
        messageElement.appendChild(timestamp);
        
        // Add message to container
        messageContainer.appendChild(messageElement);
        
        // Add container to messages div
        messagesDiv.appendChild(messageContainer);
        
        // Smooth scroll to the latest message
        messagesDiv.scrollTo({
            top: messagesDiv.scrollHeight,
            behavior: 'smooth'
        });
    }

    // --- Event Listeners ---
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    endChatButton.addEventListener('click', () => {
        if (confirm('Are you sure you want to end this chat? This cannot be undone.')) {
            endChat();
        }
    });

    // Handle disconnect on window close
    window.addEventListener('beforeunload', function() {
        if (socket.connected && isChatActive) {
            socket.emit('agent_ends_chat', { session_id: sessionId });
            socket.emit('leave', { room: sessionId, sender: agentName });
        }
    });
});
