"""
Holt das Transkript eines YouTube-Videos und lässt Gemini daraus ein
EIGENSTÄNDIGES TikTok-Skript in eigenen Worten erstellen (keine Kopie/
Paraphrase des Originalskripts, sondern eine echte Neuformulierung der
Fakten für ein kurzes Format).
"""
import os
import json
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from config import GEMINI_MODEL, NUM_IMAGES

SYSTEM_PROMPT = """Du bist Redakteur für einen TikTok-Wissenskanal.
Du bekommst das rohe Transkript eines Dokumentarfilms. Deine Aufgabe:

1. Identifiziere EIN interessantes Kernthema/Faktum aus dem Transkript.
2. Schreibe dazu ein KOMPLETT NEUES, eigenständiges Skript (ca. 45-60 Sekunden
   Sprechzeit, ca. 120-150 Wörter), das die Fakten in DEINEN EIGENEN Worten
   wiedergibt. NICHT Sätze aus dem Original übernehmen oder eng umschreiben,
   sondern die Information komplett neu und eigenständig formulieren.
3. Schreibe im gesprochenen, lockeren TikTok-Stil (kurze Sätze, Hook am Anfang).
4. Erstelle zusätzlich {num_images} kurze Bildbeschreibungen (auf Englisch,
   für einen Bildgenerator), die den Text visuell begleiten.

Antworte NUR mit validem JSON in diesem Format, ohne Markdown-Codeblock:
{{
  "title": "Kurzer TikTok-Titel",
  "script": "Das vollständige Sprechskript",
  "image_prompts": ["prompt 1", "prompt 2", ...]
}}
"""


def get_transcript_text(video_id: str) -> str:
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id, languages=["de", "en"])
    return " ".join(snippet.text for snippet in fetched)


def summarize_video(video_id: str, api_key: str) -> dict:
    client = genai.Client(api_key=api_key)

    transcript_text = get_transcript_text(video_id)
    transcript_text = transcript_text[:15000]

    prompt = SYSTEM_PROMPT.format(num_images=NUM_IMAGES) + "\n\nTranskript:\n" + transcript_text
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)


if __name__ == "__main__":
    import sys
    video_id = sys.argv[1]
    api_key = os.environ["GEMINI_API_KEY"]
    result = summarize_video(video_id, api_key)
    print(json.dumps(result, indent=2, ensure_ascii=False))
