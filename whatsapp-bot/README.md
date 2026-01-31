# WhatsApp Bot - Voice-to-Text Transcription

A lightweight, privacy-focused WhatsApp bot that transcribes voice notes using OpenAI Whisper.

## Features

- **Voice-to-Text**: Converts WhatsApp voice notes into readable text
- **Auto-Language Detection**: Supports Chinese (Mandarin) and English
- **Privacy-First**: Audio files are deleted immediately after processing
- **Async Processing**: Handles webhooks instantly to prevent Twilio timeouts

## Tech Stack

- **Web Server**: Robyn (Async Python)
- **Queue System**: arq (Redis-based asyncio job queue)
- **AI**: OpenAI Whisper API
- **SMS/WhatsApp**: Twilio API

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [ffmpeg](https://ffmpeg.org/) installed
- Redis running locally (or use Fly.io Redis)

### 1. Install Dependencies

```bash
# Install ffmpeg (macOS)
brew install ffmpeg

# Install ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
REDIS_URL=redis://localhost:6379
```

### 3. Start Redis

```bash
docker run -d -p 6379:6379 --name redis whatsapp-redis redis
```

### 4. Run the Bot

```bash
# Terminal 1: Start the web server
uv run python -m src.main

# Terminal 2: Start the worker
uv run arq src.workers.WorkerSettings
```

Or use the start script:

```bash
chmod +x start.sh
./start.sh
```

The bot will be available at `http://localhost:8080`

## Development

### Project Structure

```
whatsapp-bot/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Environment configuration
│   ├── core/                # Shared utilities
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── dependencies.py  # Dependency injection
│   ├── routes/              # HTTP endpoints
│   │   ├── health.py        # Health check
│   │   └── webhook.py       # Twilio webhook
│   ├── workers/             # Background jobs
│   │   ├── settings.py      # arq worker config
│   │   └── tasks.py         # Job tasks
│   └── services/            # Business logic
│       ├── audio.py         # Audio download/convert
│       ├── transcription.py # Whisper API
│       └── messaging.py     # Twilio API
├── Dockerfile
├── fly.toml
├── start.sh
└── pyproject.toml
```

## Deployment (Fly.io)

```bash
# Login to Fly.io
fly auth login

# Create the app
fly launch --no-deploy

# Create Redis (sets REDIS_URL automatically)
fly redis create

# Set secrets
fly secrets set \
  TWILIO_WHATSAPP_NUMBER="+14155238886" \
  TWILIO_ACCOUNT_SID="AC..." \
  TWILIO_AUTH_TOKEN="..." \
  OPENAI_API_KEY="sk-..."

# Deploy
fly deploy
```

## Twilio Setup

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Join the Sandbox by sending the code to the sandbox number
4. Configure webhook:
   - **When a message comes in**: `https://your-app.fly.dev/webhook`
   - **HTTP Method**: `POST`

## License

MIT
