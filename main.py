import os
import re
import datetime
import subprocess
import random
from pathlib import Path
from urllib.parse import quote
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# ---------------- CONFIG ----------------

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

# LANGUAGE SETTINGS (Change this for different languages)
LANGUAGE_CONFIG = {
    "name": "French",          # Language name for prompts
    "native_name": "en français",   # Native name for instructions
    "voice": "fr-FR-DeniseNeural", # Edge-TTS voice
    "vosk_model": "vosk-model-small-fr-0.22",
    "vosk_url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
    "vosk_zip": "vosk-model-fr.zip",
    "subtitle_font": "Arial"
}

# For German, you would just change to:
# LANGUAGE_CONFIG = {
#     "name": "German",
#     "native_name": "auf Deutsch",
#     "voice": "de-DE-KatjaNeural",
#     "vosk_model": "vosk-model-small-de-0.15", 
#     ...
# }

NUM_IMAGES = 8  # 8 unique scenes (faster generation)
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920
IMAGE_MODEL = "flux"

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
    
    # Nettoyer les anciennes images
    for f in IMAGES_DIR.glob("*.jpg"):
        f.unlink()
        
    # Nettoyer les anciens fichiers de sortie pour éviter les états résiduels
    for f in OUTPUT_DIR.glob("*"):
        if f.is_file() and f.name != ".gitkeep":
            try:
                f.unlink()
            except Exception:
                pass

def refill_topics():
    """Generate new topics when running low, preserving any remaining."""
    print("[sujets] ⚠️ Sujets presque épuisés! Génération de nouveaux sujets...")
    try:
        from generate_topics import generate_french_kids_topics, save_topics_to_file
        new_topics = generate_french_kids_topics(100)
        if new_topics:
            existing = []
            if os.path.exists(TOPICS_FILE):
                with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                    existing = [line.strip() for line in f if line.strip()]
            seen = set(t.lower() for t in existing)
            for t in new_topics:
                if t.lower() not in seen:
                    existing.append(t)
                    seen.add(t.lower())
            save_topics_to_file(existing, TOPICS_FILE)
            print(f"[sujets] ✅ {len(existing)} sujets ({len(new_topics)} nouveaux)")
            return True
    except Exception as e:
        print(f"[sujets] ❌ Échec auto-génération: {e}")
    return False

def choose_topic_for_today():
    if not os.path.exists(TOPICS_FILE):
        print(f"[sujets] {TOPICS_FILE} introuvable!")
        if not refill_topics():
            return "L'Aventure du Petit Animal Mignon"

    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]
    
    # Auto-générer si le pool devient bas (< 10 sujets)
    if len(topics) < 10:
        print(f"[sujets] ⚠️ Plus que {len(topics)} sujets. Régénération...")
        if refill_topics():
            with open(TOPICS_FILE, "r", encoding="utf-8") as f:
                topics = [line.strip() for line in f if line.strip()]
    
    if not topics:
        print("[sujets] Aucun sujet trouvé! Génération d'urgence...")
        if not refill_topics():
            return "Le Petit Ours dans la Forêt"
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
        if not topics:
            return "Le Petit Ours dans la Forêt"
    
    # 1. Sélectionner le premier sujet
    selected_topic = topics[0]
    print(f"[sujets] ✅ Sujet sélectionné: {selected_topic}")
    print(f"[sujets] 📊 Sujets restants dans topics.txt: {len(topics) - 1}")
    
    # 2. Sauvegarder dans l'historique des sujets utilisés
    try:
        with open("used_topics.txt", "a", encoding="utf-8") as f:
            f.write(f"{selected_topic}\n")
        print(f"[sujets] ✅ Sujet ajouté à used_topics.txt")
    except Exception as e:
        print(f"[sujets] ⚠️ Erreur lors de l'écriture dans used_topics.txt: {e}")
    
    # 3. Retirer de topics.txt (réécrire le fichier sans la première ligne)
    try:
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(topics[1:]) + "\n")
        print(f"[sujets] ✅ Sujet retiré de topics.txt")
    except Exception as e:
        print(f"[sujets] ⚠️ Erreur lors de la mise à jour de topics.txt: {e}")
    
    return selected_topic

def generate_story_with_pollinations(topic: str) -> str:
    """Générer une courte histoire pour enfants dans la langue cible."""
    
    lang_name = LANGUAGE_CONFIG["name"]
    
    # Prompt en anglais pour la génération d'histoire
    full_prompt = (
        f"Write a short children's story in {lang_name} language (ages 3-8) strictly about the topic: {topic}. "
        f"Do not change the animals or the subject. The story must be exactly about the title. "
        f"Length: 80-120 words. Simple language. Only the story content, no title."
    )

    # Utiliser l'API v1 compatible OpenAI pour plus de fiabilité
    url = "https://gen.pollinations.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a creative children's story author."},
            {"role": "user", "content": full_prompt}
        ]
    }

    print(f"[histoire] Génération de l'histoire ({lang_name}): {topic}")
    
    # Retry logic for story generation
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            text = data['choices'][0]['message']['content'].strip()

            words = text.split()
            
            # VALIDATION: Ensure minimum story length to prevent short videos
            if len(words) < 50:
                print(f"[histoire] ⚠️ Histoire trop courte ({len(words)} mots), nouvelle tentative {attempt + 1}/{max_retries}...")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise ValueError(f"Histoire trop courte après {max_retries} tentatives: {len(words)} mots")
            
            if len(words) > STORY_MAX_WORDS:
                text = " ".join(words[:STORY_MAX_WORDS])
                words = text.split()

            with open(STORY_FILE, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"[histoire] ✅ Histoire générée ({len(words)} mots)")
            return text
            
        except Exception as e:
            print(f"[histoire] ❌ Erreur tentative {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                # Secours avec une histoire minimale valide
                fallback = f"Il était une fois {topic}. C'était une belle journée. Les animaux jouaient ensemble dans la forêt. Ils étaient très heureux. Ils chantaient et dansaient. Le soleil brillait dans le ciel. Les oiseaux volaient partout. C'était merveilleux. Tous les amis s'amusaient beaucoup. Et ils vécurent heureux pour toujours."
                print(f"[histoire] ⚠️ Utilisation de l'histoire de secours")
                with open(STORY_FILE, "w", encoding="utf-8") as f:
                    f.write(fallback)
                return fallback

def generate_visual_prompts(story: str) -> list:
    """Générer 8 descriptions visuelles distinctes en ANGLAIS à partir de l'histoire."""
    print(f"[scènes] Génération de descriptions visuelles en anglais...")
    
    lang_name = LANGUAGE_CONFIG["name"]
    
    prompt = (
        f"Read this {lang_name} story: '{story}'\n"
        f"Generate exactly {NUM_IMAGES} detailed, visual image descriptions in ENGLISH based on this story. "
        f"Describe the animals, expressions, and environment clearly. "
        f"Make them cute and suitable for a 3D Pixar-style animation. "
        f"Output ONLY the {NUM_IMAGES} descriptions, one per line. No numbering."
    )

    # Utiliser l'API v1 compatible OpenAI
    url = "https://gen.pollinations.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a creative director for children's animation."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if r.status_code != 200:
             raise Exception(f"Erreur API: {r.status_code} - {r.text}")
             
        data = r.json()
        text = data['choices'][0]['message']['content'].strip()
        
        # Nettoyer les lignes
        lines = [line.strip().lstrip('0123456789.- ') for line in text.split('\n') if line.strip()]
        
        # S'assurer d'avoir exactement NUM_IMAGES
        if len(lines) < NUM_IMAGES:
            while len(lines) < NUM_IMAGES:
                lines.append(lines[-1] + " vue rapprochée" if lines else "Scène d'animal mignon")
        
        scenes = lines[:NUM_IMAGES]
        
    except Exception as e:
        print(f"[scènes] Erreur lors de la génération des prompts: {e}")
        scenes = ["Animal mignon dans la forêt"] * NUM_IMAGES

    # Sauvegarder les scènes
    with open(SCENES_FILE, "w", encoding="utf-8") as f:
        for i, scene in enumerate(scenes):
            f.write(f"{i+1}. {scene}\n")
    
    print(f"[scènes] {len(scenes)} descriptions visuelles créées")
    return scenes

def generate_image(scene: str, idx: int) -> Path:
    """Générer une image animée 3D de haute qualité pour chaque scène en utilisant Pollinations AI."""
    # Créer une graine unique pour chaque image basée sur le contenu de la scène + index
    seed = hash(scene + str(idx)) % 1000000
    
    # Prompt amélioré avec des instructions anti-déformation complètes
    prompt = (
        f"Professional 3D Pixar Disney animation style, ultra high quality 8K render, {scene}, "
        f"perfect symmetrical faces, flawless facial features, anatomically correct proportions, "
        f"cute adorable animal characters with correct anatomy, "
        f"professional character design, crystal clear details, "
        f"vibrant colorful children's book illustration, cinematic lighting, "
        f"magical forest atmosphere, child-friendly, happy joyful expression, "
        f"masterpiece quality, sharp focus, beautiful composition, "
        f"NEGATIVE PROMPT: deformed, disfigured, ugly, bad anatomy, "
        f"extra limbs, missing limbs, floating limbs, disconnected limbs, "
        f"mutated hands, poorly drawn hands, malformed hands, "
        f"poorly drawn face, mutation, deformed face, asymmetric face, "
        f"blurry, bad proportions, extra fingers, fused fingers, "
        f"too many fingers, cloned face, duplicate features, "
        f"disfigured, gross proportions, malformed limbs, "
        f"extra arms, extra legs, missing arms, missing legs, "
        f"deformed eyes, cross-eyed, misaligned eyes, extra eyes, "
        f"deformed mouth, extra mouth, bad teeth, "
        f"low quality, worst quality, low resolution, distorted"
    )
    safe_prompt = quote(prompt)
    
    # Inclure la graine pour garantir une image unique
    url = (
        f"https://gen.pollinations.ai/image/{safe_prompt}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&model={IMAGE_MODEL}&seed={seed}&nologo=true"
    )

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
    }

    out = IMAGES_DIR / f"scene_{idx:02d}.jpg"
    print(f"[image] Génération de l'image 3D {idx+1}/{NUM_IMAGES}: {scene[:50]}...")
    
    
    # Logique de nouvelle tentative avec backoff exponentiel (attentes plus longues pour les limites de taux)
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=headers, timeout=180)
            r.raise_for_status()
            out.write_bytes(r.content)
            time.sleep(2)  # Petit délai entre les requêtes réussies
            return out
        except requests.exceptions.HTTPError as e:
            # Gérer les limites de taux 429 avec des attentes beaucoup plus longues
            if e.response.status_code == 429:
                wait_time = (attempt + 1) * 20  # 20, 40, 60, 80, 100 secondes
                if attempt < max_retries - 1:
                    print(f"[image] Limite de taux atteinte! Tentative {attempt+1}/{max_retries} (attente {wait_time}s)")
                    time.sleep(wait_time)
                else:
                    print(f"[image] L'image {idx+1} n'a pas pu être générée: Limite de taux dépassée")
                    raise e
            else:
                wait_time = (attempt + 1) * 5
                if attempt < max_retries - 1:
                    print(f"[image] HTTP {e.response.status_code}. Tentative {attempt+1}/{max_retries} (attente {wait_time}s)")
                    time.sleep(wait_time)
                else:
                    print(f"[image] L'image {idx+1} n'a pas pu être générée: {e}")
                    raise e
        except Exception as e:
            wait_time = (attempt + 1) * 5
            if attempt < max_retries - 1:
                print(f"[image] Tentative {attempt+1}/{max_retries} (attente {wait_time}s)")
                time.sleep(wait_time)
            else:
                print(f"[image] L'image {idx+1} n'a pas pu être générée: {e}")
                raise e
    return out

def generate_images(scenes: list):
    """Générer des images animées 3D uniques pour chaque scène SÉQUENTIELLEMENT (évite les limites de taux)"""
    print(f"[image] Génération de {NUM_IMAGES} images 3D séquentiellement (éviter les limites de taux)...")
    return [generate_image(scene, i) for i, scene in enumerate(scenes)]

def generate_tts(story: str):
    """Générer la narration en utilisant edge-tts (TTS Microsoft gratuit)."""
    import asyncio
    try:
        import edge_tts
    except ImportError:
        subprocess.run(["pip", "install", "edge-tts"], check=True)
        import edge_tts
    
    lang_name = LANGUAGE_CONFIG["name"]
    voice = LANGUAGE_CONFIG["voice"]
    print(f"[tts] Génération de la narration ({lang_name}) avec edge-tts...")
    
    async def generate():
        communicate = edge_tts.Communicate(story, voice)
        await communicate.save(str(NARRATION_FILE))
    
    asyncio.run(generate())
    print(f"[tts] Narration sauvegardée dans {NARRATION_FILE}")

def generate_word_subtitles():
    """Générer des sous-titres MOT PAR MOT en utilisant Vosk (léger!)."""
    print("[sous-titres] Génération de sous-titres mot par mot avec Vosk...")
    
    import json
    import wave
    import subprocess
    import sys
    
    try:
        from vosk import Model, KaldiRecognizer
    except ImportError:
        print("[sous-titres] 'vosk' non trouvé, installation automatique...")
        subprocess.run([sys.executable, "-m", "pip", "install", "vosk"], check=True)
        from vosk import Model, KaldiRecognizer
    import os
    
    # Télécharger le modèle Vosk s'il n'existe pas
    model_name = LANGUAGE_CONFIG["vosk_model"]
    model_url = LANGUAGE_CONFIG["vosk_url"]
    zip_path = LANGUAGE_CONFIG["vosk_zip"]
    
    if not os.path.exists(model_name):
        print(f"[sous-titres] Téléchargement du modèle Vosk ({model_name})...")
        import urllib.request
        import zipfile
        
        urllib.request.urlretrieve(model_url, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        os.remove(zip_path)
        print("[sous-titres] Modèle téléchargé!")
    
    # Convert MP3 to WAV for Vosk
    wav_file = "output/narration.wav"
    os.system(f'ffmpeg -y -i {NARRATION_FILE} -ar 16000 -ac 1 {wav_file}')
    
    # Load Vosk model
    model = Model(model_name)
    
    # Open WAV file
    wf = wave.open(wav_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)  # Enable word-level timestamps
    
    # Process audio
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
    
    # Final result
    final_result = json.loads(rec.FinalResult())
    if 'result' in final_result:
        for word_info in final_result['result']:
            words.append({
                'word': word_info['word'].upper(),
                'start': word_info['start'],
                'end': word_info['end']
            })
    
    font_name = LANGUAGE_CONFIG.get("subtitle_font", "Arial")
    
    # Create ASS subtitle file with kid-friendly styling
    ass_content = f"""[Script Info]
Title: Children's Story
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
    
    # Save ASS file
    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"[sous-titres] Sous-titres sauvegardés ({len(words)} mots)")

def get_audio_duration(audio_file):
    """Obtenir la durée du fichier audio en utilisant ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_animated_slideshow(image_paths):
    """Créer un diaporama animé avec effet de zoom Ken Burns."""
    print("[vidéo] Création d'un diaporama animé avec effet Ken Burns...")
    
    # Obtenir la durée audio pour correspondre à la longueur de la vidéo
    duration = get_audio_duration(NARRATION_FILE)
    per_image = duration / len(image_paths)
    
    # Créer des clips animés individuels avec effet de zoom
    clips = []
    for i, img_path in enumerate(image_paths):
        clip_file = OUTPUT_DIR / f"clip_{i:02d}.mp4"
        clips.append(clip_file)
        
        # Calculer les images (30 fps)
        frames = max(int(per_image * 30), 60)
        
        # Alterner entre zoom avant et zoom arrière pour la variété
        if i % 2 == 0:
            # Effet de zoom avant
            zoom_start = 1.0
            zoom_end = 1.3
        else:
            # Effet de zoom arrière  
            zoom_start = 1.3
            zoom_end = 1.0
        
        # Zoom simple avec filtre d'échelle (plus fiable sur Windows)
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
            "-preset", "slow",  # Meilleure qualité
            "-crf", "18",  # Haute qualité (plus bas = meilleur, 18-23 est bon)
            "-pix_fmt", "yuv420p",
            str(clip_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[vidéo] Le zoom pour le clip {i+1} a échoué, utilisation de secours...")
            # Secours: simple statique avec léger mouvement
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
        
        print(f"[vidéo] Clip animé {i+1}/{len(image_paths)}")
    
    # Créer la liste de concaténation
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")
    
    # Concaténer tous les clips
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(ANIMATED_VIDEO)
    ]
    subprocess.run(cmd, check=True)
    print(f"[vidéo] Diaporama animé sauvegardé dans {ANIMATED_VIDEO}")
    
    # Nettoyer les clips individuels
    for clip in clips:
        if clip.exists():
            clip.unlink()

def add_subtitles():
    """Superposer les sous-titres ASS sur la vidéo."""
    print("[vidéo] Ajout de sous-titres en MAJUSCULES...")
    
    # Le chemin Windows nécessite une gestion spéciale pour le filtre FFmpeg
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
    print(f"[vidéo] Vidéo avec sous-titres sauvegardée dans {VIDEO_WITH_SUBS}")

def merge_audio():
    """Fusionner la vidéo avec la narration et la musique de fond."""
    print("[fusion] Fusion de l'audio avec la musique de fond...")
    
    if MUSIC_FILE.exists():
        # Fusionner narration + musique de fond (musique à volume inférieur)
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
        print("[fusion] Aucun music.mp3 trouvé, utilisation de la narration uniquement")
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
    print(f"[fusion] Vidéo finale sauvegardée dans {FINAL_VIDEO}")

def main():
    ensure_dirs()

    topic = choose_topic_for_today()
    print("=" * 60)
    print(f"=== Sujet: {topic}")
    print("=" * 60)

    # 1. Générer l'histoire avec Pollinations AI
    story = generate_story_with_pollinations(topic)
    
    # 2. Générer des prompts visuels détaillés en ANGLAIS à partir de l'histoire
    scenes = generate_visual_prompts(story)
    
    # 3. Générer des images uniques pour chaque scène
    images = generate_images(scenes)

    # 4. Générer la narration avec TTS
    generate_tts(story)
    
    # VALIDATION: Check audio duration to prevent short videos
    audio_duration = get_audio_duration(NARRATION_FILE)
    print(f"[validation] 🎵 Durée audio: {audio_duration:.2f} secondes")
    
    if audio_duration < 10:
        raise ValueError(f"❌ Audio trop court ({audio_duration:.2f}s)! Minimum 10 secondes requis. Vérifiez la génération de l'histoire et du TTS.")
    
    print(f"[validation] ✅ Durée audio valide ({audio_duration:.2f}s)")
    
    # 5. Générer des sous-titres en MAJUSCULES au niveau des mots avec Whisper
    generate_word_subtitles()
    
    # 6. Créer un diaporama animé avec effet Ken Burns
    create_animated_slideshow(images)
    
    # 7. Ajouter la superposition de sous-titres
    add_subtitles()
    
    # 8. Fusionner l'audio (narration + musique de fond)
    merge_audio()

    print("=" * 60)
    print(f"✅ TERMINÉ. Vidéo prête: {FINAL_VIDEO}")
    print(f"📊 Durée finale: {audio_duration:.2f} secondes")
    print("=" * 60)


if __name__ == "__main__":
    main()
