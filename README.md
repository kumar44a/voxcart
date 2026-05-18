# VoiceBot with Avatar

A **real-time conversational voice bot** powered by **LiveKit** infrastructure with an animated avatar interface. This application enables natural voice conversations with an AI assistant using state-of-the-art speech recognition, language models, and text-to-speech synthesis.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Environment Configuration](#environment-configuration)
7. [Installation & Setup](#installation--setup)
8. [Running the Application](#running-the-application)
9. [Docker Deployment](#docker-deployment)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [File Structure](#file-structure)

---

## Overview

This voicebot application creates a real-time, bidirectional voice communication channel between a user and an AI assistant. The system leverages:

- **LiveKit** for real-time WebRTC-based audio/video communication
- **OpenAI GPT-4o-mini** for intelligent conversational responses
- **OpenAI Whisper** for accurate speech-to-text transcription
- **Cartesia Sonic-2** for high-quality, natural-sounding text-to-speech
- **Silero VAD** for voice activity detection

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER'S BROWSER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         index.html                                   │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │    │
│  │  │  Join/Leave │  │  Microphone │  │   Avatar    │  │   Audio    │  │    │
│  │  │   Buttons   │  │   Capture   │  │    GIF      │  │  Playback  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                                      ▲
         │ 1. HTTP Request (Get JWT Token)                      │
         ▼                                                      │
┌─────────────────────┐                                         │
│      api.py         │                                         │
│   (Flask Server)    │                                         │
│   Port: 5001        │                                         │
│                     │                                         │
│  • Token Generation │                                         │
│  • Room Creation    │                                         │
│  • CORS Handling    │                                         │
└─────────────────────┘                                         │
                                                                │
         │ 2. JWT Token Response                                │
         ▼                                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LIVEKIT CLOUD                                      │
│                    (wss://biademo-byev8uhf.livekit.cloud)                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      WebRTC Media Server                             │    │
│  │  • Real-time audio/video routing                                     │    │
│  │  • Room management                                                   │    │
│  │  • Participant tracking                                              │    │
│  │  • Agent dispatch                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                                      ▲
         │ 3. WebSocket Connection                              │
         │    (Bidirectional Audio Streams)                     │
         ▼                                                      │
┌─────────────────────────────────────────────────────────────────────────────┐
│                            agent.py                                          │
│                      (LiveKit Voice Agent)                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        AI Pipeline                                   │    │
│  │                                                                      │    │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────────┐  │    │
│  │  │   VAD    │──▶│   STT    │──▶│   LLM    │──▶│       TTS        │  │    │
│  │  │ (Silero) │   │(Whisper) │   │(GPT-4o)  │   │ (Cartesia Sonic) │  │    │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────────────┘  │    │
│  │       │              │              │                   │           │    │
│  │       ▼              ▼              ▼                   ▼           │    │
│  │  Detect when   Transcribe     Generate        Synthesize natural   │    │
│  │  user speaks   speech to      AI response     sounding speech      │    │
│  │                text                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Additional Features:                                                        │
│  • Noise Cancellation (BVC)                                                 │
│  • Multilingual Turn Detection                                              │
│  • Automatic Greeting                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.12 | Application runtime |
| **Real-time Communication** | LiveKit | Latest | WebRTC infrastructure |
| **Web Framework** | Flask | Latest | REST API server |
| **Frontend** | HTML/CSS/JavaScript | - | Browser UI |

### AI/ML Services

| Service | Provider | Model | Purpose |
|---------|----------|-------|---------|
| **Speech-to-Text (STT)** | OpenAI | Whisper | Transcribes user speech to text |
| **Language Model (LLM)** | OpenAI | GPT-4o-mini | Generates conversational responses |
| **Text-to-Speech (TTS)** | Cartesia | Sonic-2 | Synthesizes natural voice output |
| **Voice Activity Detection (VAD)** | Silero | VAD | Detects when user is speaking |
| **Turn Detection** | LiveKit | Multilingual | Detects conversation turn-taking |
| **Noise Cancellation** | LiveKit | BVC | Filters background noise |

### Python Dependencies

```
python-dotenv          # Environment variable management
livekit                # LiveKit Python SDK
livekit-agents         # LiveKit Agents framework
livekit-agents[openai] # OpenAI plugin for STT/LLM
livekit-agents[cartesia] # Cartesia plugin for TTS
livekit-agents[silero] # Silero plugin for VAD
livekit-agents[turn-detector] # Turn detection plugin
livekit-plugins-noise-cancellation # Noise cancellation
flask                  # Web framework
flask-cors             # CORS support
cartesia               # Cartesia API client
```

---

## Component Details

### 1. Voice Agent (`agent.py`)

The core AI agent that processes voice interactions.

**Key Classes & Functions:**

```python
class Assistant(Agent):
    """Custom agent with personality and instructions."""
    def __init__(self):
        super().__init__(instructions="You are a helpful voice AI assistant behalf of Amit")
```

**AgentSession Configuration:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `stt` | `openai.STT()` | OpenAI Whisper for speech recognition |
| `llm` | `openai.LLM(model="gpt-4o-mini")` | GPT-4o-mini for response generation |
| `tts` | `cartesia.TTS(model="sonic-2", voice="...")` | Cartesia Sonic-2 for voice synthesis |
| `vad` | `silero.VAD.load()` | Silero for voice activity detection |
| `turn_detection` | `MultilingualModel()` | Multilingual turn detection |

**Room Input Options:**
- **Noise Cancellation**: `noise_cancellation.BVC()` - Background Voice Cancellation for cleaner audio

**Lifecycle:**
1. Agent registers with LiveKit Cloud
2. Waits for room join events
3. On user connection, starts the AI session
4. Sends initial greeting
5. Processes voice input → generates response → speaks output

---

### 2. Token Server (`api.py`)

Flask-based REST API for JWT token generation.

**Endpoints:**

| Method | Endpoint | Parameters | Response |
|--------|----------|------------|----------|
| GET | `/getToken` | `name` (optional), `room` (optional) | `{token, room, identity}` |

**Token Generation Flow:**
```python
grants = VideoGrants(room_join=True, room=room)
token = AccessToken(api_key, api_secret)
        .with_identity(name)
        .with_grants(grants)
return token.to_jwt()
```

**Security Features:**
- JWT-based authentication
- API key/secret validation
- Room-scoped permissions
- CORS enabled for browser access

---

### 3. Web Frontend (`index.html`)

Single-page browser application for user interaction.

**UI Components:**
- **Name Input**: User identity for the session
- **Join Button**: Initiates connection to LiveKit room
- **Leave Button**: Disconnects from the room
- **Avatar GIF**: Visual feedback when connected
- **Status Display**: Connection state messages
- **Audio Area**: Container for audio playback elements

**JavaScript SDK Integration:**
```javascript
const { Room, RoomEvent, Track } = window.LivekitClient;
```

**Event Handlers:**
| Event | Action |
|-------|--------|
| `TrackSubscribed` | Attaches audio track for playback |
| `Disconnected` | Cleans up UI and resets state |

**Connection Flow:**
1. Fetch JWT token from `/getToken`
2. Create LiveKit Room instance
3. Connect to LiveKit Cloud WebSocket
4. Enable local microphone
5. Subscribe to agent's audio tracks

---

### 4. Utility Script (`get_voices.py`)

Helper script to list available Cartesia voices.

```python
from cartesia import Cartesia
client = Cartesia(api_key="...")
voices = client.voices.list()
for voice in voices:
    print(voice.id, voice.name)
```

**Usage:** Run to find voice IDs for TTS configuration.

---

## Data Flow

### Complete Request-Response Cycle

```
┌─────────┐    ┌─────────┐    ┌─────────────┐    ┌─────────┐    ┌─────────┐
│  User   │    │ Browser │    │   LiveKit   │    │  Agent  │    │   AI    │
│ (Voice) │    │   UI    │    │   Cloud     │    │ Server  │    │Services │
└────┬────┘    └────┬────┘    └──────┬──────┘    └────┬────┘    └────┬────┘
     │              │                │                │              │
     │ Speak        │                │                │              │
     ├─────────────▶│                │                │              │
     │              │ Audio Stream   │                │              │
     │              ├───────────────▶│                │              │
     │              │                │ Route Audio    │              │
     │              │                ├───────────────▶│              │
     │              │                │                │ VAD: Detect  │
     │              │                │                ├─────────────▶│
     │              │                │                │              │
     │              │                │                │ STT: Transcribe
     │              │                │                ├─────────────▶│
     │              │                │                │◀─────────────┤
     │              │                │                │   "Hello"    │
     │              │                │                │              │
     │              │                │                │ LLM: Generate│
     │              │                │                ├─────────────▶│
     │              │                │                │◀─────────────┤
     │              │                │                │  Response    │
     │              │                │                │              │
     │              │                │                │ TTS: Speak   │
     │              │                │                ├─────────────▶│
     │              │                │                │◀─────────────┤
     │              │                │ Audio Stream   │  Audio       │
     │              │                │◀───────────────┤              │
     │              │ Play Audio     │                │              │
     │              │◀───────────────┤                │              │
     │ Hear Response│                │                │              │
     │◀─────────────┤                │                │              │
     │              │                │                │              │
```

### Latency Breakdown (Typical)

| Stage | Typical Latency |
|-------|-----------------|
| Audio capture → LiveKit | ~50ms |
| VAD processing | ~20ms |
| STT (Whisper) | ~200-500ms |
| LLM (GPT-4o-mini) | ~300-800ms |
| TTS (Cartesia Sonic-2) | ~100-300ms |
| Audio delivery | ~50ms |
| **Total end-to-end** | **~700ms - 1.7s** |

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# LiveKit Configuration
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx      # From LiveKit Cloud dashboard
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxx     # From LiveKit Cloud dashboard
LIVEKIT_URL=wss://your-project.livekit.cloud  # Your LiveKit server URL

# AI Service API Keys
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx      # OpenAI API key for STT & LLM
CARTESIA_API_KEY=sk_car_xxxxxxxxxxxxx   # Cartesia API key for TTS
```

### Obtaining API Keys

| Service | URL | Notes |
|---------|-----|-------|
| **LiveKit** | https://cloud.livekit.io | Create project → Settings → Keys |
| **OpenAI** | https://platform.openai.com/api-keys | Requires billing setup |
| **Cartesia** | https://play.cartesia.ai | Sign up for API access |

---

## Installation & Setup

### Prerequisites

- Python 3.11 or 3.12
- pip or conda
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Microphone access

### Step 1: Clone/Navigate to Project

```bash
cd /path/to/voicebot_with_avatar
```

### Step 2: Create Virtual Environment

**Option A: Using virtualenv**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate   # Windows
```

**Option B: Using conda**
```bash
conda create -n voicebot python=3.11 -y
conda activate voicebot
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install "livekit-agents[openai,cartesia,silero,turn-detector]~=1.0"
pip install "livekit-plugins-noise-cancellation~=0.2"
pip install python-dotenv
```

### Step 4: Configure Environment

```bash
cp .env_example .env
# Edit .env with your API keys
```

### Step 5: Download Model Files

```bash
python agent.py download-files
```

This downloads required model files for:
- Silero VAD
- Turn detection models

---

## Running the Application

### Development Mode (2 Terminals)

**Terminal 1 – Token Server + Frontend:**
```bash
python api.py
# Server starts on http://localhost:5001
# Frontend served at http://localhost:5001
```

**Terminal 2 – Voice Agent:**
```bash
python agent.py start
# Agent registers with LiveKit Cloud
```

### Stopping All Services

```bash
pkill -f "python api.py" ; pkill -f "python agent.py"
```

---

## Docker Deployment (Windows / macOS / Linux)

### Prerequisites

- **Docker Desktop** installed ([Download for Windows](https://www.docker.com/products/docker-desktop/))
- A `.env` file with your API keys (copy from `.env_example`)

### Quick Start (Docker Compose)

```bash
# 1. Copy and fill in your API keys
copy .env_example .env        # Windows
# cp .env_example .env        # macOS/Linux

# 2. Edit .env with your keys

# 3. Build and run
docker compose up --build -d

# 4. Open http://localhost:5001 in your browser
```

### Manual Docker Build & Run

```bash
# Build the image
docker build -t voicebot .

# Download AI model files (first time only)
docker run --rm --env-file .env voicebot python agent.py download-files

# Run the container
docker run -d --name voicebot -p 5001:5001 --env-file .env voicebot
```

### Stopping

```bash
docker compose down
# or
docker stop voicebot && docker rm voicebot
```

---

## API Reference

### Token Generation Endpoint

**Request:**
```http
GET /getToken?name=John&room=my-room
Host: localhost:5001
```

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | No | `guest` | User identity |
| `room` | string | No | Auto-generated | Room name |

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room": "room-bf4cfe6e",
  "identity": "John"
}
```

**Error Responses:**
| Status | Description |
|--------|-------------|
| 500 | Missing API credentials |

---

## Troubleshooting

### listing processed running
lsof -i :5001 -i :8081 -i :8080 2>/dev/null | grep LISTEN

curl -s "http://localhost:5001/getToken?name=TestUser&language=en" 2>&1

### Common Issues


#### 1. SSL Certificate Error (macOS)
```
ssl.SSLCertVerificationError: certificate verify failed
```

**Solution:**
```bash
SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())") python agent.py start
```

Or add to `~/.zshrc`:
```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
```

#### 2. Port Already in Use
```
Address already in use
```

**Solution:**
```bash
# Find and kill process on port 5001
lsof -i :5001 | grep LISTEN
kill <PID>

# Or for port 8081 (agent)
lsof -i :8081 | grep LISTEN
kill <PID>
```

#### 3. Agent Not Connecting to LiveKit
```
failed to connect to livekit after 16 attempts
```

**Check:**
- Verify `LIVEKIT_URL` in `.env` is correct
- Ensure `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are valid
- Check network connectivity to LiveKit Cloud

#### 4. No Audio from Bot
**Check:**
- Browser microphone permissions granted
- `OPENAI_API_KEY` is valid (for STT)
- `CARTESIA_API_KEY` is valid (for TTS)
- Check browser console for errors

#### 5. Microphone Not Working
**Check:**
- Browser has microphone permission
- Correct microphone selected in browser
- No other application using microphone

---

## File Structure

```
voicebot_with_avatar/
├── agent.py              # LiveKit voice agent (AI pipeline + tools)
├── api.py                # Flask token server + frontend serving
├── index.html            # Web frontend UI
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Docker Compose for one-command startup
├── start.sh              # Container entrypoint script
├── .dockerignore         # Files excluded from Docker image
├── .env                  # Environment variables (create from .env_example)
├── .env_example          # Environment template
├── get_voices.py         # Utility to list Cartesia voices
├── README.md             # This documentation
├── assets/               # Static assets
│   └── AssistantVoice.gif  # Avatar animation
└── KMS/                  # (Reserved for future use)
```

---

## Security Considerations

1. **Never commit `.env` file** – Contains sensitive API keys
2. **Use HTTPS in production** – Secure token transmission
3. **Rotate API keys regularly** – Minimize exposure risk
4. **Limit CORS origins** – Currently set to `*` (allow all)
5. **Implement rate limiting** – Prevent API abuse
6. **Validate user input** – Sanitize name parameter

---

## Future Enhancements

- [ ] Persistent conversation history
- [ ] Multiple avatar options
- [ ] Voice selection UI
- [ ] Conversation transcripts
- [ ] User authentication
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Custom wake words

---

## License

[Add your license here]

---

## Contributors

- Amit Yadav

---

*Documentation generated on April 2026*