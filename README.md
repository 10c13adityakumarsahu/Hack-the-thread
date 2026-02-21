# 🚀 Social Saver Bot: Your Personal Knowledge Base

**Turning Fleeting Social Links into Searchable Wisdom.**

Social Saver is a WhatsApp-powered bot that captures Instagram Reels, Twitter threads, and Blogs, automatically categorizing and summarizing them using AI, then displaying them on a premium web dashboard.

---

## 🌊 The Exact Data Flow

1.  **Input (WhatsApp)**: You send an Instagram Reel, Post, or Blog URL to your dedicated WhatsApp number (configured via Meta WhatsApp Cloud API).
2.  **Reception (Django)**: Meta sends a webhook notification to `backend/api/views.py:whatsapp_webhook`.
3.  **Processing Pipeline**:
    *   **Url Extraction**: The backend identifies the link type (Instagram, Twitter, or Blog).
    *   **Scraping**: `BeautifulSoup` (in `utils.py`) extracts the page title and the original caption/description.
    *   **AI Analysis**: The data is sent to **Google Gemini 1.5 Flash**. The AI:
        *   🏷️ **Categorizes**: Tags it as "Fitness", "Coding", "UI Design", etc.
        *   📝 **Summarizes**: Distills the content into a single punchy sentence.
        *   #️⃣ **Hashtags**: Extracts or generates relevant tags.
4.  **Storage**: The processed information is stored in a **SQLite database**.
5.  **Confirmation**: The bot sends a WhatsApp message back to you: *"Got it! Saved to your 'Design' bucket. Summary: [AI Summary]"*.
6.  **Visualization (React)**:
    *   The **Frontend Dashboard** fetches the items via the REST API (`/api/items/`).
    *   Content is displayed in a **Glassmorphic Grid**.
    *   **Real-time Search**: You can instantly search through titles, summaries, or categories.

---

## 🔍 Detailed Function Flow

### 1. The Input Flow (WhatsApp → Database)
*   **Entry Point**: Meta Cloud API receives a message and POSTs a JSON payload to `api/views.py:whatsapp_webhook`.
*   **Verification**: The same endpoint handles the initial `hub.challenge` verification from Meta (GET request).
*   **URL Extraction**: `re.findall` extract URLs from the JSON body.
*   **Classification**: `utils.py:get_url_type` identifies the platform (Instagram, Blog, etc.).
*   **Data Extraction**: `utils.py:scrape_metadata` uses `BeautifulSoup` to pull `<meta>` tags for the title and caption.
*   **AI Analysis**: `utils.py:process_with_ai` sends metadata to **Google Gemini AI** for categorization and summarization.
*   **Persistence**: `models.py:SavedItem.objects.create` saves the enriched data to SQLite.
*   **Confirmation**: `send_whatsapp_message` helper function calls the **Meta Graph API** to send a text reply.

### 2. The Presentation Flow (Database → UI)
*   **Boot**: `frontend/src/main.jsx` mounts the React `<App />`.
*   **Fetch**: `Dashboard.jsx` uses `useEffect` to call `services/api.js:getItems`.
*   **API Response**: Django's `SavedItemViewSet` queries the DB and uses `serializers.py` to return JSON.
*   **State Update**: React's `setItems` updates the UI state.
*   **Render**: `Card.jsx` displays each item with **Framer Motion** animations.
*   **Search**: `filteredItems` logic in `Dashboard.jsx` provides real-time search across titles, summaries, and tags.

---

## 🛠️ Project Structure

```text
├── backend/                # Django REST API
│   ├── api/                # Core logic (Views, Models, AI Utils)
│   ├── core/               # Project Settings
│   └── .env                # API Keys (Gemini, Meta Cloud API)
├── frontend/               # React + Vite Dashboard
│   ├── src/
│   │   ├── components/     # UI (Card, Dashboard)
│   │   ├── services/       # API Integration
│   │   └── App.jsx
└── ARCHITECTURE.md         # Detailed technical diagram
```

---

## 🚀 Setup & Execution

### 1. Backend (Django)
```bash
cd backend
pip install django djangorestframework django-cors-headers google-generativeai python-dotenv requests beautifulsoup4
# Add your GEMINI_API_KEY and WHATSAPP_* variables to .env
python manage.py migrate
python manage.py runserver
```

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

---

## 🔥 Hackathon "Wow" Factors
-   **Gemini AI Integration**: Goes beyond simple bookmarking; it actually *understands* the content you save.
-   **Meta Cloud API**: Uses the official WhatsApp infrastructure for maximum reliability.
-   **Premium Aesthetics**: Uses a sleek dark-mode design with glassmorphism, blur effects, and smooth `framer-motion` animations.
-   **Searchability**: Turns "hidden Instagram folders" into a searchable, usable database of ideas.
-   **Zero Friction**: No app to download. Just text your bot.

---

## 📡 Diagram of Connection
`WhatsApp User` → `Meta Cloud API` → `Django API (process & save)` ← `React Frontend (display)`
