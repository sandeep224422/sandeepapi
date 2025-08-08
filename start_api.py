#!/usr/bin/env python3
"""Start the yt-dlp API service."""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from services.config import load_settings


def main():
    """Start the API server."""
    try:
        settings = load_settings()
        print(f"Starting yt-dlp API server on {settings.api_host}:{settings.api_port}")
        print(f"Download directory: {settings.download_dir}")
        print(f"API Key: {settings.api_key}")
        print(f"Audio format: {settings.audio_format}")
        print("\nAPI Endpoints:")
        print(f"  GET  http://{settings.api_host}:{settings.api_port}/health")
        print(f"  POST http://{settings.api_host}:{settings.api_port}/download")
        print("  (Requires X-API-Key header)")
        
        uvicorn.run(
            "api.server:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=False,
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
