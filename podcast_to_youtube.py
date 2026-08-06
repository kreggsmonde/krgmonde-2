import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from upload_to_youtube import upload_to_youtube

def create_podcast_video(audio_path: Path, image_path: Path, output_path: Path):
    """Combines a static image and audio into a video for YouTube."""
    print(f"🎬 Creating video for YouTube: {output_path.name}")
    
    # ffmpeg command to loop the image and add the audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Video created: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Video creation failed: {e.stderr.decode()}")
        return False

def upload_podcast_to_youtube(video_path: Path, title: str, description: str):
    """Uploads the generated video to YouTube."""
    print(f"📺 Uploading podcast to YouTube: {title}")
    
    tags = ["French", "Podcast", "Children Stories", "Learn French", "Storytime"]
    
    try:
        result = upload_to_youtube(video_path, title, description, tags)
        if result:
            print(f"✅ YouTube Upload Success! Video ID: {result.get('id')}")
            return result
    except Exception as e:
        print(f"❌ YouTube Upload Failed: {e}")
        return None

def process_latest_podcast():
    """Finds the latest recording and uploads it to YouTube."""
    recordings_dir = Path(__file__).parent / "recordings"
    
    # Find latest mp3
    audio_files = sorted(recordings_dir.glob("*.mp3"), key=os.path.getmtime, reverse=True)
    if not audio_files:
        print("❌ No podcast recordings found.")
        return
    
    latest_audio = audio_files[0]
    filename_prefix = latest_audio.stem
    latest_image = latest_audio.with_suffix(".jpg")
    latest_story = latest_audio.with_suffix(".txt").name.replace("podcast_episode_", "story_")
    story_path = recordings_dir / latest_story
    
    if not latest_image.exists():
        print(f"❌ Matching image not found for {latest_audio.name}")
        return
        
    output_video = recordings_dir / f"{filename_prefix}_youtube.mp4"
    
    # 1. Create Video
    if create_podcast_video(latest_audio, latest_image, output_video):
        # 2. Extract Title and Description
        description = "Un nouvel episode de psychologie et developpement personnel en francais."
        if story_path.exists():
            description = story_path.read_text(encoding='utf-8')
        
        title = f"Podcast Français: {latest_audio.stem.replace('podcast_episode_', '')}"
        
        # 3. Upload
        upload_podcast_to_youtube(output_video, title, description)

if __name__ == "__main__":
    process_latest_podcast()
