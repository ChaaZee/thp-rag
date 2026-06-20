import os
import time
import requests
from youtube_transcript_api import YouTubeTranscriptApi

PROXY_URL = "http://wwqdcygj-rotate:zk3b0640mqej@p.webshare.io:80"

# Set environment keys
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

print("--- DIAGNOSTICS RUN ---")

# Let's hit the checker endpoint 3 times to see if the IP rotates
for i in range(3):
    try:
        api_instance = YouTubeTranscriptApi()
        
        # Manually assign your custom proxy session
        custom_session = requests.Session()
        custom_session.proxies = {"http": PROXY_URL, "https": PROXY_URL}
        custom_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        api_instance._http_client = custom_session 
        
        # Instead of fetching a video, we tell the session to fetch the IP API
        # This forces the exact engine your script uses to reveal its IP footprint
        response = api_instance._http_client.get("https://httpbin.org/ip", timeout=5)
        
        print(f"Request {i+1} IP Seen By Server: {response.json()['origin']}")
        
    except Exception as e:
        print(f"Request {i+1} Failed: {str(e)}")
        
    time.sleep(2)