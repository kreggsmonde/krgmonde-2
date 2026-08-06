import os
import re
import datetime
import subprocess
import random
import json
from pathlib import Path
from urllib.parse import quote
import requests
import time
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------- CONFIG ----------------

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

LANGUAGE_CONFIG = {
    "name": "French",
    "native_name": "en français",
    "voice": "fr-FR-DeniseNeural",
    "vosk_model": "vosk-model-small-fr-0.22",
    "vosk_url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
    "vosk_zip": "vosk-model-fr.zip",
    "subtitle_font": "Arial"
}

NUM_IMAGES = 8
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920

STORY_MAX_WORDS = 130

TOPICS_FILE = "topics.txt"

IMAGES_DIR = Path("images")
OUTPUT_DIR = Path("output")
AUDIO_DIR = Path("audio")

MUSIC_FILE = AUDIO_DIR / "music.mp3"

NARRATION_FILE = OUTPUT_DIR / "narration.mp3"
STORY_FILE = OUTPUT_DIR / "story.txt"
SCENES_FILE = OUTPUT_DIR / "scenes.txt"
SUBS_FILE = OUTPUT_DIR / "subtitles.ass"
ANIMATED_VIDEO = OUTPUT_DIR / "animated.mp4"
VIDEO_WITH_SUBS = OUTPUT_DIR / "video_with_subs.mp4"
FINAL_VIDEO = OUTPUT_DIR / "final_video.mp4"

WHISPER_MODEL_NAME = "small"

# ----------------------------------------

def ensure_dirs():
    IMAGES_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)

    for f in IMAGES_DIR.glob("*.jpg"):
        f.unlink()

    for f in OUTPUT_DIR.glob("*"):
        if f.is_file() and f.name != ".gitkeep":
            try:
                f.unlink()
            except Exception:
                pass

def choose_topic_for_today():
    if not os.path.exists(TOPICS_FILE):
        print(f"[topics] {TOPICS_FILE} not found!")
        return "La puissance de la gratitude au quotidien"

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]
    if not topics:
        print("[topics] No topics found! Using fallback.")
        return "Les petites habitudes qui changent tout"

    selected_topic = topics[0]
    print(f"[topics] Topic selected: {selected_topic}")
    print(f"[topics] Remaining in topics.txt: {len(topics) - 1}")

    try:
        with open("used_topics.txt", "a", encoding="utf-8") as f:
            f.write(f"{selected_topic}\n")
    except Exception as e:
        print(f"[topics] Warning writing used_topics.txt: {e}")

    try:
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(topics[1:]) + "\n")
    except Exception as e:
        print(f"[topics] Warning updating topics.txt: {e}")

    return selected_topic

def generate_story_with_pollinations(topic: str) -> str:
    """Generate a short psychology/self-improvement story in French."""
    lang_name = LANGUAGE_CONFIG["name"]

    full_prompt = (
        f"Write a short inspiring story in {lang_name} about psychology and self-improvement, "
        f"strictly on the topic: {topic}. "
        f"Do not change the topic. The story must be exactly about the title. "
        f"Include practical advice or a life lesson. "
        f"Length: 80-120 words. Simple language. Only the story content, no title."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a psychology and self-improvement author writing in French."},
            {"role": "user", "content": full_prompt}
        ]
    }

    print(f"[story] Generating story ({lang_name}): {topic}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            text = data['choices'][0]['message']['content'].strip()
            words = text.split()

            if len(words) < 50:
                print(f"[story] Story too short ({len(words)} words), retry {attempt + 1}/{max_retries}...")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise ValueError(f"Story too short after {max_retries} retries: {len(words)} words")

            if len(words) > STORY_MAX_WORDS:
                text = " ".join(words[:STORY_MAX_WORDS])
                words = text.split()

            with open(STORY_FILE, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"[story] Story generated ({len(words)} words)")
            return text

        except Exception as e:
            print(f"[story] Error attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                fallback = (
                    f"Chaque jour, nous avons le choix de prendre soin de nous-meme. {topic}. "
                    f"La reussite commence par de petites actions quotidiennes. "
                    f"En cultivant une attitude positive, nous transformons notre vie. "
                    f"Le secret est la persistance et la confiance en soi. "
                    f"Croyez en vous, et le reste suivra."
                )
                print(f"[story] Using fallback story")
                with open(STORY_FILE, "w", encoding="utf-8") as f:
                    f.write(fallback)
                return fallback

def generate_visual_prompts(story: str) -> list:
    """Generate 8 visual descriptions in English from the story."""
    print(f"[scenes] Generating visual prompts in English...")

    prompt = (
        f"Read this French story: '{story}'\n"
        f"Generate exactly {NUM_IMAGES} detailed, visual image descriptions in ENGLISH based on this story. "
        f"Describe stickman-style characters, expressions, and environments clearly. "
        f"Make them suitable for a simple animation. "
        f"Output ONLY the {NUM_IMAGES} descriptions, one per line. No numbering."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a creative director for animation."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            raise Exception(f"API Error: {r.status_code} - {r.text}")
        data = r.json()
        text = data['choices'][0]['message']['content'].strip()
        lines = [line.strip().lstrip('0123456789.- ') for line in text.split('\n') if line.strip()]
        if len(lines) < NUM_IMAGES:
            while len(lines) < NUM_IMAGES:
                lines.append(lines[-1] + " close-up" if lines else "Stickman scene")
        scenes = lines[:NUM_IMAGES]
    except Exception as e:
        print(f"[scenes] Error generating prompts: {e}")
        scenes = ["Stickman in a calm environment"] * NUM_IMAGES

    with open(SCENES_FILE, "w", encoding="utf-8") as f:
        for i, scene in enumerate(scenes):
            f.write(f"{i+1}. {scene}\n")

    print(f"[scenes] {len(scenes)} visual descriptions created")
    return scenes

def download_image_from_drive(idx: int) -> Path:
    """Pick a random stickman image from Google Drive folder (weighted by least-used)."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    out = IMAGES_DIR / f"scene_{idx:02d}.jpg"

    service_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    folder_id = os.environ.get(
        "GOOGLE_DRIVE_FOLDER_ID",
        "1E9NZSg5Ef-bcRIwMVcrJ-KsrmG0R1Zgv",
    ).strip().strip('"').strip("'")
    if not service_key:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY environment variable required")
    if not folder_id:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID environment variable required")

    cred = service_account.Credentials.from_service_account_info(
        json.loads(service_key), scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=cred)

    all_files = []
    page_token = None
    while True:
        r = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/'",
            fields="files(id, name)", pageSize=200, pageToken=page_token
        ).execute()
        all_files.extend(r.get("files", []))
        page_token = r.get("nextPageToken")
        if not page_token:
            break

    if not all_files:
        raise RuntimeError(f"No image files found in Google Drive folder: {folder_id}")

    used_log = Path("used_images.json")
    usage = {}
    if used_log.exists():
        try:
            usage = json.loads(used_log.read_text())
        except Exception:
            usage = {}

    for f in all_files:
        if f["name"] not in usage:
            usage[f["name"]] = 0

    min_usage = min(usage.values())
    weights = [1.0 / (usage[f["name"]] - min_usage + 1) for f in all_files]
    chosen = random.choices(all_files, weights=weights, k=1)[0]
    usage[chosen["name"]] += 1
    used_log.write_text(json.dumps(usage, indent=2))

    print(f"[image] Loading image from Google Drive: {chosen['name']} ...", flush=True)
    request = service.files().get_media(fileId=chosen["id"])
    from googleapiclient.http import MediaIoBaseDownload
    import io
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    out.write_bytes(fh.read())
    print(f"  Saved: {out.name} ({out.stat().st_size // 1024} KB)", flush=True)
    return out

def generate_image(scene: str, idx: int) -> Path:
    """Pick image randomly from Google Drive instead of AI generation."""
    return download_image_from_drive(idx)

def generate_images(scenes: list):
    """Download random images from Google Drive for each scene."""
    print(f"[image] Downloading {NUM_IMAGES} random images from Google Drive...")
    return [generate_image(scene, i) for i, scene in enumerate(scenes)]

def generate_tts(story: str):
    """Generate narration using edge-tts (free Microsoft TTS)."""
    import asyncio
    try:
        import edge_tts
    except ImportError:
        subprocess.run(["pip", "install", "edge-tts"], check=True)
        import edge_tts

    lang_name = LANGUAGE_CONFIG["name"]
    voice = LANGUAGE_CONFIG["voice"]
    print(f"[tts] Generating narration ({lang_name}) with edge-tts...")

    async def generate():
        communicate = edge_tts.Communicate(story, voice)
        await communicate.save(str(NARRATION_FILE))

    asyncio.run(generate())
    print(f"[tts] Narration saved to {NARRATION_FILE}")

def generate_word_subtitles():
    """Generate word-by-word subtitles using Vosk."""
    print("[subtitles] Generating word-by-word subtitles with Vosk...")

    import json
    import wave
    import subprocess
    import sys

    try:
        from vosk import Model, KaldiRecognizer
    except ImportError:
        print("[subtitles] 'vosk' not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "vosk"], check=True)
        from vosk import Model, KaldiRecognizer
    import os

    model_name = LANGUAGE_CONFIG["vosk_model"]
    model_url = LANGUAGE_CONFIG["vosk_url"]
    zip_path = LANGUAGE_CONFIG["vosk_zip"]

    if not os.path.exists(model_name):
        print(f"[subtitles] Downloading Vosk model ({model_name})...")
        import urllib.request
        import zipfile
        urllib.request.urlretrieve(model_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(zip_path)
        print("[subtitles] Model downloaded!")

    wav_file = "output/narration.wav"
    os.system(f'ffmpeg -y -i {NARRATION_FILE} -ar 16000 -ac 1 {wav_file}')

    model = Model(model_name)
    wf = wave.open(wav_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    words = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if 'result' in result:
                for word_info in result['result']:
                    words.append({
                        'word': word_info['word'].upper(),
                        'start': word_info['start'],
                        'end': word_info['end']
                    })

    final_result = json.loads(rec.FinalResult())
    if 'result' in final_result:
        for word_info in final_result['result']:
            words.append({
                'word': word_info['word'].upper(),
                'start': word_info['start'],
                'end': word_info['end']
            })

    font_name = LANGUAGE_CONFIG.get("subtitle_font", "Arial")

    ass_content = f"""[Script Info]
Title: Psychology & Self-Improvement
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},20,&H00FFFF00,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,5,10,10,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    for word in words:
        start = word['start']
        end = word['end']
        text = word['word']
        start_time = f"{int(start//3600)}:{int((start%3600)//60):02d}:{start%60:.2f}"
        end_time = f"{int(end//3600)}:{int((end%3600)//60):02d}:{end%60:.2f}"
        ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"

    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        f.write(ass_content)

    print(f"[subtitles] Subtitles saved ({len(words)} words)")

def get_audio_duration(audio_file):
    """Get audio duration using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_animated_slideshow(image_paths):
    """Create animated slideshow with Ken Burns zoom effect."""
    print("[video] Creating animated slideshow with Ken Burns effect...")

    duration = get_audio_duration(NARRATION_FILE)
    per_image = duration / len(image_paths)

    clips = []
    for i, img_path in enumerate(image_paths):
        clip_file = OUTPUT_DIR / f"clip_{i:02d}.mp4"
        clips.append(clip_file)

        frames = max(int(per_image * 30), 60)

        if i % 2 == 0:
            zoom_start = 1.0
            zoom_end = 1.3
        else:
            zoom_start = 1.3
            zoom_end = 1.0

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", (
                f"scale=8000:-1,"
                f"zoompan=z='if(lte(on,1),{zoom_start},{zoom_start}+(({zoom_end}-{zoom_start})/{frames})*on)':"
                f"d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={IMAGE_WIDTH}x{IMAGE_HEIGHT}:fps=30"
            ),
            "-t", str(per_image),
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(clip_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[video] Zoom for clip {i+1} failed, using fallback...")
            cmd_fallback = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", str(img_path),
                "-vf", f"scale={IMAGE_WIDTH}:{IMAGE_HEIGHT}:force_original_aspect_ratio=increase,crop={IMAGE_WIDTH}:{IMAGE_HEIGHT},fps=30",
                "-t", str(per_image),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                str(clip_file)
            ]
            subprocess.run(cmd_fallback, check=True, capture_output=True)

        print(f"[video] Animated clip {i+1}/{len(image_paths)}")

    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(ANIMATED_VIDEO)
    ]
    subprocess.run(cmd, check=True)
    print(f"[video] Animated slideshow saved to {ANIMATED_VIDEO}")

    for clip in clips:
        if clip.exists():
            clip.unlink()

def add_subtitles():
    """Overlay ASS subtitles on video."""
    print("[video] Adding UPPERCASE subtitles...")

    subs_path = str(SUBS_FILE.resolve()).replace("\\", "/").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(ANIMATED_VIDEO),
        "-vf", f"ass='{subs_path}'",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(VIDEO_WITH_SUBS)
    ]
    subprocess.run(cmd, check=True)
    print(f"[video] Video with subtitles saved to {VIDEO_WITH_SUBS}")

def merge_audio():
    """Merge video with narration and background music."""
    print("[merge] Merging audio with background music...")

    if MUSIC_FILE.exists():
        cmd = [
            "ffmpeg", "-y",
            "-i", str(VIDEO_WITH_SUBS),
            "-i", str(NARRATION_FILE),
            "-i", str(MUSIC_FILE),
            "-filter_complex", "[2:a]volume=0.25[bg];[1:a][bg]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-shortest",
            "-c:v", "copy",
            str(FINAL_VIDEO)
        ]
    else:
        print("[merge] No music.mp3 found, using narration only")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(VIDEO_WITH_SUBS),
            "-i", str(NARRATION_FILE),
            "-map", "0:v",
            "-map", "1:a",
            "-shortest",
            "-c:v", "copy",
            str(FINAL_VIDEO)
        ]

    subprocess.run(cmd, check=True)
    print(f"[merge] Final video saved to {FINAL_VIDEO}")

def main():
    ensure_dirs()

    topic = choose_topic_for_today()
    print("=" * 60)
    print(f"=== Topic: {topic}")
    print("=" * 60)

    story = generate_story_with_pollinations(topic)

    scenes = generate_visual_prompts(story)

    images = generate_images(scenes)

    generate_tts(story)

    audio_duration = get_audio_duration(NARRATION_FILE)
    print(f"[validation] Audio duration: {audio_duration:.2f} seconds")

    if audio_duration < 10:
        raise ValueError(f"Audio too short ({audio_duration:.2f}s)! Minimum 10 seconds required.")

    print(f"[validation] Valid audio duration ({audio_duration:.2f}s)")

    generate_word_subtitles()

    create_animated_slideshow(images)

    add_subtitles()

    merge_audio()

    print("=" * 60)
    print(f"DONE. Video ready: {FINAL_VIDEO}")
    print(f"Final duration: {audio_duration:.2f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    main()
