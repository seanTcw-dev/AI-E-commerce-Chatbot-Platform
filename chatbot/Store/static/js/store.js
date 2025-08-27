let currentUser = null;
let cart = [];
let products = [];
let socket = null;
let chatState = 'bot'; // 'bot' or 'live'
let liveChatSessionId = null;


// We no longer use DOMContentLoaded here. Instead, store.html will call a new entry function.
/**
 * This is the new main entry point, called from store.html after the page loads.
 * @param {object} userInfo - The user object passed from the Flask backend.
 */

function initializeWithServerData(userInfo) {
    if (!userInfo || !userInfo.email) {
        console.error("Server did not provide user info. This shouldn't happen.");
        // If the server fails to provide data, we do nothing. The server-side
        // protection in the route should have already redirected to login.
        return;
    }

    // Use the data from the server as our source of truth.
    currentUser = userInfo;
    localStorage.setItem('currentUser', JSON.stringify(currentUser)); // We still save it for other functions to use

    // Initialize Socket.IO connection for live agent chat
    socket = io({ transports: ['websocket'] });

    // --- Socket.IO handlers for agent communication ---
    socket.on('agent_assigned', function(data) {
        console.log('Agent assigned:', data);
        removeTypingIndicator();
        liveChatSessionId = data.room || data.session_id; // Handle both formats
        chatState = 'live';
        
        // Join the room
        socket.emit('join', {
            room: liveChatSessionId,
            username: currentUser.username || currentUser.fullName || 'Customer',
            user_type: 'customer'
        });

        showToast('An agent has joined!', 'success');
        const agentButton = document.querySelector('.talk-to-agent-btn');
        if (agentButton) {
            agentButton.disabled = false;
            agentButton.innerHTML = '<i class="fas fa-times-circle"></i> End Chat';
            agentButton.style.backgroundColor = '#e74c3c';
        }
    });

    socket.on('user_joined_notification', function(data) {
        console.log("User joined notification:", data);
        if (data.username !== (currentUser.username || currentUser.fullName)) {
            addChatMessage(`<strong>${data.username}</strong> has joined the chat.`, 'system');
        }
    });

    socket.on('message', function(data) {
        console.log('Received message:', data);
        // Don't display our own messages back to us
        if (data.sender !== (currentUser?.username || currentUser?.fullName)) {
            const message = data.msg || data.message || ''; // Handle both formats for backward compatibility
            const sender = data.sender || 'Agent';
            const messageText = message.trim();
            if (messageText) {
                addChatMessage(`<strong>${sender}:</strong> ${messageText}`, 'bot');
            } else {
                console.warn('Received empty message:', data);
            }
        }
    });

    socket.on('chat_ended_notification', (data) => {
        console.log('Chat ended notification:', data);
        // Reset chat state and update UI
        chatState = 'bot';
        liveChatSessionId = null;
        resetAgentButton();
        
        const message = data?.msg || data?.message || 'The chat session has ended. How can I assist you further?';
        addChatMessage(message, 'bot');
        showToast('Chat ended.', 'info');
    });

    socket.on('user_left_notification', (data) => {
        console.log('User left notification:', data);
        if (data && data.username) {
            addChatMessage(`<strong>${data.username}</strong> has left the chat.`, 'system');
            
            // If the agent leaves, end the session for the user
            if (data.user_type === 'staff' || data.username === 'Agent') {
                chatState = 'bot';
                liveChatSessionId = null;
                resetAgentButton();
            }
        }
    });

    socket.on('connect', function() {
        console.log('Socket.IO connected.');
        showToast('Live support connection established.', 'success');
    });

    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected.');
        showToast('Live support connection lost.', 'error');
        if (chatState === 'live') {
            chatState = 'bot';
            liveChatSessionId = null;
            addChatMessage('You have been disconnected from the live agent.', 'bot');
        }
    });

    socket.on('connect_error', (err) => {
        console.error('Socket.IO connection error:', err);
        showToast('Failed to connect to live support.', 'error');
    });

    // Now, run the rest of the original setup logic.
    updateUserDisplay();
    loadProducts();
    loadCart();
}

// Update user display (No change needed)
function updateUserDisplay() {
    const userElement = document.getElementById('currentUser');
    if (currentUser && userElement) {
        userElement.textContent = currentUser.username || currentUser.fullName || 'Guest';
    }
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('currentUser');
        localStorage.removeItem('beautyStore_cart');
        // Redirect to the SERVER'S logout route, not a file.
        window.location.href = '/store/logout';
    }
}

// Load products from data file (simulated)
async function loadProducts() {
    try {
        // In a real app, this would be an API call
        // For demo, we'll use the predefined product data
        products = [
            {
                id: 'P001',
                name: 'Fragrance Discovery Set',
                brand: 'Luxe Scents',
                price: 35.00,
                category: 'Fragrance',
                description: 'Premium fragrance discovery collection with multiple scent profiles',
                stock: 15,
                image: '/images/Discovery.jpg'
            },
            {
                id: 'P002',
                name: 'Eau de Parfum',
                brand: 'Elite Parfum',
                price: 195.00,
                category: 'Fragrance',
                description: 'Luxury eau de parfum with rich and captivating notes',
                stock: 8,
                image: '/images/Parfum.jpg'
            },
            {
                id: 'P003',
                name: 'Moisturizing Face Cream',
                brand: 'Beauty Care',
                price: 45.00,
                category: 'Skincare',
                description: 'Daily hydrating moisturizer for all skin types',
                stock: 25,
                image: '/images/Moisturizing.jpg'
            },
            {
                id: 'P004',
                name: 'Vitamin C Serum',
                brand: 'Glow Beauty',
                price: 65.00,
                category: 'Skincare',
                description: 'Brightening serum with powerful vitamin C formula',
                stock: 18,
                image: '/images/Serum.jpg'
            },
            {
                id: 'P005',
                name: 'Matte Lipstick Set',
                brand: 'Color Me',
                price: 25.00,
                category: 'Makeup',
                description: 'Long-lasting matte lipsticks in trendy shades',
                stock: 30,
                image: '/images/Lipstick Set.jpg'
            },
            {
                id: 'P006',
                name: 'Eyeshadow Palette',
                brand: 'Glamour Pro',
                price: 35.00,
                category: 'Makeup',
                description: '12-color eyeshadow palette with shimmer and matte finishes',
                stock: 22,
                image: '/images/Eyeshadow.jpg'
            }
        ];
        
        displayProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Error loading products', 'error');
    }
}

// Display products
function displayProducts(productsToShow) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    if (productsToShow.length === 0) {
        grid.innerHTML = '<p class="no-products">No products found. Try adjusting your filters.</p>';
        return;
    }
    
    grid.innerHTML = productsToShow.map(product => {
        const imageUrl = `/store/static${product.image}`;
        return `
        <div class="product-card">
            <div class="product-image" onclick="openProductModal('${product.id}')">
                <img src="${imageUrl}" alt="${product.name}" onerror="this.onerror=null;this.src='/store/static/images/placeholder.png';">
                <div class="product-actions">
                    <button class="btn-quick-view" onclick="event.stopPropagation(); openProductModal('${product.id}')">Quick View</button>
                    <button class="btn-add-to-cart" onclick="event.stopPropagation(); addToCart('${product.id}')">Add to Cart</button>
                </div>
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price">$${product.price.toFixed(2)}</p>
            </div>
        </div>`;
    }).join('');
}

// Add to cart
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    if (product.stock <= 0) {
        showToast('Sorry, this product is out of stock', 'error');
        return;
    }
    
    const existingItem = cart.find(item => item.id === productId);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: product.name,
            price: product.price,
            image: product.image,
            quantity: 1
        });
    }
    
    updateCartDisplay();
    saveCart();
    showToast(`${product.name} added to cart!`, 'success');
}

// Update cart display
function updateCartDisplay() {
    const cartCount = document.getElementById('cartCount');
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    const checkoutBtn = document.getElementById('checkoutBtn');

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;

    if (cart.length === 0) {
        cartItems.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
        cartTotal.textContent = '0.00';
        checkoutBtn.disabled = true;
    } else {
        cartItems.innerHTML = '';
        let total = 0;
        cart.forEach(cartItem => {
            const product = products.find(p => p.id === cartItem.id);

            if (product) {
                const itemElement = document.createElement('div');
                itemElement.className = 'cart-item';
                itemElement.innerHTML = `
                    <img src="/store/static${product.image}" alt="${product.name}" class="cart-item-image">
                    <div class="cart-item-details">
                        <span class="cart-item-name">${product.name}</span>
                        <span class="cart-item-price">$${product.price.toFixed(2)}</span>
                    </div>
                    <div class="cart-item-quantity">
                        <button onclick="updateCartQuantity('${product.id}', ${cartItem.quantity - 1})" class="quantity-btn">-</button>
                        <span>${cartItem.quantity}</span>
                        <button onclick="updateCartQuantity('${product.id}', ${cartItem.quantity + 1})" class="quantity-btn">+</button>
                    </div>
                    <button onclick="removeFromCart('${product.id}')" class="cart-item-remove"><i class="fas fa-trash"></i></button>
                `;
                cartItems.appendChild(itemElement);
                total += product.price * cartItem.quantity;
            }
        });
        cartTotal.textContent = total.toFixed(2);
        checkoutBtn.disabled = false;
    }
}

// Show toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// Save and load cart
function saveCart() {
    localStorage.setItem('beautyStore_cart', JSON.stringify(cart));
}

function loadCart() {
    const stored = localStorage.getItem('beautyStore_cart');
    if (stored) {
        cart = JSON.parse(stored);
        updateCartDisplay();
    }
}

// Toggle cart sidebar
function toggleCart() {
    const sidebar = document.getElementById('cartSidebar');
    const overlay = document.getElementById('cartOverlay');
    
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
}

// Filter products
function filterProducts() {
    const categoryFilter = document.getElementById('categoryFilter').value;
    const priceFilter = document.getElementById('priceFilter').value;
    
    let filtered = products;
    
    // Filter by category
    if (categoryFilter) {
        filtered = filtered.filter(p => p.category === categoryFilter);
    }
    
    // Filter by price
    if (priceFilter) {
        const [min, max] = priceFilter.split('-').map(Number);
        if (max) {
            filtered = filtered.filter(p => p.price >= min && p.price <= max);
        } else {
            filtered = filtered.filter(p => p.price >= min);
        }
    }
    
    displayProducts(filtered);
}

// Clear filters
function clearFilters() {
    document.getElementById('categoryFilter').value = '';
    document.getElementById('priceFilter').value = '';
    displayProducts(products);
}

// Search products
function handleSearchInput(event) {
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearchBtn');
    
    if (searchInput.value.length > 0) {
        clearBtn.style.display = 'block';
    } else {
        clearBtn.style.display = 'none';
    }

    if (event.key === 'Enter') {
        searchProducts();
    }
}

function clearSearch() {
    const searchInput = document.getElementById('searchInput');
    searchInput.value = '';
    document.getElementById('clearSearchBtn').style.display = 'none';
    filterAndDisplayProducts(); // Reset to show all products or current filter
}

function searchProducts() {
    filterAndDisplayProducts();
}

function filterAndDisplayProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    if (!searchTerm) {
        displayProducts(products);
        return;
    }
    
    const filtered = products.filter(p => 
        p.name.toLowerCase().includes(searchTerm) ||
        p.brand.toLowerCase().includes(searchTerm) ||
        p.description.toLowerCase().includes(searchTerm)
    );
    
    displayProducts(filtered);
}

// Update cart quantity
function updateCartQuantity(productId, newQuantity) {
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = newQuantity;
        updateCartDisplay();
        saveCart();
    }
}

// Remove from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartDisplay();
    saveCart();
    showToast('Item removed from cart', 'info');
}

// Checkout (mock)
function checkout() {
    if (cart.length === 0) return;
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    if (confirm(`Proceed with checkout? Total: $${total.toFixed(2)}`)) {
        // Mock checkout process
        showToast('Order placed successfully! (Demo)', 'success');
        cart = [];
        updateCartDisplay();
        saveCart();
        toggleCart();
    }
}

// Product modal functions (basic)
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const modal = document.getElementById('productModal');
    const modalBody = document.getElementById('modalBody');
    const imageUrl = `/store/static${product.image}`;
    modalBody.innerHTML = `
        <div class="modal-header">
            <h3>${product.name}</h3>
            <button class="close-modal" onclick="closeProductModal()">&times;</button>
        </div>
        <div class="modal-product">
            <div class="modal-product-image">
                <img src="${imageUrl}" alt="${product.name}">
            </div>
            <div class="modal-product-info">
                <p class="modal-brand">${product.brand}</p>
                <p class="modal-price">$${product.price.toFixed(2)}</p>
                <p class="modal-description">${product.description}</p>
                <p class="modal-stock">${product.stock} available</p>
                <button onclick="addToCart('${product.id}'); closeProductModal(); showToast('${product.name} added to cart!');" class="modal-add-btn">
                    <i class="fas fa-cart-plus"></i> Add to Cart
                </button>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeProductModal() {
    document.getElementById('productModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const productModal = document.getElementById('productModal');
    const studioModal = document.getElementById('studioModal');
    
    if (event.target === productModal) {
        closeProductModal();
    } else if (event.target === studioModal) {
        closeStudio();
    }
}

// Floating Chatbot Widget Functions
function toggleChatbot() {
    const container = document.getElementById('chatbotContainer');
    const widget = document.getElementById('chatbotWidget');
    const isActive = container.classList.toggle('active');
    
    // Toggle the active class on the widget for the icon animation
    if (isActive) {
        widget.classList.add('active');
        showToast('Beauty Assistant is here to help! 💄', 'info');
        // Focus the input when opening
        const input = document.getElementById('chatbotInput');
        if (input) setTimeout(() => input.focus(), 300);
    } else {
        widget.classList.remove('active');
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('chatbotInput');
    if (!messageInput) return; // Guard clause in case the element isn't found
    const message = messageInput.value.trim();
    if (message === '') return;

    addChatMessage(message, 'user');
    messageInput.value = '';

    if (chatState === 'live') {
        if (socket && socket.connected && liveChatSessionId) {
            const payload = {
                room: liveChatSessionId,
                msg: message,  // Using 'msg' to match backend expectation
                sender: currentUser.username || currentUser.fullName || 'Customer',
                user_type: 'customer'
            };
            console.log("Sending message to agent:", payload);
            socket.emit('message', payload);
            return; // Exit after sending to agent
        } else {
            console.error('Cannot send message: Socket not connected or missing session ID');
            addChatMessage("I'm sorry, I'm having trouble connecting to the live agent. Please try again.", 'bot');
            return;
        }
    }
    
    // If not in live chat, process with the bot
    showTypingIndicator();
    
    // Get the selected AI model from the dropdown
    const modelSelect = document.getElementById('aiModelSelect');
    const selectedModel = modelSelect ? modelSelect.value : 'gemini';
    
    // Send to backend for processing
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            model: selectedModel,
            user_id: currentUser?.id || currentUser?.email || 'anonymous'
        })
    })
    .then(response => response.json())
    .then(data => {
        removeTypingIndicator();
        console.log('Bot response:', data);
        
        if (data.response) {
            addChatMessage(data.response, 'bot');
        } else if (data.error) {
            console.error('Error in response:', data.error);
            addChatMessage(`I'm sorry, but I encountered an error: ${data.error}`, 'bot');
        } else {
            console.error('Unexpected response format:', data);
            addChatMessage('I apologize, but I received an unexpected response format. Please try again.', 'bot');
        }
    })
    .catch((error) => {
        removeTypingIndicator();
        const errorMsg = error.message || 'Unknown error occurred';
        console.error('Error in chat request:', error);
        
        // More specific error messages based on error type
        if (error.message && error.message.includes('Failed to fetch')) {
            addChatMessage('I\'m having trouble connecting to the server. Please check your internet connection and try again.', 'bot');
        } else {
            addChatMessage(`I'm sorry, but I encountered an error: ${errorMsg}`, 'bot');
        }
        
        // Show a toast notification for important errors
        showToast('Error: ' + errorMsg, 'error');
    });
}

function sendQuickMessage(message) {
    document.getElementById('chatbotInput').value = message;
    sendMessage();
}

function addChatMessage(message, type) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chatbot-message ${type}-message`;
    
    const avatar = type === 'user' 
        ? '<div class="message-avatar"><i class="fas fa-user"></i></div>'
        : '<div class="message-avatar"><i class="fas fa-robot"></i></div>';
    
    messageDiv.innerHTML = `
        ${avatar}
        <div class="message-content">${message}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbotMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-message bot-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar"><i class="fas fa-robot"></i></div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Fallback local responses (same as before, for offline mode)
function getLocalBotResponse(userMessage) {
    const message = userMessage.toLowerCase();
    
    // Product-specific responses
    if (message.includes('serum') || message.includes('vitamin c')) {
        return "Our Vitamin C Serum is perfect for brightening! It's currently $65 and great for all skin types. Would you like me to add it to your cart? ✨";
    }
    
    if (message.includes('dry skin') || message.includes('moisturizer')) {
        return "For dry skin, I recommend our Moisturizing Face Cream ($45) or the Eau de Parfum collection. Both are excellent for hydration! 💧";
    }
    
    if (message.includes('price') || message.includes('cost') || message.includes('$')) {
        return "Our products range from $25-$195. The Lipstick Set ($25) and Eyeshadow Palette ($35) are great affordable options! 💄";
    }
    
    if (message.includes('fragrance') || message.includes('perfume') || message.includes('scent')) {
        return "We have amazing fragrances! Try our Fragrance Discovery Set ($35) or luxury Eau de Parfum ($195). Both are customer favorites! 🌸";
    }
    
    if (message.includes('makeup') || message.includes('lipstick') || message.includes('eyeshadow')) {
        return "For makeup, check out our Matte Lipstick Set ($25) with 6 trendy shades, or our 12-color Eyeshadow Palette ($35)! 💋";
    }
    
    if (message.includes('recommend') || message.includes('suggest') || message.includes('best')) {
        return "Based on our bestsellers, I'd recommend starting with our Vitamin C Serum ($65) for skincare and Lipstick Set ($25) for makeup! Want specific recommendations for your skin type? 🌟";
    }
    
    // General responses
    const responses = [
        "I'm here to help with all your beauty needs! Are you looking for skincare, makeup, or fragrance products? 💄",
        "Tell me about your skin type or beauty goals, and I'll recommend the perfect products for you! ✨",
        "Would you like product recommendations, ingredient information, or help choosing the right shade? 🌟",
        "I can help you find products in your budget or suggest complete beauty routines! What interests you most? 💫"
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

function resetAgentButton() {
    const agentButton = document.querySelector('.talk-to-agent-btn');
    if (agentButton) {
        agentButton.disabled = false;
        agentButton.innerHTML = '<i class="fas fa-headset"></i> Talk to Agent';
        agentButton.style.backgroundColor = ''; // Reset any inline background color
        agentButton.classList.remove('active'); // Remove any active class if present
    }
}

function requestAgent() {
    console.log('requestAgent function called! Current chat state:', chatState);
    const agentButton = document.querySelector('.talk-to-agent-btn');
    
    // If already in live chat, end the chat
    if (chatState === 'live' && liveChatSessionId) {
        console.log('Ending chat session');
        socket.emit('end_chat', { 
            room: liveChatSessionId,
            username: currentUser.username || currentUser.fullName 
        });
        
        // Update UI immediately
        if (agentButton) {
            agentButton.disabled = true;
            agentButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ending...';
        }
        
        // Reset chat state after a short delay to allow server to process
        setTimeout(() => {
            chatState = 'bot';
            liveChatSessionId = null;
            resetAgentButton();
        }, 1000);
        return;
    }

    // Otherwise, start a new chat
    console.log('Requesting agent...');
    if (!socket) {
        console.error('Socket.IO object (socket) is null. Connection was never initialized.');
        showToast('Live support system is not available.', 'error');
        return;
    }

    console.log('Socket connection status:', {
        connected: socket.connected,
        id: socket.id 
    });

    if (!socket.connected) {
        showToast('Not connected to live support. Attempting to reconnect...', 'warning');
        console.log('Socket is not connected. Attempting to connect...');
        socket.connect(); 
        return;
    }
    
    addChatMessage("I'd like to talk to a live agent, please.", 'user');
    showTypingIndicator();

    // Disable the button to prevent multiple requests
    if(agentButton) {
        agentButton.disabled = true;
        agentButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Waiting...';
    }

    setTimeout(() => {
        removeTypingIndicator();
        addChatMessage("Of course. I'm finding an available agent for you. Please wait a moment.", 'bot');
        
        socket.emit('request_agent', {
            user_id: currentUser.id || currentUser.email,
            username: currentUser.username || currentUser.fullName,
            email: currentUser.email,
        });

        // Add a timeout to re-enable the button if no agent is found
        setTimeout(() => {
            if (agentButton && agentButton.disabled && chatState !== 'live') {
                agentButton.disabled = false;
                agentButton.innerHTML = '<i class="fas fa-headset"></i> Talk to Agent';
                addChatMessage("I'm sorry, all our agents seem to be busy right now. Please try again in a few minutes.", 'bot');
                showToast('No agents available at the moment.', 'warning');
            }
        }, 30000); // 30-second timeout
    }, 1000);
}

// Studio integration (kept simple)
function openStudio() {
    const modal = document.getElementById('studioModal');
    const iframe = document.getElementById('studioFrame');
    
    // Only load the iframe src when modal is actually opened
    if (!iframe.src) {
        // Pass user information to studio via URL parameters
        const userName = currentUser ? (currentUser.username || currentUser.fullName || 'Guest') : 'Guest';
        const userInfo = encodeURIComponent(JSON.stringify(currentUser || {}));
        iframe.src = `../beauty-companion-studio/studio.html?user=${encodeURIComponent(userName)}&userInfo=${userInfo}`;
    }
    
    modal.style.display = 'block';
    showToast('Opening Companion Studio...', 'info');
}

function closeStudio() {
    const modal = document.getElementById('studioModal');
    const iframe = document.getElementById('studioFrame');
    
    modal.style.display = 'none';
    // Optional: Reset iframe to prevent memory leaks on repeated opens
    // iframe.src = '';
}

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

// Initialize model selector when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize model selector and header color
    const modelSelect = document.getElementById('aiModelSelect');
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
});
