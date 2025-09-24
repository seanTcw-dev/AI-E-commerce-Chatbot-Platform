🌸 Beauty Companion AI Chatbot Platform
*Dual-LLM powered e-commerce assistant for beauty & skincare*
An AI-powered e-commerce chatbot designed for the beauty & skincare domain.
It combines Generative AI (LLMs) + RAG (FAISS + embeddings) + real-time agent handoff to deliver personalized product recommendations and customer support.

✨ Highlights

•        🤖 Smart Chatbot – Natural language Q&A and skincare product advice

•        🧩 Dual LLM System – Online (Google Gemini 1.5) + Local (OpenHermes-2.5 / Mistral via Ollama) for flexibility, privacy, and cost control

•        🔎 RAG Search – AI answers grounded in real product data (FAISS + sentence-transformers)

•        👩‍💼 Live Agent Handoff – Seamless switch from AI to human agent via WebSocket

•        🛍️ E-commerce Flow – Browse, filter, add-to-cart, and checkout (demo)

•        🎨 Beauty Companion Studio – Create & chat with a customizable AI skincare assistant

•        📱 Multi-Channel – Works on Web (Flask) and Telegram



📸 Demo & UI

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

🚀 Quick Start
# 1) Clone repo
git clone https://github.com/seanTcw-dev/AI-E-commerce-Chatbot-Platform.git
cd AI-E-commerce-Chatbot-Platform

# 2) Setup environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3) Run backend (Flask app)
python chatbot/app.py

👉 Access the web app at: http://127.0.0.1:5000

(For Telegram bot and advanced setup, see PROJECT_DETAILS.md)

🧠 AI Models (Dual-LLM)

•       🌐 Online LLM: Google Gemini 1.5 — high-quality, up-to-date generative responses (requires GOOGLE_API_KEY).

•       🖥 Local LLM: teknium/OpenHermes-2.5-Mistral-7B served via Ollama (LOCAL_AI_URL) — for offline, privacy, and cost-sensitive mode.

•       ⚖️ Model Selection: Controlled in .env

         •Example: USE_LOCAL_AI=true/false or PREFERRED_MODEL=gemini|local

         •Backend has dynamic selection + fallback (e.g., prefer Gemini for reasoning, fallback to local if offline).

•       🔎 RAG Integration: Retrieved contexts from FAISS are injected into the chosen LLM so answers remain grounded in real product data.

TL;DR → Gemini for quality, Local LLM for privacy/cost. Router chooses the best.

🏗 Architecture (Simplified)
User
  ↓
[Web UI / Telegram]
  ↓
Flask Backend
  ↓
RAG (FAISS + Embeddings)
  ↓
Model Router
  ├─> 🌐 Google Gemini 1.5 (cloud)
  └─> 🖥 Local OpenHermes (Ollama)
  ↓
👩‍💼 Optional Live Agent (WebSocket + Email)



Model Router = logic that chooses Gemini or Local model based on .env, availability, or cost rules.
🌍 Why This Project?

•        💄 Enhance e-commerce with AI-driven product discovery

•        🌱 Support SDG Goal 3 (Health & Well-being)

•        ⚖️ Showcase Dual LLM architecture balancing quality, privacy & cost

📌 Roadmap

•        ✅ Chatbot with RAG

•        ✅ Dual LLM integration + model switching/fallback

•        ✅ Product recommendation engine

•        ✅ Live agent WebSocket + email alerts

•        ✅ Telegram bot integration

•        🔜 Persistent user profiles & history

•        🔜 Analytics dashboard for agents

•        🔜 Cloud deployment (Docker/Kubernetes)


📖 More Details

👉 See PROJECT_DETAILS.md
•       Advanced model configuration

•       Production hardening tips

•       Future extension guidelines

📜 License
MIT License — free to use, modify, and distribute.
