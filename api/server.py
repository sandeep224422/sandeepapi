from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from services.config import load_settings
from services.downloader import download_audio


settings = load_settings()

app = FastAPI(title="yt-dlp Audio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

# Always mount /files; directory may be created later
app.mount(
    "/files",
    StaticFiles(directory=str(settings.download_dir), check_dir=False),
    name="files",
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "yt-dlp Audio API",
        "status": "ok",
        "endpoints": {"health": "/health", "download": "/download", "docs": "/docs"},
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "download_dir": str(settings.download_dir),
        "audio_format": settings.audio_format,
    }


@app.post("/download")
def start_download(
    payload: Dict[str, Any],
    _: None = Depends(require_api_key),
) -> JSONResponse:
    url: Optional[str] = payload.get("url")
    query: Optional[str] = payload.get("query")
    audio_format: str = (payload.get("audio_format") or settings.audio_format).lower()

    if not url and not query:
        raise HTTPException(status_code=400, detail="Provide either 'url' or 'query'")

    target: str = url or f"ytsearch1:{query}"
    result = download_audio(
        url=target,
        download_dir=settings.download_dir,
        audio_format=audio_format,
    )

    # Build a file URL for convenience
    file_url: Optional[str] = None
    try:
        relative_name = Path(result.output_file.name)
        file_url = f"/files/{relative_name.as_posix()}"
    except Exception:
        file_url = None

    return JSONResponse(
        {
            "title": result.title,
            "duration": result.duration,
            "source_url": result.webpage_url or result.source_url,
            "extractor": result.extractor,
            "audio_format": audio_format,
            "file_path": str(result.output_file),
            "file_url": file_url,
        }
    )


@app.get("/file")
def download_file(path: str, _: None = Depends(require_api_key)) -> Response:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(path=str(file_path), media_type=media_type or "application/octet-stream")


