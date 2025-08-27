// Authentication JavaScript - Refactored for Server-Side Logic

// --- Form Switching Functions (No change needed) ---
function switchToSignup() {
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('signupForm').classList.add('active');
}

function switchToLogin() {
    document.getElementById('signupForm').classList.remove('active');
    document.getElementById('loginForm').classList.add('active');
}


// --- Form Submission Handlers (Major changes) ---

// Handle login form submission
document.getElementById('loginFormSubmit').addEventListener('submit', function(e) {
    e.preventDefault(); // Always prevent the default synchronous form submission

    const form = e.target;
    const formData = new FormData(form); // Easily get all form fields

    // Send login credentials to the Flask backend
    fetch('/store/login', { // Use the correct blueprint URL
        method: 'POST',
        body: formData
    })
    .then(response => {
        // If the server responds with a redirect, the browser will follow it.
        // The '.ok' property checks for statuses in the 200-299 range.
        // A successful login should result in a redirect, so the browser handles it.
        if (response.ok && response.redirected) {
            window.location.href = response.url; // Go to the URL the server redirected to
            return; // Stop processing
        }
        // If not redirected, it means there was an error.
        return response.json(); // Expect a JSON error message from the server
    })
    .then(data => {
        if (data && data.error) {
            // Display the error message provided by the server
            showMessage(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Login Error:', error);
        showMessage('A network error occurred. Please try again.', 'error');
    });
});

// Handle signup form submission
document.getElementById('signupFormSubmit').addEventListener('submit', function(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    // Send new user data to the Flask backend for creation
    // NOTE: You will need to create a '/store/signup' route in your store_routes.py
    fetch('/store/signup', { // This route needs to be created on the backend
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Always expect a JSON response
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // Switch to the login form after successful signup
            setTimeout(() => {
                switchToLogin();
                // Pre-fill the email field for convenience
                document.getElementById('loginEmail').value = formData.get('email');
            }, 2000);
        } else {
            // Display the error from the server (e.g., "User already exists")
            showMessage(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Signup Error:', error);
        showMessage('A network error occurred during signup.', 'error');
    });
});


// --- Demo and Helper Functions (Minor changes) ---

// The "Demo Login" now just redirects to the server's login route.
// The server can handle a "guest" login if you implement that logic.
function demoLogin() {
    // This is a placeholder. A real demo login should be handled by the server.
    // For now, we'll just show a message. A better way would be to redirect
    // to something like '/store/login?demo=true'
    showMessage('Demo login feature should be handled by the server.', 'info');
}

// Message display function (No change needed)
function showMessage(text, type) {
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    const container = document.querySelector('.auth-container');
    const firstForm = container.querySelector('.auth-form');
    container.insertBefore(message, firstForm);
    setTimeout(() => message.classList.add('show'), 100);
    setTimeout(() => {
        message.classList.remove('show');
        setTimeout(() => message.remove(), 300);
    }, 4000);
}