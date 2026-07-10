"""
Prüft die konfigurierten YouTube-Kanäle per RSS-Feed auf neue Videos.
Braucht KEINEN API-Key. Gibt eine Liste neuer (noch nicht verarbeiteter)
Videos zurück und aktualisiert die State-Datei.
"""
import json
import os
import feedparser
from config import SOURCE_CHANNELS, STATE_FILE

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_ids": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_latest_video(channel_id: str):
    """Holt das neueste Video eines Kanals über dessen RSS-Feed."""
    feed = feedparser.parse(RSS_URL.format(channel_id=channel_id))
    if not feed.entries:
        return None
    entry = feed.entries[0]
    return {
        "video_id": entry.yt_videoid,
        "title": entry.title,
        "url": entry.link,
        "published": entry.published,
    }


def find_new_videos():
    state = load_state()
    new_videos = []

    for source_name, channel_id in SOURCE_CHANNELS.items():
        latest = get_latest_video(channel_id)
        if latest and latest["video_id"] not in state["processed_ids"]:
            latest["source_name"] = source_name
            new_videos.append(latest)

    return new_videos, state


if __name__ == "__main__":
    videos, _ = find_new_videos()
    if videos:
        print(f"{len(videos)} neue(s) Video(s) gefunden:")
        for v in videos:
            print(f"  - [{v['source_name']}] {v['title']} ({v['url']})")
    else:
        print("Keine neuen Videos gefunden.")
