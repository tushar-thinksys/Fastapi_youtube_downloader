
from pydantic import BaseModel
from typing import Optional


class DownloadRequest(BaseModel):
    url: str
    format: Optional[str] = "mp4"
    quality: Optional[str] = "720p"


class DownloadResponse(BaseModel):
    status: str
    message: str


class MetadataResponse(BaseModel):
    title: str
    duration: str
    views: Optional[int]
    likes: Optional[int]
    channel: str
    published_date: str
    thumbnail_url: str
