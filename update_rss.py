import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import yaml

# --- CONFIG ---
RSS_FILE = Path(__file__).parent / "feed.xml"
RECORDINGS_DIR = "recordings" # Relative path for the URL
BASE_URL = "https://kreggsmonde-podcast.netlify.app"

def create_rss_shell():
    """Creates the basic structure of a podcast RSS feed."""
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    
    channel = ET.SubElement(rss, "channel")
    
    # Podcast Metadata
    ET.SubElement(channel, "title").text = "kreggsmonde"
    ET.SubElement(channel, "description").text = "Des histoires magiques pour apprendre le français et s'endormir paisiblement."
    ET.SubElement(channel, "link").text = BASE_URL
    ET.SubElement(channel, "language").text = "fr-fr"
    
    # iTunes Specific
    itunes_author = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author")
    itunes_author.text = "kreggsmonde"
    
    # Owner info (REQUIRED for Spotify/Apple verification)
    itunes_owner = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}owner")
    ET.SubElement(itunes_owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}name").text = "kreggsmonde"
    ET.SubElement(itunes_owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}email").text = "kreggsmonde@gmail.com"
    
    itunes_category = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category")
    itunes_category.set("text", "Kids & Family")
    
    itunes_image = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image")
    itunes_image.set("href", f"{BASE_URL}/logo.jpg")
    
    return rss, channel

def add_episode_to_rss(channel, title, audio_filename, description, pub_date):
    """Adds a single episode (item) to the RSS channel."""
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "description").text = description
    
    # Audio Enclosure
    enclosure = ET.SubElement(item, "enclosure")
    enclosure.set("url", f"{BASE_URL}/{RECORDINGS_DIR}/{audio_filename}")
    enclosure.set("type", "audio/mpeg")
    # In a real scenario, we'd calculate the file size here
    enclosure.set("length", "1000000") 
    
    ET.SubElement(item, "guid").text = audio_filename
    ET.SubElement(item, "pubDate").text = pub_date

def update_feed():
    """Scans the recordings folder and builds/updates the RSS feed."""
    print("📡 Updating Podcast RSS Feed...")
    rss_root, channel = create_rss_shell()
    
    recordings_path = Path(__file__).parent / RECORDINGS_DIR
    audio_files = sorted(recordings_path.glob("*.mp3"), key=os.path.getmtime, reverse=True)
    
    for audio in audio_files:
        # Try to find matching story text for description
        story_file = audio.with_suffix(".txt").name.replace("podcast_episode_", "story_")
        story_path = recordings_path / story_file
        
        description = "Une nouvelle histoire passionnante."
        if story_path.exists():
            description = story_path.read_text(encoding='utf-8')[:300] + "..."
            
        title = f"Épisode: {audio.stem.replace('podcast_episode_', '')}"
        # Format date for RSS: Wed, 04 Feb 2026 19:00:00 +0000
        mod_time = datetime.fromtimestamp(audio.stat().st_mtime)
        pub_date = mod_time.strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        add_episode_to_rss(channel, title, audio.name, description, pub_date)
    
    # Save the file
    tree = ET.ElementTree(rss_root)
    ET.indent(tree, space="  ", level=0)
    tree.write(RSS_FILE, encoding="utf-8", xml_declaration=True)
    print(f"✅ RSS Feed updated: {RSS_FILE}")

if __name__ == "__main__":
    update_feed()
