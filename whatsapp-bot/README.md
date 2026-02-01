# WhatsApp Bot - Voice-to-Text Transcription

A privacy-focused WhatsApp bot that transcribes and translates voice notes using OpenAI's latest AI models.

## What It Does

When someone sends a voice note to your WhatsApp number, this bot:
1. **Receives** the audio via Twilio webhook
2. **Acknowledges** immediately with "🔄 Translating your voice note..."
3. **Translates** the audio using OpenAI `gpt-4o-transcribe` direct translation API
4. **Replies** with the translated text

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-language** | Supports Chinese (Mandarin), English, and code-switching between them |
| **Singlish Support** | Handles Singaporean English and mixed Chinese-English content |
| **Privacy-First** | Audio files deleted immediately after processing |
| **Async Processing** | Handles webhooks instantly, processes audio in background queue |
| **Instant Feedback** | Sends acknowledgment message when voice note is received |
| **Error Handling** | Graceful error messages sent back to user on failure |
| **Extensible** | `translate()` function accepts `language_to` parameter for future language support |

---

## Architecture

```
                    Twilio WhatsApp
                         |
                         v
                    /webhook
                         |
                    +--------+
                    |  Ack   | "🔄 Translating..."
                    +--------+
                         |
                         v
            +------------------------+
            |   Robyn Web Server     |
            |  (port 8080)           |
            +------------------------+
                         |
                         v
            +------------------------+
            |   Kew Queue Manager    |
            |  (in-process workers)  |
            +------------------------+
                         |
                         v
            +------------------------+
            |   process_audio()      |
            |   Background Task      |
            +------------------------+
                         |
         +---------------+---------------+
         v               v               v
   [Download]      [Translate]      [Reply]
   Twilio CDN      OpenAI API       Twilio API
         |               |               |
         v               v               v
    .ogg file      gpt-4o-transcribe   WhatsApp
         |           (direct trans)
         v
    ffmpeg (.mp3)
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Web Server** | [Robyn](https://robyn.dev/) - Async Python web framework |
| **Queue System** | [Kew](https://github.com/justrach/kew) - Redis-based task queue (in-process) |
| **AI Model** | OpenAI `gpt-4o-transcribe` (direct translation API) |
| **Messaging** | Twilio WhatsApp API |
| **Audio** | ffmpeg for format conversion |

### Feature Architecture

#### 1. Webhook Reception (`src/routes/webhook.py`)
- Receives POST from Twilio when voice note arrives
- Parses form data for media URL and sender number
- Sends immediate acknowledgment message to user
- Submits task to Kew queue for background processing
- Returns 200 OK (prevents Twilio timeout)

#### 2. Queue Management (`src/taskqueue/manager.py`)
- **Kew TaskQueueManager** handles job queue with Redis backend
- 5 concurrent workers process audio tasks
- 5-minute timeout per task
- No separate worker process needed (runs in-process)

#### 3. Audio Pipeline (`src/services/`)

| Service | Responsibility |
|---------|---------------|
| **AudioService** | Downloads from Twilio CDN, converts .ogg to .mp3 via ffmpeg |
| **TranscriptionService** | Single-step: direct translation with `gpt-4o-transcribe`, extensible via `language_to` parameter |
| **MessagingService** | Sends acknowledgment and translated text via WhatsApp |

#### 4. Dependency Injection (`src/core/dependencies.py`)
- `ServiceContainer` holds singleton instances (services + queue_manager)
- Clean separation of concerns

---

## Local Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [ffmpeg](https://ffmpeg.org/) installed
- Docker (for Redis)

### Step 1: Clone and Install

```bash
cd whatsapp-bot

# Install ffmpeg (macOS)
brew install ffmpeg

# Install ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Install Python dependencies
uv sync
```

### Step 2: Environment Variables

Create a `.env` file:

```bash
# Twilio credentials (from console.twilio.com)
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here

# OpenAI API key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Redis (local or Fly.io)
REDIS_URL=redis://localhost:6379
```

### Step 3: Start Redis

```bash
docker run -d -p 6379:6379 --name whatsapp-redis redis
```

### Step 4: Run the Bot

```bash
# Single command - server starts with in-process queue workers
uv run python -m src.main
```

Server runs on `http://localhost:8080`

### Step 5: Expose with ngrok (for Twilio webhook)

```bash
ngrok http 8080
```

Use the ngrok URL in Twilio webhook configuration.

---

## Production Deployment (Fly.io)

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login

```bash
fly auth login
```

### Step 3: Create App

```bash
fly launch --no-deploy
```

### Step 4: Create Redis

```bash
fly redis create
```

This automatically sets `REDIS_URL` in your app's environment.

### Step 5: Set Secrets

```bash
fly secrets set \
  TWILIO_WHATSAPP_NUMBER="+14155238886" \
  TWILIO_ACCOUNT_SID="AC..." \
  TWILIO_AUTH_TOKEN="..." \
  OPENAI_API_KEY="sk-..."
```

### Step 6: Deploy

```bash
fly deploy
```

Your app will be live at `https://your-app-name.fly.dev`

### Step 7: Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Configure webhook:
   - **When a message comes in**: `https://your-app-name.fly.dev/webhook`
   - **HTTP Method**: `POST`
4. You'll need to buy a Twilio phone number for a monthly fee to set up your bot.
---

## Project Structure

```
whatsapp-bot/
├── src/
│   ├── main.py              # App entry point, startup/shutdown handlers
│   ├── config.py            # Pydantic settings from environment
│   ├── core/
│   │   ├── exceptions.py    # Custom exception types
│   │   ├── dependencies.py  # Service container (dependency injection)
│   │   └── logging.py       # Structured logging
│   ├── routes/
│   │   ├── health.py        # GET /health endpoint
│   │   └── webhook.py       # POST /webhook (Twilio)
│   ├── services/
│   │   ├── audio.py         # Download + convert audio
│   │   ├── transcription.py # OpenAI Whisper + translation
│   │   └── messaging.py     # Twilio WhatsApp API
│   └── taskqueue/
│       ├── manager.py       # Kew queue wrapper
│       └── __init__.py
├── Dockerfile               # Fly.io deployment
├── fly.toml                 # Fly.io config
├── pyproject.toml           # uv dependencies
└── .env.example             # Environment template
```

---

## Development

### Running Tests

```bash
uv run pytest
```

### Viewing Logs

```bash
# Local
tail -f /tmp/server.log

# Fly.io production
fly logs
```

### Monitoring Queue

Connect to Redis to see queued tasks:

```bash
redis-cli -h localhost -p 6379
> KEYS kew:*
```

---

## License

MIT
