---
description: How to run the Social Saver project
---

# Running Social Saver

### 1. Backend Setup
1. Open a terminal in `backend/`
2. Create and activate a virtual environment (optional but recommended)
3. Install dependencies: `pip install django djangorestframework django-cors-headers google-generativeai twilio python-dotenv requests beautifulsoup4`
4. Set your API Key in `.env` (copy from `.env.example`)
5. Run migrations: `python manage.py migrate`
// turbo
6. Start server: `python manage.py runserver`

### 2. Frontend Setup
1. Open a terminal in `frontend/`
2. Install dependencies: `npm install`
// turbo
3. Start frontend: `npm run dev`

### 3. Testing the Webhook
- Use `ngrok` or similar to expose your local port 8000.
- Point your Twilio WhatsApp Sandbox webhook to `https://<your-url>/api/webhook/whatsapp/`.
- Send a link!
