import os
import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
import re
import time

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3-flash-preview"

def get_url_type(url):
    domain = urlparse(url).netloc.lower()
    if 'instagram.com' in domain:
        return 'instagram'
    elif 'twitter.com' in domain or 'x.com' in domain:
        return 'twitter'
    else:
        return 'blog'

def scrape_metadata(url):
    """Scrape metadata using Jina Reader API (handles JS rendering)."""
    try:
        print(f"Scraping using Jina Reader for: {url}")
        jina_url = f"https://r.jina.ai/{url}"
        headers = {
            'X-Return-Format': 'markdown'
        }
        # Using a longer timeout as rendering can take time
        response = requests.get(jina_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            content = response.text
            # Basic extraction from the Jina markdown/text
            lines = content.split('\n')
            title = lines[0].strip('# ') if lines else url
            
            return {
                'title': title,
                'caption': content[:500], # First 500 chars as caption hint
                'body_text': content[:3000], # More context for Gemini
                'html': '' # Not needed with Jina's clean text
            }
        else:
            print(f"Jina error {response.status_code}, falling back...")
            raise Exception("Jina failed")

    except Exception as e:
        print(f"Jina scrape error for {url}: {e}")
        # Standard fallback
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                'title': soup.title.string if soup.title else url,
                'caption': '',
                'body_text': soup.get_text()[:1000],
                'html': response.text[:1000]
            }
        except:
            return {'title': 'Link', 'caption': '', 'body_text': '', 'html': ''}

def process_with_ai(url, scraped_data):
    prompt = f"""
    Analyze the following social media/web content and extract key metadata.
    
    URL: {url}
    SCRAEPD TITLE: {scraped_data.get('title')}
    SCRAPED CAPTION: {scraped_data.get('caption')}
    BODY CONTEXT: {scraped_data.get('body_text')}
    
    TASKS:
    1.  **A Better Title**: If the scraped title is generic (like "Instagram" or "Twitter"), generate a descriptive title based on the content. If it's a video/reel, describe what happens if possible from the text.
    2.  **Category**: Categorize into one of: Technology, Design, Coding, Fitness, Food, Travel, Finance, News, Entertainment, or Other.
    3.  **Summary**: One concise sentence summarizing the main point.
    4.  **Hashtags**: List 3-5 relevant hashtags.
    
    RETURN ONLY A JSON OBJECT with these keys:
    "title": "...",
    "category": "...",
    "summary": "...",
    "hashtags": ["tag1", "tag2", ...]
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        import json
        ai_output = json.loads(response.text)
        
        return {
            'title': ai_output.get('title', scraped_data.get('title')),
            'category': ai_output.get('category', 'Other'),
            'summary': ai_output.get('summary', 'No summary available.'),
            'hashtags': ai_output.get('hashtags', [])
        }
    except Exception as e:
        print(f"AI processing error for {url}: {e}")
        return {
            'title': scraped_data.get('title'),
            'category': "Other",
            'summary': scraped_data.get('caption')[:100] if scraped_data.get('caption') else "Saved link.",
            'hashtags': []
        }
