# yt-dlp Audio API Service

A FastAPI service that provides audio download functionality using yt-dlp with API key authentication.

## Features

- 🔐 API key authentication
- 🎵 Audio download from URLs or search queries
- 📁 Automatic file organization
- 🎧 Multiple audio formats (mp3, m4a, etc.)
- 🌐 CORS enabled for web integration

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r services/requirements.txt
```

### 2. Environment Variables

Set these environment variables (or use defaults):

```bash
# Required
export API_KEY="your-secret-api-key-here"

# Optional (with defaults)
export DOWNLOAD_DIR="./downloads"           # Default: ./downloads
export AUDIO_FORMAT="mp3"                   # Default: mp3
export API_HOST="0.0.0.0"                  # Default: 0.0.0.0
export API_PORT="8000"                      # Default: 8000
```

### 3. Start the API Server

```bash
python start_api.py
```

The server will start on `http://0.0.0.0:8000` (or your configured host/port).

## API Endpoints

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "download_dir": "/path/to/downloads",
  "audio_format": "mp3"
}
```

### Download Audio
```http
POST /download
X-API-Key: your-secret-api-key-here
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "audio_format": "mp3"
}
```

Or search by query:
```http
POST /download
X-API-Key: your-secret-api-key-here
Content-Type: application/json

{
  "query": "never gonna give you up",
  "audio_format": "mp3"
}
```

Response:
```json
{
  "title": "Rick Astley - Never Gonna Give You Up",
  "duration": 212.0,
  "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "extractor": "Youtube",
  "audio_format": "mp3",
  "file_path": "/path/to/downloads/Rick Astley - Never Gonna Give You Up.mp3",
  "file_url": "/files/Rick Astley - Never Gonna Give You Up.mp3"
}
```

## Integration with Music Bots

### Example Usage (Python)

```python
import requests

API_BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"

def download_song(query_or_url):
    headers = {"X-API-Key": API_KEY}
    
    if query_or_url.startswith("http"):
        payload = {"url": query_or_url}
    else:
        payload = {"query": query_or_url}
    
    response = requests.post(
        f"{API_BASE_URL}/download",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data["title"],
            "file_path": data["file_path"],
            "file_url": f"{API_BASE_URL}{data['file_url']}" if data["file_url"] else None
        }
    else:
        raise Exception(f"Download failed: {response.text}")

# Usage
try:
    result = download_song("never gonna give you up")
    print(f"Downloaded: {result['title']}")
    print(f"File: {result['file_path']}")
except Exception as e:
    print(f"Error: {e}")
```

### Example Usage (cURL)

```bash
# Download by URL
curl -X POST "http://localhost:8000/download" \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Download by search query
curl -X POST "http://localhost:8000/download" \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "never gonna give you up"}'
```

## Requirements

- Python 3.8+
- ffmpeg (for audio conversion)
- yt-dlp
- FastAPI
- uvicorn

## Notes

- The API requires ffmpeg to be installed and available in PATH for audio conversion
- Downloads are stored in the configured `DOWNLOAD_DIR`
- Files are automatically converted to the specified audio format
- The service supports both direct URLs and search queries
- CORS is enabled for web integration
