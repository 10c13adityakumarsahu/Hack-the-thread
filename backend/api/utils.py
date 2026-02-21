import os
import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
import re
import time
from playwright.sync_api import sync_playwright

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
    """Scrape metadata using Playwright for JS-heavy sites."""
    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Navigate to URL
            print(f"Playwright: Navigating to {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit for dynamic content
            page.wait_for_timeout(2000)
            
            # Extract content
            html = page.content()
            title = page.title()
            
            # Specific handling for social media titles/captions
            soup = BeautifulSoup(html, 'html.parser')
            
            og_title = soup.find('meta', property='og:title')
            og_desc = soup.find('meta', property='og:description')
            
            scraped_title = og_title['content'] if og_title else title
            scraped_caption = og_desc['content'] if og_desc else ""
            
            # For Instagram/Twitter, sometimes the title is just "Instagram" or "X"
            # We want more context from the body
            body_text = ""
            if soup.body:
                for script in soup(["script", "style"]):
                    script.decompose()
                body_text = soup.body.get_text(separator=' ', strip=True)[:2000]
            
            browser.close()
            
            return {
                'title': scraped_title.strip(),
                'caption': scraped_caption.strip(),
                'body_text': body_text.strip(),
                'html': html[:1000]
            }
    except Exception as e:
        print(f"Playwright scrape error for {url}: {e}")
        # Fallback to requests if Playwright fails
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
