"""
Hauptskript: prüft neue Videos -> fasst zusammen -> erzeugt Bilder+Stimme
-> baut Video -> lädt auf TikTok hoch -> merkt sich verarbeitete Videos.

Wird von GitHub Actions per Zeitplan aufgerufen (siehe .github/workflows/).
"""
import os
import sys
import traceback

from check_new_videos import find_new_videos, save_state
from summarize import summarize_video
from generate_assets import generate_images, generate_voiceover
from build_video import build_video
from upload_tiktok import refresh_access_token, upload_video
from config import OUTPUT_DIR


def process_video(video: dict, gemini_key: str) -> str:
    print(f"Verarbeite: {video['title']}")

    summary = summarize_video(video["video_id"], gemini_key)
    print(f"  Titel: {summary['title']}")

    work_dir = os.path.join(OUTPUT_DIR, video["video_id"])
    images = generate_images(summary["image_prompts"], work_dir)
    audio = generate_voiceover(summary["script"], work_dir)

    out_path = os.path.join(work_dir, "final.mp4")
    build_video(images, audio, summary["script"], out_path)

    return out_path, summary["title"]


def main():
    gemini_key = os.environ["GEMINI_API_KEY"]

    # TikTok-Upload ist optional: nur wenn alle drei Variablen gesetzt sind,
    # sonst wird das Video nur lokal erzeugt (nützlich zum Testen).
    tiktok_ready = all(k in os.environ for k in
                        ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"])

    new_videos, state = find_new_videos()
    if not new_videos:
        print("Keine neuen Videos. Fertig.")
        return

    # Nur das erste neue Video verarbeiten (1 Video pro Lauf reicht für "1x täglich")
    video = new_videos[0]

    try:
        video_path, title = process_video(video, gemini_key)
        print(f"Video erstellt: {video_path}")

        if tiktok_ready:
            access_token = refresh_access_token(
                os.environ["TIKTOK_CLIENT_KEY"],
                os.environ["TIKTOK_CLIENT_SECRET"],
                os.environ["TIKTOK_REFRESH_TOKEN"],
            )
            publish_id = upload_video(video_path, title, access_token,
                                       privacy_level=os.environ.get("TIKTOK_PRIVACY", "SELF_ONLY"))
            print(f"Auf TikTok hochgeladen, publish_id: {publish_id}")
        else:
            print("TikTok-Zugangsdaten fehlen -> Video wurde nur lokal erzeugt, nicht hochgeladen.")

        # Als verarbeitet markieren, damit es nicht nochmal läuft
        state["processed_ids"].append(video["video_id"])
        save_state(state)

    except Exception:
        print("FEHLER bei der Verarbeitung:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
