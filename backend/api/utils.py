import os
import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
import re

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.0-flash"

def get_url_type(url):
    domain = urlparse(url).netloc
    if 'instagram.com' in domain:
        return 'instagram'
    elif 'twitter.com' in domain or 'x.com' in domain:
        return 'twitter'
    else:
        return 'blog'

def scrape_metadata(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('meta', property='og:title')
        title = title['content'] if title else soup.title.string if soup.title else url
        
        description = soup.find('meta', property='og:description')
        description = description['content'] if description else ""
        
        # Instagram specific (basic extraction, might need official API for full caption)
        # For a hackathon, we often rely on og tags if public
        
        return {
            'title': title,
            'caption': description,
            'html': response.text[:2000] # Pass some context to AI
        }
    except Exception as e:
        print(f"Scrape error: {e}")
        return {'title': 'Unknown', 'caption': '', 'html': ''}

def process_with_ai(url, scraped_data):
    prompt = f"""
    Analyze this social media link: {url}
    Content Title: {scraped_data.get('title')}
    Description: {scraped_data.get('caption')}
    
    Tasks:
    1. Categorize it (e.g., Fitness, Coding, Food, Travel, Design, etc.)
    2. Summarize it in exactly one sentence.
    3. Extract relevant hashtags if any.
    
    Output in format:
    Category: [Category]
    Summary: [Summary]
    Hashtags: #tag1, #tag2
    """
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = response.text
        
        category = re.search(r"Category: (.*)", text)
        summary = re.search(r"Summary: (.*)", text)
        hashtags = re.search(r"Hashtags: (.*)", text)
        
        return {
            'category': category.group(1).strip() if category else "Other",
            'summary': summary.group(1).strip() if summary else "No summary available.",
            'hashtags': [h.strip() for h in hashtags.group(1).split(',')] if hashtags else []
        }
    except Exception as e:
        print(f"AI error: {e}")
        return {
            'category': "General",
            'summary': scraped_data.get('caption')[:100] if scraped_data.get('caption') else "Saved link.",
            'hashtags': []
        }
