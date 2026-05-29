import os
import requests
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

# --- CONFIG ---
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
OUTPUT_DIR = Path(__file__).parent / "recordings"
OUTPUT_DIR.mkdir(exist_ok=True)

# Language settings for Podcast (Longer format)
PODCAST_CONFIG = {
    "name": "French",
    "voice": "fr-FR-DeniseNeural", # Good for stories
    "ambient_music": None # We can add music later
}

def generate_podcast_story(topic: str):
    """Generates a long, engaging French story for a podcast (approx 5-10 mins)."""
    print(f"🎙️ Generating long podcast story for topic: {topic}")
    
    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prompt for a longer, more detailed story
    prompt = (
        f"Write a cozy, educational, and engaging children's story in French about: {topic}. "
        f"The story should be detailed, with vivid descriptions and a calm pace. "
        f"Target length: 500-800 words. "
        f"Structure: An introduction welcoming the listeners, the main story with 3 distinct parts, and a gentle conclusion with a lesson. "
        f"Output ONLY the story text in French."
    )
    
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a world-class French children's podcast narrator and author."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        story = r.json()['choices'][0]['message']['content'].strip()
        
        # Save story text
        timestamp = int(time.time())
        story_file = OUTPUT_DIR / f"story_{timestamp}.txt"
        story_file.write_text(story, encoding='utf-8')
        
        print(f"✅ Story generated ({len(story.split())} words)")
        return story, story_file
    except Exception as e:
        print(f"❌ Story generation failed: {e}")
        return None, None

def generate_cover_image(topic: str, filename_prefix: str):
    """Generates a podcast cover image using Pollinations AI."""
    print(f"🎨 Generating cover image for: {topic}")
    
    # Prompt for Flux
    prompt = f"Podcast cover art, high-quality professional design, {topic}, illustrative style, child-friendly, vibrant colors, cozy atmosphere, centered composition, 1024x1024"
    safe_prompt = requests.utils.quote(prompt)
    
    url = f"https://gen.pollinations.ai/image/{safe_prompt}?width=1024&height=1024&model=flux&nologo=true"
    
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
    }
    
    output_file = OUTPUT_DIR / f"{filename_prefix}.jpg"
    
    try:
        r = requests.get(url, headers=headers, timeout=120)
        r.raise_for_status()
        output_file.write_bytes(r.content)
        print(f"✅ Cover image saved: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Cover image generation failed: {e}")
        return None

async def convert_to_audio(story: str, filename_prefix: str):
    """Converts the story to a high-quality MP3 using edge-tts."""
    import edge_tts
    
    output_file = OUTPUT_DIR / f"{filename_prefix}.mp3"
    print(f"🔊 Converting story to audio: {output_file.name}")
    
    communicate = edge_tts.Communicate(story, PODCAST_CONFIG["voice"])
    await communicate.save(str(output_file))
    
    print(f"✅ Audio recording saved: {output_file}")
    return output_file

def choose_podcast_topic():
    """Picks the first topic from the topics file and removes it."""
    topics_file = Path(__file__).parent / "podcast_topics.txt"
    if not topics_file.exists():
        return "Une histoire magique pour les enfants"

    with open(topics_file, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]
    
    if not topics:
        return "Une nouvelle aventure française"
    
    selected = topics[0]
    
    # Save the rest back
    with open(topics_file, "w", encoding="utf-8") as f:
        f.write("\n".join(topics[1:]) + "\n")
        
    return selected

def main():
    if not POLLINATIONS_API_KEY:
        print("❌ Error: POLLINATIONS_API_KEY not found in .env")
        return

    topic = choose_podcast_topic()
    print(f"📌 Today's Podcast Topic: {topic}")
    
    story_text, text_file = generate_podcast_story(topic)
    
    if story_text:
        timestamp = int(time.time())
        filename_prefix = f"podcast_episode_{timestamp}"
        
        # 1. Generate Audio
        asyncio.run(convert_to_audio(story_text, filename_prefix))
        
        # 2. Generate Cover Image
        generate_cover_image(topic, filename_prefix)
        
        print("\n--- PODCAST EPISODE READY ---")
        print(f"Text: {text_file}")
        print(f"Audio: {OUTPUT_DIR}/{filename_prefix}.mp3")
        print(f"Image: {OUTPUT_DIR}/{filename_prefix}.jpg")

if __name__ == "__main__":
    main()
