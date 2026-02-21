from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import SavedItem
from .serializers import SavedItemSerializer
from .utils import get_url_type, scrape_metadata, process_with_ai
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import re
import os
import json
import threading
from django.db import close_old_connections

class SavedItemViewSet(viewsets.ModelViewSet):
    queryset = SavedItem.objects.all().order_by('-created_at')
    serializer_class = SavedItemSerializer

def send_whatsapp_message(to, text):
    """Utility to send message via Meta WhatsApp Cloud API"""
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    
    if not access_token or not phone_number_id:
        print("ERROR: Missing WhatsApp API credentials in environment variables!")
        return None

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    
    print(f"Sending message to {to}...")
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        resp_json = response.json()
        print(f"Meta API Response Status: {response.status_code}")
        print(f"Meta API Response Body: {json.dumps(resp_json, indent=2)}")
        
        if response.status_code != 200:
            print(f"FAILED to send message to {to}. Status: {response.status_code}")
        
        return resp_json
    except Exception as e:
        print(f"Critical Error sending WhatsApp message: {e}")
        return None

def process_webhook_in_background(url, from_number):
    """Heavy lifting (Scraping + AI + DB) in a background thread."""
    try:
        print(f"Background: Processing URL {url}")
        item_type = get_url_type(url)
        
        print("Background: Scraping metadata...")
        scraped_data = scrape_metadata(url)
        
        print("Background: Processing with AI...")
        ai_data = process_with_ai(url, scraped_data)
        
        # Save to DB
        print("Background: Saving to database...")
        item = SavedItem.objects.create(
            url=url,
            item_type=item_type,
            title=scraped_data.get('title'),
            caption=scraped_data.get('caption'),
            summary=ai_data.get('summary'),
            category=ai_data.get('category'),
            hashtags=ai_data.get('hashtags')
        )
        
        reply_text = f"Got it! Saved to your '{item.category}' bucket.\n\nView your collection here: https://hack-the-thread.onrender.com/ 🚀"
        print(f"Background: Sending reply to {from_number}")
        send_whatsapp_message(from_number, reply_text)
        
    except Exception as e:
        print(f"Background process error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Crucial for long-running threads in Django
        close_old_connections()

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    # 1. Webhook Verification (GET)
    if request.method == 'GET':
        print("--- Webhook Verification (GET) ---")
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        
        if mode == 'subscribe' and token == verify_token:
            from django.http import HttpResponse
            return HttpResponse(challenge, content_type="text/plain")
        
        return Response("Verification failed", status=status.HTTP_403_FORBIDDEN)

    # 2. Handle Incoming Message (POST)
    if request.method == 'POST':
        data = request.data
        print("--- Incoming Webhook (POST) ---")
        print(f"Payload from Meta: {json.dumps(data, indent=2)}")
        
        try:
            entries = data.get('entry', [])
            if not entries:
                return Response(status=status.HTTP_200_OK)

            changes = entries[0].get('changes', [])
            if not changes:
                return Response(status=status.HTTP_200_OK)

            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return Response(status=status.HTTP_200_OK)

            message = messages[0]
            from_number = message.get('from')
            
            if message.get('type') != 'text':
                return Response(status=status.HTTP_200_OK)

            text_body = message.get('text', {}).get('body', '').strip()
            
            # 1a. Immediate Acknowledgement (User requested this happen first)
            ack_text = f"Received: \"{text_body}\"\n\nProcessing... ⏳"
            send_whatsapp_message(from_number, ack_text)

            # Simple URL extraction
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, text_body)
            
            if not urls:
                send_whatsapp_message(from_number, "I'm ready! Send me a link from Instagram, Twitter, or a Blog, and I'll save it for you! 🚀")
                return Response(status=status.HTTP_200_OK)
            
            url = urls[0]
            
            # --- Duplicate Protection ---
            
            # 1. Check if URL already exists
            if SavedItem.objects.filter(url=url).exists():
                send_whatsapp_message(from_number, "By the way, this link is already in your collection! 📂")
                return Response(status=status.HTTP_200_OK)

            # 3. Launch background thread for heavy processing
            # We already sent the "Processing" message above
            thread = threading.Thread(target=process_webhook_in_background, args=(url, from_number))
            thread.start()
            
            # Return 200 OK immediately
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
