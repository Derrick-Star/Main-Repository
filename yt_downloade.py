import os
import re
import subprocess

BASE_DIR = "/storage/emulated/0/Python Download"

FOLDERS = {
    "video": os.path.join(BASE_DIR, "videos"),
    "short": os.path.join(BASE_DIR, "shorts"),
    "playlist": os.path.join(BASE_DIR, "playlists"),
    "music": os.path.join(BASE_DIR, "music"),
}

def _ensure_folders():
    for folder in FOLDERS.values():
        os.makedirs(folder, exist_ok=True)

def detect_youtube_type(url: str) -> str:
    if "music.youtube.com" in url:
        return "music"
    if "playlist" in url or "list=" in url:
        return "playlist"
    if re.search(r"youtube\.com/shorts/", url):
        return "short"
    return "video"

def build_command(url: str, yt_type: str) -> list:
    """Brute-force single-file download (no ffmpeg merge needed)"""
    output_dir = FOLDERS[yt_type]

    # FORCE single file (best mp4 + audio)
    return [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",
        "-o", f"{output_dir}/%(title)s.%(ext)s",
        url,
    ]

def download_youtube(url: str) -> dict:
    _ensure_folders()
    yt_type = detect_youtube_type(url)
    command = build_command(url, yt_type)

    try:
        subprocess.run(command, check=True)
        return {
            "success": True,
            "type": yt_type,
            "folder": FOLDERS[yt_type],
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "type": yt_type,
            "error": str(e),
        }
        
user_url = input("Input Url:  ")

download_youtube(user_url)