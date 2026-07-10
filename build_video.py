"""
Baut aus den generierten Bildern + der Sprachausgabe ein fertiges,
TikTok-taugliches Video (1080x1920, mit eingebrannten Untertiteln).
Braucht ffmpeg (auf GitHub Actions per apt vorinstallierbar, siehe workflow).
"""
import os
import json
import subprocess
import textwrap


def get_audio_duration(audio_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def build_srt(script_text: str, duration: float, out_path: str, chunk_words: int = 6):
    words = script_text.split()
    chunks = [" ".join(words[i:i + chunk_words]) for i in range(0, len(words), chunk_words)]
    if not chunks:
        chunks = [script_text]

    per_chunk = duration / len(chunks)

    def fmt(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

    with open(out_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            start = i * per_chunk
            end = (i + 1) * per_chunk
            f.write(f"{i+1}\n{fmt(start)} --> {fmt(end)}\n{chunk}\n\n")


def build_video(image_paths: list[str], audio_path: str, script_text: str, out_path: str):
    work_dir = os.path.dirname(out_path)
    os.makedirs(work_dir, exist_ok=True)

    duration = get_audio_duration(audio_path)
    per_image = duration / len(image_paths)

    # Bilderliste für ffmpeg concat demuxer erzeugen
    list_path = os.path.join(work_dir, "images.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for img in image_paths:
            abs_img = os.path.abspath(img)
            f.write(f"file '{abs_img}'\nduration {per_image:.3f}\n")
        # letztes Bild nochmal ohne duration (ffmpeg-Quirk)
        f.write(f"file '{os.path.abspath(image_paths[-1])}'\n")

    srt_path = os.path.join(work_dir, "captions.srt")
    build_srt(script_text, duration, srt_path)

    silent_video = os.path.join(work_dir, "_silent.mp4")

    # Schritt 1: Bilder zu stummer Slideshow im 9:16-Format zusammensetzen
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",
        "-r", "30", silent_video,
    ], check=True)

    # Schritt 2: Audio + Untertitel drauf
    subprocess.run([
        "ffmpeg", "-y", "-i", silent_video, "-i", audio_path,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=16,PrimaryColour=&HFFFFFF&,Outline=2,Alignment=2,MarginV=120'",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", out_path,
    ], check=True)

    return out_path
