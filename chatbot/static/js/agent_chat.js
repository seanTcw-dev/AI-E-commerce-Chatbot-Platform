// agent_chat.js - The ONE and ONLY script for the agent chat page.

document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Get Elements and Initial Data ---
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('message_input');
    const sendButton = document.getElementById('send_button');
    const endChatButton = document.getElementById('end_chat_button');
    const header = document.querySelector('.chat-header h1');

    // Get session ID from the meta tag in the HTML
    const sessionId = document.querySelector('meta[name="chat-session-id"]').getAttribute('content');
    
    if (!sessionId) {
        addSystemMessage("CRITICAL ERROR: Session ID not found. Cannot start chat.", 'error');
        return;
    }

    // --- 2. Prompt for Agent Name and Initialize ---
    const agentName = prompt("Please enter your name to begin:") || "Agent";
    if (header) {
        header.textContent = `Live Chat - Agent: ${agentName}`;
    }

    // --- 3. Connect to Socket.IO ---
    const socket = io(); // Connect to the server

    // --- 4. Define Event Handlers ---
    socket.on('connect', () => {
        console.log('Agent connected with Socket.IO.');
        addSystemMessage('Connecting to chat room...', 'info');
        // Agent joins the room
        socket.emit('join', { 
            room: sessionId, 
            username: agentName,
            user_type: 'staff' // Let the server know this is a staff member
        });
    });

    socket.on('user_joined_notification', (data) => {
        addSystemMessage(`${data.username} has joined the chat.`, 'info');
    });

    socket.on('user_left_notification', (data) => {
        addSystemMessage(`${data.username} has left the chat.`, 'info');
    });

    socket.on('message', (data) => {
        // Agent receives messages from both customer and themselves (for confirmation)
        // We will let the server decide what to send.
        addChatMessage(data);
    });
    
    socket.on('chat_ended_notification', () => {
        addSystemMessage('This chat session has been ended.', 'info');
        disableChat();
    });

    socket.on('disconnect', () => {
        addSystemMessage('You have been disconnected from the server.', 'error');
        disableChat();
    });

    // --- 5. Define Functions ---
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {
            const messageData = {
                room: sessionId,
                msg: message,
                sender: agentName, // Use 'sender' consistently
                user_type: 'staff'
            };
            socket.emit('message', messageData);
            addChatMessage(messageData); // Add to own UI immediately
            messageInput.value = '';
        }
    }

    function endChat() {
        if (confirm("Are you sure you want to end this chat?")) {
            socket.emit('end_chat', { room: sessionId, ender_name: agentName });
        }
    }

    function addChatMessage(data) {
        const msgDiv = document.createElement('div');
        const isAgent = data.user_type === 'staff';
        
        msgDiv.className = isAgent ? 'message-right' : 'message-left';
        msgDiv.innerHTML = `<strong>${data.sender}:</strong> ${data.msg}`;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addSystemMessage(text, type = 'info') {
        const msgDiv = document.createElement('div');
        msgDiv.className = `system-message ${type}`;
        msgDiv.textContent = `[System] ${text}`;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function disableChat() {
        messageInput.disabled = true;
        sendButton.disabled = true;
        endChatButton.disabled = true;
    }

    // --- 6. Attach Event Listeners ---
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    endChatButton.addEventListener('click', endChat);
});
