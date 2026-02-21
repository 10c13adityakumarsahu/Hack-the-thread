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
MODEL_NAME = "gemini-2.5-flash-preview"

def get_url_type(url):
    domain = urlparse(url).netloc.lower()
    if 'instagram.com' in domain:
        return 'instagram'
    elif 'twitter.com' in domain or 'x.com' in domain:
        return 'x'
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'tiktok.com' in domain:
        return 'tiktok'
    else:
        return 'web'

def scrape_social_metadata(url, platform):
    """Specialized scraping for social media to avoid login walls."""
    headers = {
        'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    target_url = url
    # Use bot-friendly proxies for X/Twitter
    if platform == 'x':
        target_url = url.replace('twitter.com', 'vxtwitter.com').replace('x.com', 'vxtwitter.com')
    
    try:
        print(f"Bypassing login wall for {platform}: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract OpenGraph and Twitter Meta Tags (usually allowed through login walls)
            meta_data = {
                'title': soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title'),
                'description': soup.find('meta', property='og:description') or soup.find('meta', name='twitter:description') or soup.find('meta', property='description'),
                'site_name': soup.find('meta', property='og:site_name'),
                'image': soup.find('meta', property='og:image'),
            }
            
            # Clean up the extracted tags
            info = {k: v['content'] if v and v.has_attr('content') else None for k, v in meta_data.items()}
            
            if info['title'] or info['description']:
                return {
                    'title': info['title'] or f"{platform.capitalize()} Content",
                    'caption': info['description'] or "",
                    'body_text': f"Site: {info['site_name']}\nDescription: {info['description']}",
                    'status': 'ok'
                }
    except Exception as e:
        print(f"Social bypass failed: {e}")
    
    return None

def scrape_metadata(url):
    """Robust multi-layered scraping: Specialized Social -> Jina Reader -> Standard."""
    platform = get_url_type(url)
    
    # Layer 1: Specialized social bypass (Meta-tag crawler spoofing)
    if platform in ['instagram', 'x', 'tiktok']:
        social_data = scrape_social_metadata(url, platform)
        if social_data:
            return social_data

    # Layer 2: Jina Reader (Good for general blogs/articles)
    try:
        print(f"Layer 2: Scraping using Jina for: {url}")
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, headers={'X-Return-Format': 'markdown'}, timeout=15)
        
        if response.status_code == 200 and "Log In" not in response.text[:500]:
            content = response.text
            return {
                'title': content.split('\n')[0].strip('# ') if content else url,
                'caption': content[:1000],
                'body_text': content[:4000],
                'status': 'ok'
            }
    except Exception as e:
        print(f"Jina Layer failed: {e}")

    # Layer 3: Final Fallback (URL Info ONLY)
    return {
        'title': f"Shared {platform}",
        'caption': f"A link from {platform}",
        'body_text': f"Source URL: {url}. Content restricted by login wall.",
        'status': 'restricted'
    }

def process_with_ai(url, scraped_data):
    platform = get_url_type(url)
    
    prompt = f"""
    You are a professional metadata extractor.
    URL: {url}
    PLATFORM: {platform}
    SCRAPED TITLE: {scraped_data.get('title')}
    SCRAPED CAPTION: {scraped_data.get('caption')}
    CONTENT: {scraped_data.get('body_text')}
    
    TASK:
    Generate high-quality metadata for this saved link.
    If the content seems restricted (title is generic), use the URL to infer context.
    - Title: Descriptive (e.g., '@user's Fitness Reel' or 'Article about AI in 2024')
    - Category: Choose from [Technology, Design, Coding, Fitness, Food, Travel, Finance, News, Entertainment, Other]
    - Summary: 1 clean sentence.
    - Hashtags: 3-5 relevant tags.
    
    NO EMOJIS.
    RETURN ONLY JSON.
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        import json
        ai_output = json.loads(response.text)
        
        return {
            'title': ai_output.get('title', scraped_data.get('title')),
            'category': ai_output.get('category', 'Other'),
            'summary': ai_output.get('summary', 'Saved social media content.'),
            'hashtags': ai_output.get('hashtags', [platform])
        }
    except Exception as e:
        print(f"AI error: {e}")
        return {
            'title': scraped_data.get('title'),
            'category': "Other",
            'summary': "Saved from web.",
            'hashtags': [platform]
        }
