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
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        
        if mode == 'subscribe' and token == verify_token:
            return Response(int(challenge), status=status.HTTP_200_OK)
        return Response("Verification failed", status=status.HTTP_403_FORBIDDEN)

    # 2. Handle Incoming Message (POST)
    if request.method == 'POST':
        data = request.data
        
        try:
            # Extracting information from Meta's nested JSON
            entry = data.get('entry', [{}])[0]
            change = entry.get('changes', [{}])[0]
            value = change.get('value', {})
            message = value.get('messages', [{}])[0]
            
            if not message:
                return Response(status=status.HTTP_200_OK)

            from_number = message.get('from')
            text_body = message.get('text', {}).get('body', '').strip()
            
            # Simple URL extraction
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, text_body)
            
            if not urls:
                send_whatsapp_message(from_number, "Hi! Send me a link from Instagram, Twitter, or a Blog, and I'll save it for you! 🚀")
                return Response(status=status.HTTP_200_OK)
            
            url = urls[0]
            item_type = get_url_type(url)
            
            # Processing
            scraped_data = scrape_metadata(url)
            ai_data = process_with_ai(url, scraped_data)
            
            # Save to DB
            item = SavedItem.objects.create(
                url=url,
                item_type=item_type,
                title=scraped_data.get('title'),
                caption=scraped_data.get('caption'),
                summary=ai_data.get('summary'),
                category=ai_data.get('category'),
                hashtags=ai_data.get('hashtags')
            )
            
            reply_text = f"✅ Got it! Saved to your '{item.category}' bucket.\n\nSummary: {item.summary}"
            send_whatsapp_message(from_number, reply_text)
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return Response(status=status.HTTP_200_OK) # Always return 200 to Meta to avoid retries

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
