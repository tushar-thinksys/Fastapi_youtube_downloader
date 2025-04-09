import os
from yt_dlp import YoutubeDL
from pytube import YouTube
from pytube.exceptions import VideoUnavailable

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def download_with_yt_dlp(url: str, fmt: str, quality: str) -> str:
    print(f"Trying yt-dlp with format={fmt}, quality={quality}")

    # Clean format and quality inputs
    expected_ext = fmt if fmt != "mp3" else "mp3"
    
    ydl_opts = {
        "format": get_format_string(fmt, quality),
        "quiet": True,
        "merge_output_format": expected_ext,
        "outtmpl": os.path.join(DOWNLOAD_DIR, f"%(title)s_{quality}.%(ext)s"),
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ] if fmt == "mp3" else [],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = sanitize_filename(info.get("title", "video"))
        expected_filename = f"{title}_{quality}.{expected_ext}"
        actual_path = os.path.join(DOWNLOAD_DIR, expected_filename)

        # Try to find the actual file downloaded
        if not os.path.exists(actual_path):
            downloaded_files = os.listdir(DOWNLOAD_DIR)
            for file in downloaded_files:
                if file.startswith(title) and file.endswith(f".{expected_ext}"):
                    guessed_path = os.path.join(DOWNLOAD_DIR, file)
                    os.rename(guessed_path, actual_path)
                    break
            else:
                raise Exception("Downloaded file not found after yt-dlp run.")

    return actual_path

async def download_with_pytube(url: str, fmt: str, quality: str) -> str:
    print(f"pytube: trying to download format={fmt}, quality={quality}")
    yt = YouTube(url)
    title = sanitize_filename(yt.title)

    if fmt == "mp3":
        stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    else:
        stream = (
            yt.streams.filter(file_extension=fmt, progressive=True)
            .filter(res=quality)
            .first()
            or yt.streams.filter(file_extension=fmt, progressive=True)
            .order_by("resolution")
            .desc()
            .first()
        )

    if not stream:
        raise ValueError("No compatible stream found.")

    filename = f"{title}.{fmt}"
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    stream.download(output_path=DOWNLOAD_DIR, filename=filename)
    return filepath

def get_format_string(fmt: str, quality: str) -> str:
    try:
        qmap = {"4k": 2160, "8k": 4320}
        height = qmap.get(quality.lower(), int(quality.lower().replace("p", "")))
    except ValueError:
        height = 720
    if fmt == "mp3":
        return "bestaudio"
    return f"bestvideo[ext={fmt}][height<={height}]+bestaudio/best"

def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
