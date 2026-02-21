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
    
    # Expanded category list for better accuracy
    categories_list = [
        "AI & Machine Learning", "Coding & Development", "Design & Creative", 
        "Business & Startups", "Marketing & Growth", "Finance & Crypto", 
        "Health & Fitness", "Food & Cooking", "Travel & Adventure", 
        "Personal Development", "News & Politics", "Entertainment & Pop Culture",
        "Science & Tech", "Gaming", "Productivity", "Social Media Trends", "Other"
    ]
    
    prompt = f"""
    You are an expert Content Curator and Metadata Engineer. Your goal is to transform messy scraped data into a premium, organized bookmark entry.
    
    SYSTEM CONTEXT:
    URL: {url}
    PLATFORM: {platform}
    SCRAPED TITLE: {scraped_data.get('title')}
    SCRAPED CAPTION: {scraped_data.get('caption')}
    FULL CONTENT SNIPPET: {scraped_data.get('body_text')}
    
    YOUR TASKS:
    1. **Title**: Create a compelling, "click-worthy" but professional title (max 60 chars). 
       - DO NOT use generic titles like "Instagram Post" or "YouTube Video". 
       - Capture the core hook or benefit of the content.
       - If it's a social media post, include the creator's handle if visible (e.g., "DeepSeek's new AI model breakdown by @tech_guru").
    
    2. **Category**: Select the MOST ACCURATE category from this specific list: {", ".join(categories_list)}.
       - Be precise. If it's about a new app, use "Science & Tech" or "Coding & Development" based on context.
    
    3. **Summary**: Write a high-value, insight-dense summary (20-30 words).
       - Focus on the "So what?". Why did the user save this? 
       - Avoid stalling phrases like "This is a post about...". Jump straight to the value.
    
    4. **Hashtags**: Generate 4-6 highly specific hashtags.
       - Mix broad tags (e.g., #AI) with niche tags (e.g., #LargeLanguageModels).
       - DO NOT just use the platform name as a tag.
    
    CONSTRAINTS:
    - NO emojis.
    - NO generic platform-only titles.
    - Response MUST be valid JSON.
    - If data is sparse, use the URL slug to intelligently guess the topic.
    
    RETURN FORMAT (JSON ONLY):
    {{
      "title": "...",
      "category": "...",
      "summary": "...",
      "hashtags": ["...", "...", "..."]
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        import json
        ai_output = json.loads(response.text)
        
        # Validation to ensure category is from our list
        final_category = ai_output.get('category', 'Other')
        if final_category not in categories_list:
           # Optional: attempt to map or default
           pass

        return {
            'title': ai_output.get('title', scraped_data.get('title')),
            'category': final_category,
            'summary': ai_output.get('summary', 'Saved high-quality content for later review.'),
            'hashtags': ai_output.get('hashtags', [platform])
        }
    except Exception as e:
        print(f"AI error: {e}")
        return {
            'title': scraped_data.get('title') or f"Saved {platform.capitalize()} Link",
            'category': "Other",
            'summary': "Insightful content saved from the web.",
            'hashtags': [platform]
        }
