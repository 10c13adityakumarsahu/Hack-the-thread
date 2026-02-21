import os
import requests
from bs4 import BeautifulSoup
from google import genai
from urllib.parse import urlparse
import re
import time

# Configure Gemini - Using verified models
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
# Use a stable, verified model
MODEL_NAME = "gemini-2.0-flash"

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
    }
    
    target_url = url
    if platform == 'x':
        target_url = url.replace('twitter.com', 'vxtwitter.com').replace('x.com', 'vxtwitter.com')
    
    try:
        print(f"Bypassing login wall for {platform}")
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            meta_data = {
                'title': soup.find('meta', property='og:title') or soup.find('meta', name='twitter:title'),
                'description': soup.find('meta', property='og:description') or soup.find('meta', name='twitter:description'),
                'site_name': soup.find('meta', property='og:site_name'),
            }
            
            info = {k: v['content'] if v and v.has_attr('content') else None for k, v in meta_data.items()}
            
            if info['title'] or info['description']:
                return {
                    'title': info['title'],
                    'caption': info['description'] or "",
                    'body_text': f"Site: {info['site_name']}\nDescription: {info['description']}",
                    'status': 'ok'
                }
    except Exception as e:
        print(f"Social bypass failed: {e}")
    
    return None

def scrape_metadata(url):
    """Robust multi-layered scraping. Always returns a dict for the LLM to process."""
    platform = get_url_type(url)
    
    # Layer 1: Social Bypass
    if platform in ['instagram', 'x', 'tiktok']:
        social_data = scrape_social_metadata(url, platform)
        if social_data:
            return social_data

    # Layer 2: Jina Reader
    try:
        print(f"Layer 2: Jina scrape for: {url}")
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, headers={'X-Return-Format': 'markdown'}, timeout=12)
        
        if response.status_code == 200 and "Log In" not in response.text[:400]:
            content = response.text
            return {
                'title': content.split('\n')[0].strip('# ') if content else url,
                'caption': content[:800],
                'body_text': content[:3000],
                'status': 'ok'
            }
    except Exception:
        pass

    # Layer 3: Fallback (Minimal data, but LLM will still use it)
    return {
        'title': f"Saved {platform.capitalize()} Link",
        'caption': "",
        'body_text': f"URL: {url}",
        'status': 'restricted'
    }

def process_with_ai(url, scraped_data):
    """Generates high-quality metadata using LLM. Always called regardless of scrape result."""
    platform = get_url_type(url)
    categories_list = [
        "AI & Machine Learning", "Coding & Development", "Design & Creative", 
        "Business & Startups", "Marketing & Growth", "Finance & Crypto", 
        "Health & Fitness", "Food & Cooking", "Travel & Adventure", 
        "Personal Development", "News & Politics", "Entertainment & Pop Culture",
        "Science & Tech", "Gaming", "Productivity", "Social Media Trends", "Other"
    ]
    
    # Check if scraping actually gave us content
    is_restricted = scraped_data.get('status') == 'restricted'
    
    prompt = f"""
    You are an expert Content Curator. Transform the following data into a premium entry.
    
    SOURCE URL: {url}
    PLATFORM: {platform}
    SCRAPED DATA (STATUS: {scraped_data.get('status')}): {scraped_data}
    
    YOUR MISSION:
    Even if the SCRAPED DATA is sparse or restricted (e.g., login wall), you MUST generate high-quality metadata.
    1. **Title**: Professional and descriptive. If restricted, infer from the URL slug/username (e.g., "Post by @username on {platform}").
    2. **Category**: Select the MOST ACCURATE from: {categories_list}. DO NOT default to 'Other' if you can infer context from the URL.
    3. **Summary**: Insightful summary (max 30 words). If you can't see the content, mention it's a save from {platform} and infer its likely topic from the URL.
    4. **Hashtags**: 3-5 niche tags.
    
    JSON ONLY. NO EMOJIS.
    """
    
    import json
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        ai_output = json.loads(response.text)
            
        return {
            'title': ai_output.get('title', scraped_data.get('title')),
            'category': ai_output.get('category', 'Other'),
            'summary': ai_output.get('summary', 'Curated content saved for later review.'),
            'hashtags': ai_output.get('hashtags', [platform])
        }
    except Exception as e:
        print(f"LLM Processing Failed: {e}")
        # Final emergency fallback if even the LLM fails
        domain = urlparse(url).netloc.split('.')[-2].capitalize() if '.' in url else "Web"
        return {
            'title': f"Resource from {domain}",
            'category': "Other",
            'summary': f"A link saved from {domain}. Click source to view.",
            'hashtags': [platform, domain.lower()]
        }
