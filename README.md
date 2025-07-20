# Advanced Quote Generator System - Modular Architecture

A comprehensive modular API system that generates viral Instagram quotes, creates images and videos, and uploads content to Instagram with a clean separation of concerns.

## 🏗️ Architecture Overview

```
src/
├── core/           # Core configuration and constants  
├── models/         # Pydantic data models and schemas
├── generators/     # Quote, image, and video generation
├── services/       # Business logic and orchestration
├── utils/          # Utility functions and helpers
└── api/            # FastAPI endpoints and routing
```

## ✨ Features

- 🧠 **AI Quote Generation**: Generate viral quotes with different formats and themes
- 🖼️ **Image Creation**: Convert quotes to styled images using Azure OpenAI DALL-E  
- 🎬 **Video Production**: Create engaging videos with background music and banners
- 📱 **Instagram Upload**: Automatically upload reels to Instagram
- 🔄 **Batch Processing**: Process multiple requests asynchronously
- 📊 **Analytics**: Track viral potential and performance metrics
- 🏗️ **Modular Design**: Clean separation of concerns for maintainability

## 🚀 Quick Start

1. **Setup Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements_modular.txt
   ```

3. **Run the Server**:
   ```bash
   python main.py
   ```

4. **Access API Documentation**:
   Open http://localhost:8000/docs

## Environment Variables

```bash
# AI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://litellm.tecosys.ai/

# Azure Configuration
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
DEPLOYMENT_NAME=your_deployment_name
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection

# Instagram Configuration
ACCESS_TOKEN=your_instagram_access_token
```

## API Endpoints

### Quote Generation
- `POST /generate-quote` - Generate a viral quote
- `GET /generate-trending-quote` - Generate trending viral content

### Content Creation
- `POST /generate-image` - Create image from quote
- `POST /generate-video` - Create video with image and title
- `POST /generate-complete-content` - Generate quote + image + video

### Batch Processing
- `POST /generate-batch-content` - Process multiple requests
- `GET /jobs/{job_id}` - Check batch job status

### Instagram Integration
- `POST /upload-to-instagram` - Upload video to Instagram
- `POST /create-and-upload-complete` - Full workflow with upload

### Analytics & Utilities
- `GET /viral-ideas` - Get viral content ideas
- `GET /analytics` - Performance analytics
- `GET /health` - System health check

## Usage Examples

### Generate a Viral Quote
```python
import requests

response = requests.post("http://localhost:8013/generate-quote", json={
    "audience": "gen-z",
    "theme": "relationships", 
    "format_preference": "painful_truth",
    "custom_topic": "modern dating"
})

quote = response.json()
print(f"Title: {quote['title']}")
print(f"Quote: {quote['quote']}")
```

### Create Complete Content Package
```python
response = requests.post("http://localhost:8013/generate-complete-content", json={
    "audience": "mixed",
    "theme": "life_lessons",
    "format_preference": "maturity_when"
}, params={
    "generate_image": True,
    "generate_video": True,
    "image_style": "paper"
})

content = response.json()
```

### Batch Processing
```python
requests_data = [
    {"audience": "gen-z", "theme": "motivation"},
    {"audience": "millennial", "theme": "success"},
    {"audience": "mixed", "theme": "relationships"}
]

response = requests.post("http://localhost:8013/generate-batch-content", json={
    "requests": requests_data,
    "generate_images": True,
    "generate_videos": False,
    "image_style": "modern"
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8013/jobs/{job_id}")
```

## Viral Content Tips

### Best Performing Formats
1. **"Maturity is when..."** - 95% viral rate
2. **"Painful But True"** - 92% viral rate  
3. **"Not everyone understands"** - 88% viral rate

### Optimal Themes
- Relationships (universal appeal)
- Mental health (high sharing)
- Life lessons (wisdom seekers)

### Engagement Boosters
- Keep quotes under 25 words
- Use emotional trigger words
- Create exclusivity feeling
- Make content screenshot-worthy

## Architecture

```
main.py                 # Main FastAPI application
├── advanced_quote_system.py  # AI quote generation
├── image_generator.py         # Azure DALL-E image creation
├── video_generator.py         # MoviePy video production
├── instaupload.py            # Instagram API integration
└── config.py                 # Configuration and constants
```

## System Requirements

- Python 3.8+
- Audio file: `new.mp3` (for video background)
- Azure OpenAI access
- Azure Blob Storage
- Instagram Business API access

## Production Deployment

1. Use environment variables for all secrets
2. Set up Redis for job storage instead of in-memory
3. Configure proper logging
4. Set up monitoring and health checks
5. Use a production WSGI server

## License

MIT License - see LICENSE file for details
