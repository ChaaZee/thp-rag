from yt_dlp import YoutubeDL

channel_urls = ["https://www.youtube.com/@thpstrength1/videos", "https://www.youtube.com/@IsaiahRivera1/videos", "https://www.youtube.com/@JohnEvans/videos"]

ydl_opts = {
    'extract_flat': True,       # Pulls only metadata instead of scanning individual video pages
    'force_generic_extractor': False,
    'sleep_interval': 5,        # Forces a minimum 5-second sleep between requests
    'max_sleep_interval': 10,   # Automatically randomizes the delay up to 10 seconds
    'sleep_requests': 1.5,      # Introduces short gaps between internal API calls
}

video_ids = []

with YoutubeDL(ydl_opts) as ydl:
    for channel_url in channel_urls:
        print(f"Processing channel: {channel_url}")
        try:
            # Fetch the channel's upload data dictionary
            channel_info = ydl.extract_info(channel_url, download=False)

            # Loop through the entries and extract the IDs
            if 'entries' in channel_info:
                for entry in channel_info['entries']:
                    if entry and 'id' in entry:
                        video_ids.append(entry['id'])

        except Exception as e:
            print(f"Skipping error on link {channel_url}: {e}")

print(len(video_ids))



with open('video_ids.txt', 'w', encoding='utf-8') as file:
    for vid_id in video_ids:
        # Write the ID and append a newline character to step to the next row
        file.write(f"{vid_id}\n")

print("Saved cleanly to video_ids.txt!")