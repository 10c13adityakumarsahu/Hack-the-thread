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

class SavedItemViewSet(viewsets.ModelViewSet):
    queryset = SavedItem.objects.all().order_by('-created_at')
    serializer_class = SavedItemSerializer

def send_whatsapp_message(to, text):
    """Utility to send message via Meta WhatsApp Cloud API"""
    access_token = os.environ.get("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
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
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return None

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
        
        print(f"Mode: {mode}")
        print(f"Token: {token}")
        print(f"Challenge: {challenge}")

        if mode == 'subscribe' and token == verify_token:
            print("Verification successful!")
            # Challenge must be returned as a raw string
            from django.http import HttpResponse
            return HttpResponse(challenge, content_type="text/plain")
        
        print("Verification failed!")
        return Response("Verification failed", status=status.HTTP_403_FORBIDDEN)

    # 2. Handle Incoming Message (POST)
    if request.method == 'POST':
        print("--- Incoming Webhook (POST) ---")
        data = request.data
        print(f"Payload: {json.dumps(data, indent=2)}")
        
        try:
            # Extracting information from Meta's nested JSON
            entries = data.get('entry', [])
            if not entries:
                print("No entries in payload")
                return Response(status=status.HTTP_200_OK)

            changes = entries[0].get('changes', [])
            if not changes:
                print("No changes in entry")
                return Response(status=status.HTTP_200_OK)

            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                print("No messages in value (likely status update)")
                return Response(status=status.HTTP_200_OK)

            message = messages[0]
            from_number = message.get('from')
            
            # Check if it's a text message
            if message.get('type') != 'text':
                print(f"Received non-text message type: {message.get('type')}")
                return Response(status=status.HTTP_200_OK)

            text_body = message.get('text', {}).get('body', '').strip()
            print(f"Message from {from_number}: {text_body}")
            
            # Simple URL extraction
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, text_body)
            
            if not urls:
                print("No URLs found, sending help message")
                send_whatsapp_message(from_number, "Hi! Send me a link from Instagram, Twitter, or a Blog, and I'll save it for you! 🚀")
                return Response(status=status.HTTP_200_OK)
            
            url = urls[0]
            print(f"Processing URL: {url}")
            item_type = get_url_type(url)
            
            # Processing
            print("Scraping metadata...")
            scraped_data = scrape_metadata(url)
            print("Processing with AI...")
            ai_data = process_with_ai(url, scraped_data)
            
            # Save to DB
            print("Saving to database...")
            item = SavedItem.objects.create(
                url=url,
                item_type=item_type,
                title=scraped_data.get('title'),
                caption=scraped_data.get('caption'),
                summary=ai_data.get('summary'),
                category=ai_data.get('category'),
                hashtags=ai_data.get('hashtags')
            )
            
            reply_text = f"Got it! Saved to your '{item.category}' bucket."
            print(f"Sending reply to {from_number}")
            send_whatsapp_message(from_number, reply_text)
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Webhook error: {e}")
            import traceback
            traceback.print_exc()
            return Response(status=status.HTTP_200_OK) # Always return 200 to Meta to avoid retries

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
