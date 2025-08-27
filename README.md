# 🧠 Beauty Companion AI Chatbot — Full Technical Overview

Home Page
<img width="905" height="393" alt="image" src="https://github.com/user-attachments/assets/7c1c0887-6882-4ac7-8d62-cd647ab51a5b" />
Product Page
<img width="1437" height="670" alt="image" src="https://github.com/user-attachments/assets/7a248b64-b8ed-4b3b-997b-fcfc1be94d8a" />
AI Chatbot
<img width="451" height="650" alt="image" src="https://github.com/user-attachments/assets/90823866-cb5c-49d9-b32d-48400006d396" />
<img width="453" height="662" alt="image" src="https://github.com/user-attachments/assets/2dec6aa5-97ca-4675-9850-c321e5b1f763" />
Agent Page
<img width="1080" height="591" alt="image" src="https://github.com/user-attachments/assets/ebc6ea36-a625-4944-808b-2b7e52e198b0" />
<img width="944" height="698" alt="image" src="https://github.com/user-attachments/assets/d07cacce-5379-4b18-a923-8c541e75135e" />
<img width="1080" height="754" alt="image" src="https://github.com/user-attachments/assets/06366684-97a0-4231-84c6-444d216962c1" />
Telegram Page
<img width="490" height="1080" alt="image" src="https://github.com/user-attachments/assets/f57dec0a-d53c-454d-bad4-c6adea78743a" />
<img width="490" height="1080" alt="image" src="https://github.com/user-attachments/assets/1c602334-321a-4cbc-8de1-db993d472976" />
<img width="490" height="1080" alt="image" src="https://github.com/user-attachments/assets/4ffad8ce-a060-48b4-9875-8fe4b84360d1" />
Telegram Agent Live Chat Page
<img width="1080" height="830" alt="image" src="https://github.com/user-attachments/assets/7dbd55a2-ad03-4e4a-a2b0-1cd52b7a69d5" />
Telegram Email Page
<img width="966" height="680" alt="image" src="https://github.com/user-attachments/assets/5b8d1c11-f063-4f06-b7f9-8c38c2b25ffc" />
Web Email Page
<img width="1080" height="522" alt="image" src="https://github.com/user-attachments/assets/97de17ec-3f0f-4860-b27a-40eef5854fd4" />
Login Page
<img width="568" height="879" alt="image" src="https://github.com/user-attachments/assets/6421a46c-195c-447f-a5b1-d4fea76c7479" />
Online Shopping Page
<img width="1375" height="637" alt="image" src="https://github.com/user-attachments/assets/adf7bd86-3e28-4d8a-b9af-17ca2994f11d" />
Product Information Page
<img width="1000" height="557" alt="image" src="https://github.com/user-attachments/assets/53e0e894-817e-40e5-9014-7f75f440f5ba" />
Ai Chatbot Personality Studio
<img width="1300" height="601" alt="image" src="https://github.com/user-attachments/assets/1040041d-d65b-45a1-9037-a2a2d8a8a9dd" />
<img width="1412" height="753" alt="image" src="https://github.com/user-attachments/assets/0f0a5a55-603b-44a3-83a5-742096925b99" />
Filter Page
<img width="1423" height="656" alt="image" src="https://github.com/user-attachments/assets/96e4bcd5-6195-4130-b3c8-3469a8fc0187" />
Search Page
<img width="1323" height="679" alt="image" src="https://github.com/user-attachments/assets/44066913-a8ef-44ef-ac2c-94b453e031d5" />
Cart Page
<img width="505" height="881" alt="image" src="https://github.com/user-attachments/assets/958005b3-7894-4e71-888f-2dd2335bc012" />
## 📌 Project Goal and Use Case
The Beauty Companion AI Chatbot is an intelligent, multi-modal customer support and product recommendation system for the beauty and skincare domain. It leverages Generative AI (LLMs) and Retrieval-Augmented Generation (RAG) to provide personalized product advice, answer customer queries, and connect users to live agents. The system is designed to enhance e-commerce experiences, support SDG Goal 3 (Good Health & Well-being) by promoting informed skincare choices, and streamline agent workflows via automation and real-time chat.



- **Conversational AI Chatbot**: Natural language chat for product Q&A, recommendations, and support, powered by advanced LLMs and RAG.
- **Retrieval-Augmented Generation (RAG)**: Uses FAISS and sentence-transformers to ground LLM responses in real product data, ensuring accurate and context-aware answers.
- **Live Agent Handoff**: Seamless escalation from AI to human agent via real-time WebSocket chat, with agent notification, session management, and agent assignment logic (one agent per session, agent join/leave tracking).
- **Product Recommendation Engine**: Embeds product info and matches user needs to best-fit items, supporting personalized and context-driven suggestions, with filtering by category, skin type, and more.
- **Beauty Companion Studio**: Interactive web module allowing users to create, customize, and chat with their own AI beauty assistant, including persona selection, memory/autosave, and persistent companion settings.
- **Product Gallery & Image Support**: Users can browse products with images, view bestsellers, search/filter products, and access detailed product and review information.
- **Review Analysis**: Integrates product review data for more informed recommendations and sentiment-aware responses.
- **Session-Based Chat & History**: Each chat session is uniquely identified, with support for session-based context, agent assignment, and (optionally) chat history.
- **Multi-Channel Support**: Unified experience across web (Flask/Jinja2), Telegram bot (with markdown and command support), and Studio UI, with extensibility for future channels (e.g., WhatsApp, WeChat).
 - **Advanced Agent Management**: Agent email notification system (agent emails are read from an external `agents.txt` file for easy management), agent session tracking, agent availability logic, and one-agent-per-session enforcement for quality support.
## 🏢 Demo vs. Production: Data Management & Real-Time Features
This project is designed for rapid prototyping, academic demonstration, and small-team use. To maximize speed and minimize setup, we use browser local storage for user data (username, password, cart, etc.) and a simple `agents.txt` file for agent management. This approach avoids the need for a backend database, making the system easy to run and test on any machine.

**How it works in this demo:**
- Usernames, passwords, and cart/session data are stored in the browser's local storage (client-side), not on a server or database.
- Product data is loaded from CSV files and embedded for AI search, not from a live database.
- Agent emails are managed via a text file, and notifications are sent via Google SMTP.

**How a real-world company would do it:**
- User authentication, passwords, and profiles would be securely stored in a backend database (e.g., PostgreSQL, MySQL, MongoDB), with proper encryption and hashing for passwords.
- Product catalog, inventory, and cart data would be managed in a database, supporting multi-user, multi-device, and persistent sessions.
- Real-time features (chat, notifications, cart updates) would use scalable backends such as Firebase, Redis, or cloud-based WebSocket services for reliability and performance.
- Agent management would use a database, real-time dashboards, and dynamic assignment logic, often integrated with CRM/helpdesk platforms.
- Security, privacy, and compliance (e.g., GDPR) would be enforced at all layers.

**Trade-offs:**
- The demo approach is fast, simple, and great for learning, but not suitable for production or handling sensitive data.
- Production systems require more setup, but provide security, scalability, and robustness for real users and business needs.

This project demonstrates the core logic and user experience in a lightweight, easily auditable way, and can be extended to production-grade architecture as needed.
- **User Authentication & Guest Access**: Demo login, guest mode, and session-based dashboard for store features, with extensible user management.
 - **Email Notifications (Google SMTP)**: Automated emails to agents for new chat requests, sent securely via Gmail SMTP (Google's email service), with customizable templates, agent list management, and multi-path agent file discovery.
- **Analytics & Logging**: Rotating logs, session tracking, error handling, and extensible analytics hooks for future reporting and admin dashboards.
- **Modular & Extensible Design**: Flask Blueprints, service modules, and configuration for easy extension and maintenance; clear separation of routes, services, and templates.
- **Security & Config Management**: API keys, agent emails, and sensitive data managed via `.env` and external files; CORS and input validation for safe operation.
- **Testing & Validation**: System and integration tests for both backend and Telegram bot components, with test scripts for API, email, and bot logic.
- **Internationalization & Accessibility**: (If present) Extensible for multi-language support and accessible UI design.
- **Error Handling & Robustness**: Graceful error messages, fallback logic for missing data, and robust handling of missing agent files or API keys.

- **Local Server Hosting**: When starting `app.py`, your computer acts as a server, allowing users on the same network to access the website via your machine's IP address. This enables easy LAN-based demos and multi-device access.
- **Conversational AI Chatbot**: Natural language chat for product Q&A, recommendations, and support, powered by advanced LLMs and RAG.
- **Retrieval-Augmented Generation (RAG)**: Uses FAISS and sentence-transformers to ground LLM responses in real product data, ensuring accurate and context-aware answers.
- **Live Agent Handoff**: Seamless escalation from AI to human agent via real-time WebSocket chat, with agent notification, session management, and agent assignment logic (one agent per session, agent join/leave tracking).
- **Product Recommendation Engine**: Embeds product info and matches user needs to best-fit items, supporting personalized and context-driven suggestions, with filtering by category, skin type, and more.
- **E-commerce Features**: Full e-commerce flow including product filtering, search, add to cart, and checkout. User cart and session data are stored in browser local storage for privacy and speed, eliminating the need for a backend database.
- **Beauty Companion Studio**: Interactive web module allowing users to create, customize, and chat with their own AI beauty assistant, including persona selection, memory/autosave, and persistent companion settings.
- **Product Gallery & Image Support**: Users can browse products with images, view bestsellers, search/filter products, and access detailed product and review information.
- **Review Analysis**: Integrates product review data for more informed recommendations and sentiment-aware responses.
 - **Session-Based Chat & History (WebSocket)**: Each chat session is uniquely identified, with real-time communication powered by Flask-SocketIO (WebSocket), supporting session-based context, agent assignment, and (optionally) chat history.
- **Multi-Channel Support**: Unified experience across web (Flask/Jinja2), Telegram bot (with markdown and command support), and Studio UI, with extensibility for future channels (e.g., WhatsApp, WeChat).
- **Advanced Agent Management**: Agent email notification system, agent session tracking, agent availability logic, and one-agent-per-session enforcement for quality support.
- **User Authentication & Guest Access**: Demo login, guest mode, and session-based dashboard for store features, with extensible user management.
- **Email Notifications**: Automated emails to agents for new chat requests, with customizable templates, agent list management, and multi-path agent file discovery.
- **Analytics & Logging**: Rotating logs, session tracking, error handling, and extensible analytics hooks for future reporting and admin dashboards.
- **Modular & Extensible Design**: Flask Blueprints, service modules, and configuration for easy extension and maintenance; clear separation of routes, services, and templates.
- **Security & Config Management**: API keys, agent emails, and sensitive data managed via `.env` and external files; CORS and input validation for safe operation.
- **Testing & Validation**: System and integration tests for both backend and Telegram bot components, with test scripts for API, email, and bot logic.
- **Internationalization & Accessibility**: (If present) Extensible for multi-language support and accessible UI design.
- **Error Handling & Robustness**: Graceful error messages, fallback logic for missing data, and robust handling of missing agent files or API keys.


## ⚙️ AI Model(s) and Integration
- **LLMs Used**:
  - **Online API**: Google Gemini 1.5 (via `google-generativeai`), used for high-quality, up-to-date generative responses and product Q&A.
  - **Local Model**: `teknium/OpenHermes-2.5-Mistral-7B` (served via Ollama REST API at `LOCAL_AI_URL`), used for privacy-preserving, offline, or cost-effective inference.
- **Model Switching**: The backend dynamically selects between Gemini 1.5 and the local OpenHermes-2.5-Mistral-7B model based on `.env` configuration. This allows seamless fallback or hybrid operation, with endpoints and API keys set via `GOOGLE_API_KEY` and `LOCAL_AI_URL`.
- **Embeddings & Semantic Search**: Product data is embedded using `sentence-transformers` (`all-MiniLM-L6-v2`), and indexed with FAISS for fast similarity search and context retrieval.
- **RAG Pipeline**: On each user query, the system:
  1. Embeds the query using the same transformer model as the product data.
  2. Searches the FAISS index for the most relevant product contexts.
  3. Passes the retrieved context and user query to the selected LLM (Gemini 1.5 or OpenHermes-2.5-Mistral-7B) to generate a grounded, context-aware response.
  4. Returns the answer to the user, with the option to escalate to a live agent if needed.

- **Local Network Access**: The Flask app can be started in a mode that binds to your computer's IP address, making the web application accessible to other devices on the same LAN. This is ideal for classroom demos, team testing, or multi-device scenarios.
- **Flask Backend**: Modularized with Blueprints (`main`, `store`, `studio`).
 - **WebSocket (Flask-SocketIO)**: Real-time, bidirectional chat for both customer and agent, with room/session management, instant message delivery, and agent-customer handoff.
- **AI Service Layer**: Handles LLM calls, RAG, and model selection.
 - **Email Service (Google SMTP)**: Sends notifications to agents using Gmail SMTP (Google's secure email platform), ensuring reliable and authenticated delivery of chat requests and notifications.
- **Telegram Bot**: Async Python bot with command handlers, markdown, and backend integration.
- **Frontends**: 
  - Main chatbot UI (Flask/Jinja2 + JS)
  - Beauty Companion Studio (customizable AI persona, modern UI)
  - Telegram chat interface

```
[User] ⇄ [Flask Web UI / Telegram] ⇄ [Flask API/SocketIO] ⇄ [AI Service (Gemini/Local)] ⇄ [FAISS/Product Data]
                                              ⇅
                                         [Live Agent]
```

## 🧠 User Flow
1. User visits the site or Telegram bot and starts a chat.
2. User asks a question (e.g., "What moisturizer is best for oily skin?").
3. System embeds the query, retrieves relevant product contexts, and generates a response via LLM.
4. If needed, user can request a live agent; agent is notified by email and joins via a dedicated chat page.
5. User can also interact with the Beauty Companion Studio to create a personalized AI assistant.
6. On Telegram, users can use commands to browse products, connect to agents, or end chat.

## 🤖 Telegram Bot Features
- **Supported Commands:**
  - `/start` — Welcome message
  - `/help` — List commands and usage
  - `/products` — Show best-selling products
  - `/gallery` — Browse products with images
  - `/agent` — Connect to a live agent
  - `/end` — End the current agent chat
- **Welcome Message Logic:** Sends a friendly intro and usage guide on `/start`.
- **Markdown Formatting:** Product info and responses are formatted for clarity.
- **Backend Integration:** Shares AI, RAG, and agent handoff logic with main backend.

## 📂 Directory Summary
```
project-root/
├── agents.txt                # List of agent emails for notifications
├── app.log                   # Rotating log files
├── requirements.txt          # Python dependencies
├── .env                      # API keys and config
├── beauty-companion-studio/  # Studio UI (custom AI companion)
│   ├── static/               # CSS/JS for Studio
│   └── templates/            # studio.html
├── chatbot/                  # Main Flask backend
│   ├── app.py                # App entrypoint
│   ├── agent_names.json      # Default agent names
│   ├── routes/               # Flask Blueprints (main, store, studio)
│   ├── services/             # AI, chat, email, Gemini, extensions
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # Static assets
├── telegram_bot/             # Telegram bot and services
│   ├── telegram_bot.py       # Bot entrypoint
│   ├── services/             # Telegram bot/email/web services
│   ├── templates/            # Telegram HTML/email templates
│   └── tests/                # Telegram bot tests
├── Vector_Store/             # Embedding and FAISS logic
│   └── embedFunc.py          # Embedding generation/cache
├── DataSet/                  # Product and review CSVs
├── tests/                    # System and integration tests
```
- **chatbot/routes/**: Flask Blueprints for main site, store (login/dashboard), and studio.
- **chatbot/services/**: Modular services for AI, chat (WebSocket), email, Gemini, and agent logic.
- **Vector_Store/**: Handles embedding generation and FAISS index creation for RAG.
- **telegram_bot/services/**: Telegram bot logic, email notifications, and web integration.
- **beauty-companion-studio/**: Standalone UI for creating and customizing AI companions.
- **DataSet/**: Cleaned and original product/review data for embedding and recommendations.

## 🔐 Security and Config
- **API Keys & Secrets**: Managed via `.env` (never hardcoded in code).
- **CORS**: Enabled via Flask-CORS for safe cross-origin requests.
- **Input Validation**: Handled in Flask routes and service layers.
- **Logging**: Rotating logs for error tracking and audit.
- **Agent Emails**: Loaded from `agents.txt` (not in code).

## 📈 Completed Milestones
- [x] AI chatbot with RAG and Gemini integration
- [x] Product recommendation engine
- [x] Live agent handoff (WebSocket)
- [x] Email notification system
- [x] Telegram bot with command support
- [x] Beauty Companion Studio UI
- [x] Modular Flask backend (Blueprints, services)
- [x] Embedding and FAISS index pipeline
- [x] User authentication (demo)
- [x] System and Telegram bot tests

## 🚀 Future Work
- Add user profile and chat history persistence
- Expand product catalog and support image-based queries
- Integrate more LLMs (OpenAI, Claude, etc.)
- Enhance security (rate limiting, advanced validation)
- Deploy on scalable cloud infrastructure (Docker, Kubernetes)
- Add analytics dashboard for admin/agents
- Support multi-language and accessibility features

## 🧾 Additional Notes
- Designed for academic and demo use; production deployment requires further security hardening.
- Modular codebase: easy to extend with new AI models, channels, or features.
- All sensitive keys/configs are loaded from `.env` and not committed to version control.
- For academic reports, reference the RAG pipeline, modular Flask architecture, and multi-channel (web + Telegram) integration as key innovations.
