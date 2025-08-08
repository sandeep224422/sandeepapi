from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_key: str
    download_dir: Path
    audio_format: str
    api_host: str
    api_port: int


def _get_env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_settings() -> Settings:
    api_key = _get_env("API_KEY", "change-me")
    download_dir_str = os.environ.get("DOWNLOAD_DIR", str(Path("downloads").resolve()))
    audio_format = os.environ.get("AUDIO_FORMAT", "mp3").lower()
    api_host = os.environ.get("API_HOST", "0.0.0.0")
    api_port = int(os.environ.get("PORT", os.environ.get("API_PORT", "8000")))

    download_dir = Path(download_dir_str).expanduser().resolve()
    return Settings(
        api_key=api_key,
        download_dir=download_dir,
        audio_format=audio_format,
        api_host=api_host,
        api_port=api_port,
    )


