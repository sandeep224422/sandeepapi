from __future__ import annotations

import concurrent.futures
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from yt_dlp import YoutubeDL


_thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4, thread_name_prefix="yt_dlp_worker")
_thread_pool_lock = threading.Lock()


@dataclass
class DownloadResult:
    source_url: str
    output_file: Path
    title: Optional[str]
    duration: Optional[float]
    extractor: Optional[str]
    webpage_url: Optional[str]
    info: Dict[str, Any]


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _run_download(
    url: str,
    download_dir: Path,
    audio_format: str = "mp3",
    output_template: str = "%(title)s.%(ext)s",
    extra_ydl_opts: Optional[Dict[str, Any]] = None,
) -> DownloadResult:
    _ensure_directory(download_dir)

    safe_outtmpl = str(download_dir / output_template)

    ydl_opts: Dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": safe_outtmpl,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
    }

    if extra_ydl_opts:
        ydl_opts.update(extra_ydl_opts)

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise RuntimeError("yt-dlp returned no info for the provided URL")

        # For search queries like ytsearch1:, actual entry lies under entries[0]
        if info.get("_type") == "playlist" and info.get("entries"):
            info = info["entries"][0]

        requested_downloads = ydl.prepare_filename(info)

    # After postprocessing, extension changes to audio_format
    output_file = Path(requested_downloads)
    output_file = output_file.with_suffix(f".{audio_format}")

    return DownloadResult(
        source_url=url,
        output_file=output_file,
        title=info.get("title"),
        duration=info.get("duration"),
        extractor=info.get("extractor_key"),
        webpage_url=info.get("webpage_url"),
        info=info,
    )


def download_audio(
    url: str,
    download_dir: Path,
    audio_format: str = "mp3",
    output_template: str = "%(title)s.%(ext)s",
    extra_ydl_opts: Optional[Dict[str, Any]] = None,
) -> DownloadResult:
    """
    Run a yt-dlp audio download in a shared thread pool to avoid blocking async servers.

    Note: Requires ffmpeg to be available on PATH for audio extraction.
    """
    with _thread_pool_lock:
        future = _thread_pool.submit(
            _run_download,
            url,
            Path(download_dir),
            audio_format,
            output_template,
            extra_ydl_opts,
        )
    return future.result()


