import threading
import time
import os
import urllib.request
import logging

logger = logging.getLogger(__name__)

def ping_server():
    """
    Pings the server's own URL to keep it awake on platforms like Render.
    Relies on RENDER_EXTERNAL_URL environment variable properly set by Render,
    or manually set WEBSITE_URL.
    """
    url = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('WEBSITE_URL')
    
    if not url:
        logger.warning("Keep-alive: No RENDER_EXTERNAL_URL or WEBSITE_URL found. Skipping ping.")
        return

    # Ensure we are hitting a valid endpoint. 
    # If the URL is just the base, we might want to ensure we don't get a 404, 
    # though 404 is still activity.
    # Let's target the API root if possible.
    if not url.endswith('/'):
        url += '/'
    
    # Construct a URL that definitely hits the Django app
    # Changed from 'api/' to '' to hit the root or whatever is configured
    # Actually, based on URLs, 'api/' should work if it's the backend.
    # But let's just hit the base URL to be safe, any activity counts.
    target_url = url

    try:
        # usage of timeout is good practice
        with urllib.request.urlopen(target_url, timeout=10) as response:
            logger.info(f"Keep-alive ping sent to {target_url}. Status: {response.getcode()}")
    except Exception as e:
        logger.error(f"Keep-alive ping failed for {target_url}: {e}")

def start_keep_alive_loop():
    """
    Starts a background thread that pings the server every 10 minutes.
    """
    # Only start if we are likely in a production environment or explicitly told to
    # Render sets RENDER_EXTERNAL_URL by default if the option is enabled in Render dashboard
    if not (os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('WEBSITE_URL')):
        logger.info("Keep-alive: No environment URL found. Loop not started.")
        return

    def run():
        logger.info("Keep-alive loop started.")
        # Ping once at start
        ping_server()
        while True:
            time.sleep(600)  # 10 minutes (600 seconds)
            ping_server()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
