from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from schemas import DownloadRequest, DownloadResponse, MetadataResponse
from yt_dlp_fallback import download_with_yt_dlp, download_with_pytube
from utils import extract_metadata
import asyncio
import os

app = FastAPI()



@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest):
    url, fmt, quality = request.url, request.format or "mp4", request.quality or "720p"

    try:
        await download_with_yt_dlp(url, fmt, quality)
        return DownloadResponse(status="success", message="Download started")
    except Exception:
        try:
            await download_with_pytube(url, fmt, quality)
            return DownloadResponse(status="success", message="Download started")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")


@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata(url: str):
    try:
        data = await extract_metadata(url)
        return MetadataResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Metadata extraction failed: {str(e)}")
