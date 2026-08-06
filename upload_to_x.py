"""
X (Twitter) Upload Script - 2025

Uploads generated video to X (Twitter) using Tweepy and X API v2.
"""

import os
from pathlib import Path
import tweepy

def get_authenticated_client():
    """Authenticate using X API credentials from environment."""
    
    # Get credentials from GitHub Secrets / environment
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError(
            "Missing X API credentials! Set these environment variables:\n"
            "  - X_API_KEY (Consumer Key)\n"
            "  - X_API_SECRET (Consumer Secret)\n"
            "  - X_ACCESS_TOKEN\n"
            "  - X_ACCESS_TOKEN_SECRET"
        )
    
    # Create Tweepy Client with OAuth 1.0a User Context
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # Also create API v1.1 client for media upload
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret, access_token, access_token_secret
    )
    api = tweepy.API(auth)
    
    return client, api

def upload_to_x(video_file, text, hashtags=None):
    """Upload video to X and create a tweet."""
    
    client, api = get_authenticated_client()
    
    # Add hashtags to text
    if hashtags:
        hashtag_str = ' '.join([f'#{tag}' for tag in hashtags])
        full_text = f"{text}\n\n{hashtag_str}"
    else:
        full_text = text
    
    # Ensure text is within X's character limit (280 characters)
    if len(full_text) > 280:
        # Truncate text but keep hashtags
        available_chars = 280 - len(hashtag_str) - 3  # -3 for "\n\n"
        truncated_text = text[:available_chars] + "..."
        full_text = f"{truncated_text}\n\n{hashtag_str}"
    
    print(f"[X] Uploading video: {video_file}")
    
    # Upload media using API v1.1 (required for video)
    media = api.media_upload(
        filename=str(video_file),
        media_category='tweet_video',
        chunked=True
    )
    
    print(f"[X] Media uploaded. Media ID: {media.media_id}")
    
    # Create tweet with media using API v2
    print(f"[X] Creating tweet: {full_text[:50]}...")
    
    response = client.create_tweet(
        text=full_text,
        media_ids=[media.media_id]
    )
    
    tweet_id = response.data['id']
    print(f"[X] ✅ Tweet posted! Tweet ID: {tweet_id}")
    print(f"[X] URL: https://x.com/i/status/{tweet_id}")
    
    return response

def main():
    """Upload the generated video to X."""
    video_file = Path('output/final_video.mp4')
    
    if not video_file.exists():
        print("[X] ❌ No video found at output/final_video.mp4")
        return
    
    # Read the topic from used_topics.txt (last line is the current topic)
    topic = ""
    used_topics_file = Path('used_topics.txt')
    
    if used_topics_file.exists():
        with open(used_topics_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                topic = lines[-1]  # Get the last used topic
    
    # Use topic as tweet text (or fallback)
    if topic:
        tweet_text = topic
    else:
        tweet_text = "Psychologie & Bien-etre"
    
    # Add relevant hashtags
    hashtags = [
        'Psychologie',
        'BienEtre',
        'DeveloppementPersonnel',
        'Motivation',
        'Shorts'
    ]
    
    # Upload to X
    try:
        upload_to_x(
            video_file=video_file,
            text=tweet_text,
            hashtags=hashtags
        )
    except Exception as e:
        print(f"[X] ❌ Upload failed: {e}")
        raise

if __name__ == '__main__':
    main()
