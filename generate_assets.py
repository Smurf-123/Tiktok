"""
Erzeugt die visuellen und akustischen Bausteine für das Video:
- Bilder über Pollinations.ai (kostenlose Bild-API, kein Key nötig)
- Sprachausgabe über edge-tts (nutzt Microsofts kostenlose Edge-Stimmen)
"""
import os
import asyncio
import requests
import edge_tts
from urllib.parse import quote
from config import TTS_VOICE, OUTPUT_DIR

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true"


def generate_images(image_prompts: list[str], out_dir: str) -> list[str]:
    """Lädt für jeden Prompt ein Bild von Pollinations.ai herunter."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, prompt in enumerate(image_prompts):
        url = POLLINATIONS_URL.format(prompt=quote(prompt))
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        path = os.path.join(out_dir, f"image_{i:02d}.jpg")
        with open(path, "wb") as f:
            f.write(response.content)
        paths.append(path)
    return paths


async def _generate_speech(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(out_path)


def generate_voiceover(script_text: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "voiceover.mp3")
    asyncio.run(_generate_speech(script_text, out_path))
    return out_path


if __name__ == "__main__":
    test_prompts = ["a misty mountain at sunrise, cinematic", "aerial view of a river delta"]
    imgs = generate_images(test_prompts, os.path.join(OUTPUT_DIR, "test"))
    print("Bilder:", imgs)
    audio = generate_voiceover("Das ist ein Test der Sprachausgabe.", os.path.join(OUTPUT_DIR, "test"))
    print("Audio:", audio)
