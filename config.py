"""
Zentrale Konfiguration. Passe hier die Kanäle und Grundeinstellungen an.
Alle Secrets (API-Keys) kommen NICHT hierher, sondern aus Umgebungsvariablen
(siehe README.md -> GitHub Secrets).
"""

# YouTube-Kanäle, die als Themen-Quelle dienen (KEIN Video-Reupload!).
# Nutze die Kanal-ID (beginnt mit UC...). So findest du sie:
# -> Kanal-Seite öffnen -> Seitenquelltext -> nach "channelId" suchen
# oder https://commentpicker.com/youtube-channel-id.php nutzen.
SOURCE_CHANNELS = {
    "dw_documentary": "UCEkjqEIDpXvpTNPKMFypDbQ",  # DW Documentary
}

# Wie viele Sekunden soll das fertige Video ungefähr lang sein
TARGET_VIDEO_SECONDS = 55

# Wie viele KI-Bilder sollen für ein Video generiert werden
NUM_IMAGES = 6

# Edge-TTS Stimme (kostenlos). Deutsche Stimmen: de-DE-KatjaNeural, de-DE-ConradNeural
# Englische Stimmen: en-US-AriaNeural, en-US-GuyNeural
TTS_VOICE = "de-DE-KatjaNeural"

# Gemini-Modell für die Zusammenfassung (kostenloses Kontingent)
GEMINI_MODEL = "gemini-2.0-flash"

# Datei, in der bereits verarbeitete Video-IDs gespeichert werden,
# damit nichts doppelt verarbeitet wird.
STATE_FILE = "processed_videos.json"

# Ausgabeordner für die fertigen Videos
OUTPUT_DIR = "output"
