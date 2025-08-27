// Global script for shared chat functionalities

/**
 * Ends the chat session and notifies all parties.
 * @param {object} socket - The active Socket.IO socket instance.
 * @param {string} sessionId - The ID of the chat room.
 * @param {string} userName - The name of the user ending the chat (e.g., 'AgentName' or 'Customer').
 * @param {string} userType - The type of user ('staff' or 'customer').
 */
function endChatSession(socket, sessionId, userName, userType) {
    if (confirm('Are you sure you want to end this chat session?')) {
        console.log(`${userName} is ending the chat.`);

        // 1. Send a 'chat_ended' event to the server
        socket.emit('end_chat', {
            room: sessionId,
            user_name: userName
        });

        // 2. Disable the local chat interface immediately
        disableChatInterface(userName);
    }
}

/**
 * Disables the chat input fields and buttons.
 * @param {string} [enderName] - The name of the person who ended the chat.
 */
function disableChatInterface(enderName) {
    const messageInput = document.getElementById('message_input');
    const sendButton = document.getElementById('send_button');
    const endChatButton = document.getElementById('end_chat_button');

    if (messageInput) messageInput.disabled = true;
    if (sendButton) sendButton.disabled = true;
    
    if (endChatButton) {
        endChatButton.disabled = true;
        endChatButton.textContent = 'Chat Ended';
    }

    // Display a final message in the chat window
    const messagesDiv = document.getElementById('messages');
    const endMessage = document.createElement('div');
    endMessage.style.color = 'red';
    endMessage.style.fontWeight = 'bold';
    endMessage.style.textAlign = 'center';
    endMessage.style.padding = '1rem';

    if (enderName) {
        endMessage.textContent = `Chat ended by ${enderName}. You may now close this window.`;
    } else {
        endMessage.textContent = 'The chat session has ended. You may now close this window.';
    }
    
    messagesDiv.appendChild(endMessage);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Update the header
    const header = document.querySelector('.chat-header h1');
    if (header) {
        header.textContent = 'Chat Session Ended';
    }
}
