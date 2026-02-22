# Social Saver Bot - Architecture

##  How it Works

1.  **WhatsApp Link**: User sends an Instagram, Twitter, or Blog URL to the WhatsApp Bot (Meta Cloud API).
2.  **Django Webhook**: The Django backend receives the link via the `/api/webhook/whatsapp/` endpoint.
3.  **Link Processing**:
    *   **Scraping**: `BeautifulSoup` extracts initial metadata (title, description).
    *   **AI Enhancement**: Google's **Gemini AI** analyzes the content to:
        *   Automatically categorize it (Fitness, Coding, Food).
        *   Generate a concise 1-sentence summary.
        *   Extract relevant hashtags.
4.  **Database**: The processed data is stored in SQLite.
5.  **Dashboard**: The React frontend fetches items via REST API and displays them in a sleek, glassmorphic card layout.

## 🛠 Tech Stack
-   **Frontend**: React (Vite) + Framer Motion + Lucide Icons
-   **Backend**: Django + Django REST Framework
-   **AI**: Google Gemini Pro (via `google-generativeai`)
-   **Bot**: Meta WhatsApp Cloud API

##  Pipeline Diagram
```text
[ WhatsApp ] ----> [ Meta Cloud API ] ----> [ Django Webhook ]
                                                    |
                                                    v
[ React Dashboard ] <--- [ API ] <--- [ DB + Gemini AI ]
```
