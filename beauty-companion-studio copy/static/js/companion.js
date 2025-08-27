// Beauty Companion Studio JavaScript
// Enhanced with ChatGPT-style auto-save memory system

let activeCompanion = null;
let chatHistory = [];
let savedMemories = [];
let currentMemoryId = null;
let sidebarCollapsed = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for color presets
    const colorPresets = document.querySelectorAll('.color-preset');
    colorPresets.forEach(preset => {
        preset.addEventListener('click', function() {
            const color = this.getAttribute('data-color');
            document.getElementById('backgroundColor').value = color;
        });
    });

    // Add enter key listener for chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Load any existing memories from localStorage
    loadSavedMemories();
});

// Companion selection functions
function selectCompanion(companionId) {
    activeCompanion = companionData[companionId];
    if (!activeCompanion) {
        console.error('Companion not found:', companionId);
        return;
    }

    // Hide selection screen and show chat interface
    document.getElementById('companionSelection').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'flex';

    // Update active companion display
    updateActiveCompanionDisplay();

    // Apply background color
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.style.setProperty('--bg-color', activeCompanion.backgroundColor);
    chatMessages.style.background = activeCompanion.backgroundColor;

    // Start new chat with greeting
    startNewChat();
    
    // Update memory sidebar after companion selection
    updateMemorySidebar();
}

function showCustomization() {
    document.getElementById('companionSelection').style.display = 'none';
    document.getElementById('customizationPanel').style.display = 'block';
}

function cancelCustomization() {
    document.getElementById('customizationPanel').style.display = 'none';
    document.getElementById('companionSelection').style.display = 'block';
}

function createCustomCompanion() {
    const name = document.getElementById('companionName').value.trim();
    const personalityType = document.getElementById('personalityType').value;
    const greeting = document.getElementById('greetingMessage').value.trim();
    const backgroundColor = document.getElementById('backgroundColor').value;

    if (!name) {
        alert('Please enter a name for your companion.');
        return;
    }

    // Create custom companion data
    const customCompanion = {
        name: name,
        type: "Custom Assistant",
        personality: personalityType,
        avatar: "fas fa-user",
        backgroundColor: backgroundColor,
        greeting: greeting || `Hello! I'm ${name}, your personalized beauty companion. How can I help you today?`,
        systemPrompt: `You are ${name}, a ${personalityType} beauty assistant. Adapt your personality to be ${personalityType} while providing helpful beauty advice.`
    };

    activeCompanion = customCompanion;

    // Hide customization and show chat
    document.getElementById('customizationPanel').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'block';

    updateActiveCompanionDisplay();

    // Apply background color
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.style.setProperty('--bg-color', activeCompanion.backgroundColor);
    chatMessages.style.background = activeCompanion.backgroundColor;

    startNewChat();
    
    // Update memory sidebar
    updateMemorySidebar();
}

function updateActiveCompanionDisplay() {
    document.getElementById('activeCompanionName').textContent = activeCompanion.name;
    document.getElementById('activeCompanionType').textContent = activeCompanion.type;
    
    const avatar = document.getElementById('activeCompanionAvatar');
    avatar.innerHTML = `<i class="${activeCompanion.avatar}"></i>`;
}

// Chat functions
function startNewChat() {
    chatHistory = [];
    currentMemoryId = null;
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';

    // Add greeting message
    addMessage(activeCompanion.greeting, 'companion');
    
    // Update memory sidebar
    updateMemorySidebar();
}

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Simulate API call to your Flask chatbot
    setTimeout(() => {
        getBotResponse(message);
    }, 1000);
}

function addMessage(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatarClass = sender === 'user' ? 'fas fa-user' : activeCompanion.avatar;
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarClass}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${content}</div>
            <div class="message-time">${timestamp}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Add to chat history
    chatHistory.push({
        content: content,
        sender: sender,
        timestamp: new Date().toISOString()
    });
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message companion typing-indicator';
    typingDiv.id = 'typingIndicator';

    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${activeCompanion.avatar}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">
                <i class="fas fa-circle"></i>
                <i class="fas fa-circle"></i>
                <i class="fas fa-circle"></i>
                Typing...
            </div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function getBotResponse(userMessage) {
    try {
        // Create personalized prompt
        const personalizedPrompt = `${activeCompanion.systemPrompt}\n\nUser: ${userMessage}\nAssistant:`;

        // Call your Flask chatbot API
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: personalizedPrompt,
                companion_id: activeCompanion.name.toLowerCase(),
                user_id: 'beauty_studio_user'
            })
        });

        const data = await response.json();
        removeTypingIndicator();

        if (data.reply) {
            addMessage(data.reply, 'companion');
        } else {
            addMessage("I'm sorry, I'm having trouble responding right now. Please try again!", 'companion');
        }
    } catch (error) {
        console.error('Error getting bot response:', error);
        removeTypingIndicator();
        addMessage("I'm having connection issues. Please check if the chatbot server is running!", 'companion');
    }
}

// Navigation functions
function backToSelection() {
    // Auto-save current conversation before leaving
    if (chatHistory.length > 1) { // More than just greeting
        autoSaveCurrentChat();
    }
    
    document.getElementById('chatInterface').style.display = 'none';
    document.getElementById('companionSelection').style.display = 'block';
    activeCompanion = null;
    chatHistory = [];
    currentMemoryId = null;
}

// Auto-save and start new chat
function autoSaveAndNewChat() {
    if (chatHistory.length > 1) { // More than just greeting
        autoSaveCurrentChat();
    }
    startNewChat();
}

// Auto-save memory management functions
function autoSaveCurrentChat() {
    if (chatHistory.length <= 1) return; // Don't save if only greeting

    const memoryId = currentMemoryId || generateMemoryId();
    const memoryTitle = generateMemoryTitle();
    
    const memory = {
        id: memoryId,
        title: memoryTitle,
        companionName: activeCompanion.name,
        companionType: activeCompanion.type,
        companionAvatar: activeCompanion.avatar,
        backgroundColor: activeCompanion.backgroundColor,
        chatHistory: [...chatHistory],
        timestamp: new Date().toISOString(),
        lastUpdated: new Date().toISOString()
    };

    // Save to localStorage and virtual folder (no download)
    saveMemoryToStorage(memory);
    saveMemoryToVirtualFolder(memory);
    
    // Update current memory ID for continued conversation
    currentMemoryId = memoryId;
    
    // Update sidebar
    updateMemorySidebar();
}

function generateMemoryId() {
    return 'memory_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateMemoryTitle() {
    // Try to create a meaningful title from the first user message
    const firstUserMessage = chatHistory.find(msg => msg.sender === 'user');
    if (firstUserMessage) {
        let title = firstUserMessage.content;
        // Truncate and clean up the title
        if (title.length > 50) {
            title = title.substring(0, 47) + '...';
        }
        return title;
    }
    
    // Fallback to timestamp-based title
    const date = new Date();
    const timeStr = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    return `Chat ${timeStr}`;
}

function saveMemoryToStorage(memory) {
    savedMemories = savedMemories.filter(m => m.id !== memory.id); // Remove existing
    savedMemories.unshift(memory); // Add to beginning
    
    // Keep only last 50 memories to avoid storage issues
    if (savedMemories.length > 50) {
        savedMemories = savedMemories.slice(0, 50);
    }
    
    localStorage.setItem('beautyCompanionMemories', JSON.stringify(savedMemories));
}

function loadSavedMemories() {
    try {
        const stored = localStorage.getItem('beautyCompanionMemories');
        if (stored) {
            savedMemories = JSON.parse(stored);
        } else {
            savedMemories = [];
        }
    } catch (e) {
        console.error('Error loading memories:', e);
        savedMemories = [];
        // Clear corrupted data
        localStorage.removeItem('beautyCompanionMemories');
    }
}

function updateMemorySidebar() {
    const memoryList = document.getElementById('memoryList');
    const memoryCount = document.getElementById('memoryCount');
    
    // Update memory count
    if (memoryCount) {
        memoryCount.textContent = `(${savedMemories.length})`;
    }
    
    if (savedMemories.length === 0) {
        memoryList.innerHTML = '<p class="no-memories">No previous conversations yet</p>';
        return;
    }
    
    let memoriesHtml = '';
    savedMemories.forEach(memory => {
        const date = new Date(memory.timestamp);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const isActive = currentMemoryId === memory.id ? 'active' : '';
        
        memoriesHtml += `
            <div class="memory-item ${isActive}" onclick="loadMemoryFromId('${memory.id}')">
                <div class="memory-header">
                    <div class="memory-companion">
                        <i class="${memory.companionAvatar}"></i>
                        <span>${memory.companionName}</span>
                    </div>
                    <div class="memory-actions">
                        <button class="view-memory" onclick="event.stopPropagation(); viewMemoryFile('${memory.id}')" title="View memory file">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="download-memory" onclick="event.stopPropagation(); downloadMemoryFile('${memory.id}')" title="Download memory file">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="delete-memory" onclick="event.stopPropagation(); deleteMemory('${memory.id}')" title="Delete conversation">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="memory-title">${memory.title}</div>
                <div class="memory-date">${dateStr} ${timeStr}</div>
            </div>
        `;
    });
    
    memoryList.innerHTML = memoriesHtml;
}

function loadMemoryFromId(memoryId) {
    const memory = savedMemories.find(m => m.id === memoryId);
    if (!memory) return;
    
    // Set active companion
    activeCompanion = {
        name: memory.companionName,
        type: memory.companionType,
        avatar: memory.companionAvatar,
        backgroundColor: memory.backgroundColor,
        greeting: chatHistory.length > 0 ? chatHistory[0].content : "Hello! How can I help you today?",
        systemPrompt: `You are ${memory.companionName}, a beauty assistant.`
    };
    
    // Update companion display
    updateActiveCompanionDisplay();
    
    // Apply background color
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.style.setProperty('--bg-color', activeCompanion.backgroundColor);
    chatMessages.style.background = activeCompanion.backgroundColor;
    
    // Load chat history
    chatHistory = [...memory.chatHistory];
    currentMemoryId = memoryId;
    
    // Display messages
    chatMessages.innerHTML = '';
    chatHistory.forEach(msg => {
        displayMessage(msg.content, msg.sender, msg.timestamp);
    });
    
    // Update sidebar to show active memory
    updateMemorySidebar();
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displayMessage(content, sender, timestamp) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatarClass = sender === 'user' ? 'fas fa-user' : activeCompanion.avatar;
    const timeStr = new Date(timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarClass}"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${content}</div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
}

function deleteMemory(memoryId) {
    if (confirm('Are you sure you want to delete this conversation?')) {
        savedMemories = savedMemories.filter(m => m.id !== memoryId);
        localStorage.setItem('beautyCompanionMemories', JSON.stringify(savedMemories));
        
        // If we're currently viewing the deleted memory, start a new chat
        if (currentMemoryId === memoryId) {
            startNewChat();
        } else {
            updateMemorySidebar();
        }
    }
}

function toggleMemorySidebar() {
    const sidebar = document.getElementById('memorySidebar');
    const icon = document.getElementById('sidebarToggleIcon');
    
    sidebarCollapsed = !sidebarCollapsed;
    
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        icon.className = 'fas fa-chevron-right';
    } else {
        sidebar.classList.remove('collapsed');
        icon.className = 'fas fa-chevron-left';
    }
}

function saveMemoryToVirtualFolder(memory) {
    // Save memory HTML content to localStorage with a "virtual file" structure
    const filename = `${memory.companionName}_${new Date(memory.timestamp).toISOString().split('T')[0]}_${new Date(memory.timestamp).toTimeString().split(' ')[0].replace(/:/g, '-')}.html`;
    const memoryHtml = generateMemoryHtml(memory);
    
    // Store the HTML content in localStorage as a "virtual file"
    const virtualFiles = JSON.parse(localStorage.getItem('beautyCompanion_virtualFiles') || '{}');
    virtualFiles[filename] = {
        content: memoryHtml,
        memoryId: memory.id,
        timestamp: memory.timestamp,
        companionName: memory.companionName,
        filename: filename
    };
    localStorage.setItem('beautyCompanion_virtualFiles', JSON.stringify(virtualFiles));
    
    // Show success notification
    showToast(`💾 Memory saved: ${filename}`, 'success');
}

function showToast(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Show toast
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

function viewMemoryFile(memoryId) {
    // Find and open the memory file in a new window/tab
    const virtualFiles = JSON.parse(localStorage.getItem('beautyCompanion_virtualFiles') || '{}');
    
    for (const [filename, fileData] of Object.entries(virtualFiles)) {
        if (fileData.memoryId === memoryId) {
            // Open the HTML content in a new window
            const newWindow = window.open('', '_blank');
            newWindow.document.write(fileData.content);
            newWindow.document.close();
            showToast(`👀 Opened memory: ${filename}`, 'info');
            return;
        }
    }
    
    showToast('❌ Memory file not found', 'error');
}

function downloadMemoryFile(memoryId) {
    // Allow users to download a specific memory file if needed
    const virtualFiles = JSON.parse(localStorage.getItem('beautyCompanion_virtualFiles') || '{}');
    
    for (const [filename, fileData] of Object.entries(virtualFiles)) {
        if (fileData.memoryId === memoryId) {
            const element = document.createElement('a');
            element.setAttribute('href', 'data:text/html;charset=utf-8,' + encodeURIComponent(fileData.content));
            element.setAttribute('download', filename);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
            showToast(`📥 Downloaded: ${filename}`, 'success');
            return;
        }
    }
    
    showToast('❌ Memory file not found for download', 'error');
}

function generateMemoryHtml(memory) {
    const currentDate = new Date(memory.timestamp).toLocaleDateString();
    
    let messagesHtml = '';
    memory.chatHistory.forEach(msg => {
        const senderClass = msg.sender === 'user' ? 'user-message' : 'companion-message';
        const senderName = msg.sender === 'user' ? 'You' : memory.companionName;
        const timestamp = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messagesHtml += `
            <div class="message ${senderClass}">
                <div class="message-header">
                    <strong>${senderName}</strong>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-content">${msg.content}</div>
            </div>
        `;
    });

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${memory.title} - ${memory.companionName} - ${currentDate}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: ${memory.backgroundColor};
            line-height: 1.6;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        .header p {
            color: #666;
        }
        .message {
            margin-bottom: 1.5rem;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 2rem;
        }
        .companion-message {
            background: white;
            margin-right: 2rem;
        }
        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        .timestamp {
            opacity: 0.7;
        }
        .message-content {
            font-size: 1rem;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            background: white;
            border-radius: 10px;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💄 ${memory.title}</h1>
        <p>Conversation with ${memory.companionName} (${memory.companionType})</p>
        <p>Date: ${currentDate}</p>
        <p>Total Messages: ${memory.chatHistory.length}</p>
        <p>Memory ID: ${memory.id}</p>
    </div>
    
    <div class="conversation">
        ${messagesHtml}
    </div>
    
    <div class="footer">
        <p>Generated by Sephora Beauty Companion Studio</p>
        <p>This conversation memory was saved on ${new Date(memory.timestamp).toLocaleString()}</p>
        <p>Memory ID: ${memory.id}</p>
    </div>
</body>
</html>`;
}

// Companion data definitions
const companionData = {
    luna: {
        name: "Luna",
        type: "Beauty Expert",
        personality: "professional",
        avatar: "fas fa-crown",
        backgroundColor: "#f8e8f0",
        greeting: "Hello! I'm Luna, your professional beauty expert. I'm here to provide you with detailed knowledge and expert advice on all things beauty. How can I assist you today?",
        systemPrompt: "You are Luna, a professional and experienced beauty expert. You provide detailed, knowledgeable advice about skincare, makeup, and beauty products. You are helpful, professional, and always base your recommendations on proven beauty principles."
    },
    aria: {
        name: "Aria",
        type: "Beauty Bestie",
        personality: "friendly",
        avatar: "fas fa-heart",
        backgroundColor: "#fff2e6",
        greeting: "Hey there! I'm Aria, your friendly beauty bestie! I'm so excited to help you on your beauty journey. Whether you need product recommendations or just want to chat about beauty, I'm here for you! 💕",
        systemPrompt: "You are Aria, a friendly and supportive beauty companion. You speak in a warm, encouraging tone and always make the user feel confident. You're like a best friend who happens to know a lot about beauty. Use emojis occasionally and keep things fun and supportive."
    },
    victoria: {
        name: "Victoria",
        type: "Luxury Consultant",
        personality: "sophisticated",
        avatar: "fas fa-gem",
        backgroundColor: "#f5f0ff",
        greeting: "Good day! I'm Victoria, your luxury beauty consultant. I specialize in premium beauty experiences and sophisticated skincare regimens. Allow me to guide you through the world of luxury beauty with elegance and expertise.",
        systemPrompt: "You are Victoria, a sophisticated and elegant luxury beauty consultant. You have refined taste and specialize in high-end, premium beauty products. You speak with sophistication and focus on quality, luxury experiences, and premium skincare and makeup."
    },
    zoe: {
        name: "Zoe",
        type: "Trend Expert",
        personality: "trendy",
        avatar: "fas fa-fire",
        backgroundColor: "#ffe6f2",
        greeting: "Hey! I'm Zoe, your go-to trend expert! ✨ I'm always on top of the latest beauty trends, viral products, and what's hot right now. Ready to discover some amazing new beauty trends together?",
        systemPrompt: "You are Zoe, an energetic and trendy beauty expert who stays up-to-date with the latest beauty trends. You're enthusiastic, modern, and know about viral beauty products, TikTok trends, and what's popular with Gen Z. Use trendy language and be excited about new discoveries."
    }
};

// Add some animation styles for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator .message-text i {
        opacity: 0.4;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-indicator .message-text i:nth-child(1) {
        animation-delay: 0s;
    }
    
    .typing-indicator .message-text i:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator .message-text i:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
`;
document.head.appendChild(style);

function showStoredMemories() {
    console.log('=== STORED MEMORIES DEBUG ===');
    
    // Show localStorage memories
    const memories = JSON.parse(localStorage.getItem('beautyCompanion_memories') || '[]');
    console.log('Memories in localStorage:', memories);
    
    // Show virtual files
    const virtualFiles = JSON.parse(localStorage.getItem('beautyCompanion_virtualFiles') || '{}');
    console.log('Virtual files:', virtualFiles);
    
    // Show total count
    console.log(`Total memories: ${memories.length}`);
    console.log(`Total virtual files: ${Object.keys(virtualFiles).length}`);
    
    return { memories, virtualFiles };
}

// Call this function to debug
// showStoredMemories();

function exportAllMemories() {
    const virtualFiles = JSON.parse(localStorage.getItem('beautyCompanion_virtualFiles') || '{}');
    const memories = JSON.parse(localStorage.getItem('beautyCompanion_memories') || '[]');
    
    if (memories.length === 0) {
        showToast('No memories to export', 'info');
        return;
    }
    
    // Create a zip-like structure by creating an index file
    let indexHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beauty Companion Memories - Index</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
        .memory-item { background: #f5f5f5; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
        .memory-title { font-weight: bold; color: #667eea; }
        .export-info { background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }
    </style>
</head>
<body>
    <h1>🎨 Beauty Companion Studio - Memory Index</h1>
    
    <div class="export-info">
        <h3>📁 Memory Storage Information</h3>
        <p><strong>Total Memories:</strong> ${memories.length}</p>
        <p><strong>Export Date:</strong> ${new Date().toLocaleString()}</p>
        <p><strong>Storage Location:</strong> Browser localStorage + Virtual files</p>
        <p><strong>Note:</strong> Individual memory files are available through the "View" button in the chat interface.</p>
    </div>
    
    <h2>📚 All Conversations</h2>`;
    
    memories.forEach(memory => {
        const date = new Date(memory.timestamp).toLocaleDateString();
        indexHtml += `
        <div class="memory-item">
            <div class="memory-title">${memory.title}</div>
            <p><strong>Companion:</strong> ${memory.companionName} (${memory.companionType})</p>
            <p><strong>Date:</strong> ${date}</p>
            <p><strong>Messages:</strong> ${memory.chatHistory.length}</p>
            <p><strong>Memory ID:</strong> ${memory.id}</p>
        </div>`;
    });
    
    indexHtml += `
    <div class="export-info">
        <h3>🔍 How to Access Individual Memories</h3>
        <ol>
            <li>Go back to the Beauty Companion Studio</li>
            <li>Open any conversation from the sidebar</li>
            <li>Click the "👁️ View" button to see the full memory file</li>
            <li>Click the "📥 Download" button to save individual memories</li>
        </ol>
    </div>
</body>
</html>`;
    
    // Download the index file
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/html;charset=utf-8,' + encodeURIComponent(indexHtml));
    element.setAttribute('download', 'Beauty_Companion_Memory_Index.html');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    showToast(`📋 Memory index exported (${memories.length} memories)`, 'success');
}

function clearAllMemories() {
    if (confirm('Are you sure you want to delete ALL memories? This cannot be undone.')) {
        localStorage.removeItem('beautyCompanion_memories');
        localStorage.removeItem('beautyCompanion_virtualFiles');
        savedMemories = [];
        updateMemorySidebar();
        showToast('🗑️ All memories cleared', 'info');
    }
}
