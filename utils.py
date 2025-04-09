
from yt_dlp import YoutubeDL


async def extract_metadata(url: str) -> dict:
    ydl_opts = {"quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "duration": format_duration(info.get("duration", 0)),
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "channel": info.get("uploader"),
            "published_date": info.get("upload_date", "N/A"),
            "thumbnail_url": info.get("thumbnail"),
        }


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}m{sec}s"
