import traceback

from youtube_transcript_api import YouTubeTranscriptApi
#from youtube_transcript_api import WebshareProxyConfig
import time
import random
import json
import os
import requests

output_file = "rag_dataset.jsonl"
video_ids = open("video_ids.txt", "r").read().splitlines()
WORDS_PER_CHUNK = 80
WEBSHARE_PROXY = "http://wwqdcygj-rotate:zk3b0640mqej@p.webshare.io:80"

api_instance = YouTubeTranscriptApi()

os.environ["HTTP_PROXY"] = WEBSHARE_PROXY
os.environ["HTTPS_PROXY"] = WEBSHARE_PROXY

with open(output_file, "a", encoding="utf-8") as f:
    for i, video_id in enumerate(video_ids):
        print(f"Processing video {i+1}/{len(video_ids)}: {video_id}")
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        attempt = 0
        success = False

        while not success and attempt < 15:
            attempt += 1
            try:

                api_instance = YouTubeTranscriptApi()
            
                # Manually assign your custom proxy session
                custom_session = requests.Session()
                custom_session.proxies = {"http": WEBSHARE_PROXY, "https": WEBSHARE_PROXY}
                custom_session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                api_instance._http_client = custom_session 

                # This forces the exact engine your script uses to reveal its IP footprint
                #ip = api_instance._http_client.get("https://httpbin.org/ip", timeout=5)
                #print(f"IP Seen By Server: {ip.json()['origin']}")

                # Fetch the transcript for the video
                entries = api_instance.fetch(video_id).to_raw_data()
                
                # Helper variables for chunking
                current_chunk_words = []
                chunk_start_time = 0.0

                for entry in entries:
                    text_line = entry['text'].strip()

                    # If this is the start of a new chunk, lock in timestamp
                    if not current_chunk_words:
                        chunk_start_time = entry['start']

                    current_chunk_words.extend(text_line.split())

                    # If we've reached the word limit, save the chunk
                    if len(current_chunk_words) >= WORDS_PER_CHUNK:
                        chunk_text = " ".join(current_chunk_words)

                        # Create clickable YouTube timestamp link
                        timestamp_link = f"https://www.youtube.com/watch?v={video_id}&t={int(chunk_start_time)}s"
                        
                        # Create the RAG payload
                        rag_payload = {
                            "text": chunk_text,
                            "metadata": {
                                "video_id": video_id,
                                "video_url": video_url,
                                "timestamp": chunk_start_time,
                                "timestamp_link": timestamp_link
                            },
                        }

                        # Write as a single JSON line (JSONL format)
                        f.write(json.dumps(rag_payload) + "\n")

                        # Reset for the next chunk
                        current_chunk_words = []

                # Handle any remaining words at the end of the video
                if current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    timestamp_link = f"https://www.youtube.com/watch?v={video_id}&t={int(chunk_start_time)}s"

                    rag_payload = {
                        "text": chunk_text,
                        "metadata": {
                            "video_id": video_id,
                            "video_url": video_url,
                            "timestamp": chunk_start_time,
                            "timestamp_link": timestamp_link
                        },
                    }

                    f.write(json.dumps(rag_payload) + "\n")

                    success = True

            except Exception as e:
                if "Subtitles are disabled for this video" in str(e):
                    print(f"Skipping video {video_id} with disabled subtitles.")
                    break
                if "No transcripts were found" in str(e):
                    print(f"Skipping video {video_id} with no transcripts found.")
                    break
                if "YouTube is blocking requests from your IP" in str(e):
                    print(f"YouTube blocking requests from your IP for video {video_id}. Retrying...")
                    time.sleep(random.uniform(4.0, 8.0))
                else:
                    print(f"Error fetching transcript for {video_id}: {e}")
                    traceback.print_exc()

        time.sleep(random.uniform(4.0, 8.0))

print(f"\nTask complete! Your RAG-ready dataset is saved in '{output_file}'")
