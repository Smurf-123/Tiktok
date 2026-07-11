"""
Veröffentlicht ein lokales Video über die offizielle TikTok Content Posting API.

WICHTIG - einmaliger manueller Schritt vorab:
TikTok erfordert pro Konto einen OAuth-Login (kann nicht automatisiert werden,
da du dabei im Browser "Erlauben" klicken musst). Danach bekommst du ein
Access- und Refresh-Token, die du EINMALIG in GitHub Secrets einträgst.
Dieses Skript erneuert das Access-Token danach selbstständig über das
Refresh-Token (das 1 Jahr gültig ist).

Solange deine App noch nicht von TikTok freigegeben ("audited") ist, werden
alle Posts automatisch auf "Nur privat sichtbar" gesetzt. Das ist normal.
"""
import os
import time
import requests

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> str:
    response = requests.post(TOKEN_URL, data={
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    response.raise_for_status()
    return response.json()["access_token"]


def upload_video(video_path: str, title: str, access_token: str, privacy_level: str = "SELF_ONLY"):
    """
    privacy_level: SELF_ONLY (privat, Standard solange App nicht auditiert ist),
    PUBLIC_TO_EVERYONE (erst nach TikTok-App-Review möglich).
    """
    video_size = os.path.getsize(video_path)
    chunk_size = video_size

    init_payload = {
        "post_info": {
            "title": title,
            "privacy_level": privacy_level,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": 1,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    init_response = requests.post(INIT_URL, json=init_payload, headers=headers)
    init_response.raise_for_status()
    init_data = init_response.json()["data"]
    publish_id = init_data["publish_id"]
    upload_url = init_data["upload_url"]

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    put_headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
    }
    put_response = requests.put(upload_url, data=video_bytes, headers=put_headers)
    put_response.raise_for_status()

    return publish_id


def check_status(publish_id: str, access_token: str):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    response = requests.post(STATUS_URL, json={"publish_id": publish_id}, headers=headers)
    response.raise_for_status()
    return response.json()["data"]


if __name__ == "__main__":
    import sys
    video_path = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "Neues Video"

    access_token = refresh_access_token(
        os.environ["TIKTOK_CLIENT_KEY"],
        os.environ["TIKTOK_CLIENT_SECRET"],
        os.environ["TIKTOK_REFRESH_TOKEN"],
    )
    publish_id = upload_video(video_path, title, access_token)
    print(f"Hochgeladen, publish_id: {publish_id}")

    time.sleep(5)
    print(check_status(publish_id, access_token))
