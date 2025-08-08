# Heroku Deployment Guide

This guide will help you deploy the yt-dlp API service to Heroku.

## Prerequisites

1. **GitHub Account**: Make sure your code is pushed to https://github.com/Suraj08832/ytdlp
2. **Heroku Account**: Sign up at https://heroku.com
3. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli

## Step 1: Prepare Your Repository

Make sure your repository has these files:
- `Procfile` - Tells Heroku how to run your app
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `app.json` - Heroku app configuration

## Step 2: Deploy to Heroku

### Option A: Deploy via Heroku Dashboard (Recommended)

1. **Go to Heroku Dashboard**
   - Visit https://dashboard.heroku.com
   - Click "New" → "Create new app"

2. **Connect to GitHub**
   - Choose "GitHub" as deployment method
   - Connect your GitHub account if not already connected
   - Search for your repository: `Suraj08832/ytdlp`
   - Select the repository

3. **Configure Environment Variables**
   - Go to "Settings" tab
   - Click "Reveal Config Vars"
   - Add these environment variables:
     ```
     API_KEY = your-secret-api-key-here
     DOWNLOAD_DIR = /tmp/downloads
     AUDIO_FORMAT = mp3
     ```

4. **Deploy**
   - Go to "Deploy" tab
   - Click "Deploy Branch" (main/master)
   - Wait for deployment to complete

### Option B: Deploy via Heroku CLI

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Add Buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-ffmpeg-latest
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set API_KEY=your-secret-api-key-here
   heroku config:set DOWNLOAD_DIR=/tmp/downloads
   heroku config:set AUDIO_FORMAT=mp3
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

## Step 3: Verify Deployment

1. **Check App Status**
   ```bash
   heroku ps
   ```

2. **View Logs**
   ```bash
   heroku logs --tail
   ```

3. **Test the API**
   ```bash
   # Health check
   curl https://your-app-name.herokuapp.com/health
   
   # Test download (replace with your actual API key)
   curl -X POST "https://your-app-name.herokuapp.com/download" \
     -H "X-API-Key: your-secret-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"query": "test song"}'
   ```

## Step 4: Update Your Music Bot

Update your music bot to use the Heroku URL:

```python
# Replace with your actual Heroku app URL
API_BASE_URL = "https://your-app-name.herokuapp.com"
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
```

## Important Notes

1. **API Key**: Make sure to use a strong, unique API key
2. **File Storage**: Heroku uses ephemeral storage, so files will be deleted when the dyno restarts
3. **Rate Limits**: Be aware of Heroku's rate limits and your app's usage
4. **Scaling**: Consider upgrading your dyno if you need more resources

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Ensure `Procfile` is correctly formatted
   - Verify Python version in `runtime.txt`

2. **App Crashes**
   - Check logs: `heroku logs --tail`
   - Verify environment variables are set
   - Ensure ffmpeg buildpack is added

3. **API Key Issues**
   - Make sure `API_KEY` environment variable is set
   - Verify the key is being sent in the `X-API-Key` header

### Getting Help

- [Heroku Documentation](https://devcenter.heroku.com/)
- [Heroku Support](https://help.heroku.com/)
- [GitHub Issues](https://github.com/Suraj08832/ytdlp/issues)
