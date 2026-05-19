# VoxCart — Real-Time E-Commerce Voice Assistant

> **Capstone Project** · Generative AI Applications (GIAI) Program

VoxCart is a **real-time, voice-driven e-commerce support assistant** built on LiveKit's WebRTC infrastructure. A customer speaks naturally into their browser microphone; VoxCart transcribes the speech, reasons over it using a large language model, and replies with synthesized voice — all within a second. The system handles product inquiries, order tracking, and returns policy questions using a mock e-commerce backend, with an optional RAG layer for factual consistency.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [E-Commerce Features](#e-commerce-features)
5. [Real-Time AI Pipeline](#real-time-ai-pipeline)
6. [Environment Configuration](#environment-configuration)
7. [Installation & Setup](#installation--setup)
8. [Running the Application](#running-the-application)
9. [Docker Deployment](#docker-deployment)
10. [Demo Scenarios](#demo-scenarios)
11. [API Reference](#api-reference)
12. [Project Structure](#project-structure)
13. [Troubleshooting](#troubleshooting)

---

## Overview

### Capstone Objectives

| Objective | Implementation |
|-----------|----------------|
| Real-time voice interaction | LiveKit WebRTC room — bidirectional audio in < 1 second |
| STT + TTS in a live loop | OpenAI Whisper (STT) + Cartesia Sonic-2 (TTS) |
| LLM-driven conversational engine | GPT-4.1 with e-commerce system prompt |
| Decision routing to backend actions | Function-calling tools for orders, products, returns |
| End-to-end e-commerce demo | Three required demo scenarios fully functional |

### What Makes VoxCart Different

- **No page refresh, no typing** — pure voice from start to finish
- **Stateful conversation** — Aria (the assistant) remembers context within a session
- **Graceful uncertainty handling** — explicit fallbacks for unclear speech and out-of-scope requests
- **Multilingual** — handles English + multiple Indian languages via language selector
- **Optional RAG** — product FAQ and policy documents injected into LLM context for factual answers

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            USER'S BROWSER                                 │
│                                                                           │
│   ┌────────────┐  ┌─────────────────┐  ┌──────────┐  ┌───────────────┐  │
│   │ Microphone │  │  Avatar + State │  │  Transcript│  │  Audio Output │  │
│   │  Capture   │  │   Visualizer    │  │   Panel  │  │   Playback    │  │
│   └────────────┘  └─────────────────┘  └──────────┘  └───────────────┘  │
└────────────────────────────┬──────────────────────────────┬──────────────┘
                             │ 1. GET /getToken              │ 5. Audio out
                             ▼                               │
                   ┌─────────────────────┐                  │
                   │      api.py          │                  │
                   │   Flask  :5001       │                  │
                   │  JWT token minting   │                  │
                   └────────┬────────────┘                  │
                            │ 2. JWT token                  │
                            ▼                               │
              ┌─────────────────────────────┐              │
              │       LIVEKIT CLOUD          │◀─────────────┘
              │   WebRTC Media Server        │
              │  Room · Tracks · Dispatch    │
              └──────────────┬──────────────┘
                             │ 3. Audio stream (user mic)
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            agent.py (VoxCart Agent)                       │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────────────────────────┐  │
│  │  Silero  │  │ OpenAI   │  │          GPT-4.1 (LLM)                │  │
│  │  VAD     │─▶│ Whisper  │─▶│  E-Commerce System Prompt             │  │
│  │          │  │  (STT)   │  │  + Optional RAG Context               │  │
│  └──────────┘  └──────────┘  │                                       │  │
│                               │  ┌────────────────────────────────┐  │  │
│                               │  │     Function-Calling Tools      │  │  │
│                               │  │  • get_order_status(order_id)   │  │  │
│                               │  │  • lookup_product(query)        │  │  │
│                               │  │  • get_returns_policy(reason)   │  │  │
│                               │  │  • get_current_datetime(tz)     │  │  │
│                               │  │  • search_faq(query)            │  │
│                               │  └────────────────────────────────┘  │  │
│                               └──────────────┬────────────────────────┘  │
│                                              │                            │
│                                              ▼                            │
│                                    ┌──────────────────┐                  │
│                                    │  Cartesia Sonic-2 │                  │
│                                    │  (TTS) → Audio    │                  │
│                                    └────────┬──────────┘                  │
└─────────────────────────────────────────────┼────────────────────────────┘
                                              │ 4. Audio stream (bot voice)
                                              ▼
                                     LiveKit Cloud → Browser
```

---

## Technology Stack

### Core Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Real-time transport | **LiveKit** (WebRTC) | Bidirectional audio rooms, agent dispatch |
| Backend API | **Flask** (Python) | JWT token minting, static file serving |
| Frontend | **HTML / CSS / JS** | Browser voice UI with avatar |
| Containerisation | **Docker + Compose** | One-command portable deployment |

### AI / ML Services

| Layer | Provider | Model | Role |
|-------|----------|-------|------|
| Voice Activity Detection | Silero | VAD | Detect when user starts/stops speaking |
| Speech-to-Text | OpenAI | Whisper | Transcribe user speech to text |
| Language Model | OpenAI | **GPT-4.1** | Conversational reasoning + tool calls |
| Text-to-Speech | Cartesia | **Sonic-2** | Synthesise natural e-commerce assistant voice |
| Turn Detection | LiveKit | Multilingual | Know when the user has finished their turn |

### Python Dependencies

```
livekit-agents[openai,cartesia,silero,turn-detector]~=1.0
flask, flask-cors
python-dotenv
certifi
```

---

## E-Commerce Features

### Supported Intents

| Intent | Example Query | Tool Called |
|--------|---------------|-------------|
| Order tracking | *"Where is my order ORD-1042?"* | `get_order_status` |
| Product inquiry | *"Tell me about the Sony headphones"* | `lookup_product` |
| Returns & refunds | *"I want to return my jacket"* | `get_returns_policy` |
| General FAQ | *"What's your delivery time?"* | RAG / LLM knowledge |
| Date / time | *"What day is today?"* | `get_current_datetime` |
| Policy / FAQ | *"Is COD available?"* / *"How long does delivery take?"* | `search_faq` |

### Mock Data

All e-commerce data is **self-generated and synthetic** — no real customer data is used.

| Dataset | Contents |
|---------|----------|
| `mock_data.py` | 10 sample orders · 20 products · returns policy rules |
| `rag/faq.txt` | Shipping, payment, and policy FAQ for RAG context |

---

## Real-Time AI Pipeline

### End-to-End Latency

| Stage | Typical |
|-------|---------|
| Audio capture → LiveKit | ~50 ms |
| VAD (turn end detection) | ~20 ms |
| STT — OpenAI Whisper | ~200–500 ms |
| LLM — GPT-4.1 (first token) | ~300–600 ms |
| TTS — Cartesia Sonic-2 | ~100–300 ms |
| Audio delivery to browser | ~50 ms |
| **Total end-to-end** | **~700 ms – 1.5 s** |

### Graceful Fallbacks

- **Unclear speech** → Aria asks for clarification politely
- **Unknown order ID** → Aria acknowledges and offers to try again
- **Out-of-scope request** → Aria redirects to supported e-commerce topics
- **API failure** → Aria informs the user and suggests alternatives

---

## Environment Configuration

Create a `.env` file in the project root (copy from `.env_example`):

```bash
# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI  (STT + LLM)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Cartesia  (TTS)
CARTESIA_API_KEY=sk_car_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Obtaining API Keys

| Service | URL |
|---------|-----|
| LiveKit | https://cloud.livekit.io → Project → Settings → Keys |
| OpenAI | https://platform.openai.com/api-keys |
| Cartesia | https://play.cartesia.ai → API Keys |

---

## Installation & Setup

### Prerequisites

- Python 3.11 or 3.12
- Modern browser with microphone access (Chrome recommended)

### Option A — Quick Start (Recommended)

```bash
git clone https://github.com/kumar44a/voxcart.git
cd voxcart
cp .env_example .env
# Fill in your API keys in .env
./start.sh          # auto-creates venv, installs deps, starts both services
```

Open **http://localhost:5001** in your browser.

### Option B — Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate          # macOS/Linux
pip install -r requirements.txt

# Terminal 1 — Token server + frontend
python api.py

# Terminal 2 — Voice agent
python agent.py start
```

### Stopping All Services

```bash
./stop.sh
```

---

## Docker Deployment

```bash
cp .env_example .env          # fill in your API keys
docker compose up --build -d  # build and start
# Open http://localhost:5001
docker compose down           # stop
```

---

## Demo Scenarios

These three scenarios satisfy the Capstone's required deliverables:

### Scenario A — Informational Query (Delivery/Returns)
> *"What is your returns policy if I received the wrong item?"*

Aria calls `get_returns_policy("wrong item")` and explains the 30-day return window with free collection.

### Scenario B — Product-Related Response
> *"Tell me about the Sony WH-1000XM5 headphones."*

Aria calls `lookup_product("Sony WH-1000XM5")` and describes price, stock status, and key features.

### Scenario C — Backend-Style Action (Order Tracking)
> *"Can you check the status of my order ORD-1003?"*

Aria calls `get_order_status("ORD-1003")` and reads back the delivery date and current status.

---

## API Reference

### `GET /getToken`

Mints a LiveKit JWT for a participant.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | `guest` | User display name / identity |
| `language` | string | `en` | Conversation language code |

**Response:**
```json
{ "token": "eyJ...", "room": "room-bf4cfe6e" }
```

---

## Project Structure

```
voxcart/
├── agent.py            # LiveKit voice agent — AI pipeline + tools
├── api.py              # Flask server — JWT tokens + frontend serving
├── mock_data.py        # Synthetic e-commerce data (orders, products, policy)
├── index.html          # Browser voice UI (avatar, transcript, controls)
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image definition
├── docker-compose.yml  # One-command startup
├── start.sh            # Local startup script (auto-creates venv)
├── stop.sh             # Graceful shutdown script
├── get_voices.py       # Utility — list available Cartesia voices
├── .env_example        # Environment variable template
├── .gitignore
├── assets/
│   └── AssistantVoice.gif   # Animated avatar
└── rag/
    ├── faq.txt              # 30-entry FAQ for RAG (shipping, payments, policy)
    └── retriever.py         # Pure-Python TF-IDF retriever — no external deps
```

---

## Troubleshooting

### Port already in use
```bash
lsof -i :5001 | grep LISTEN    # find PID
kill <PID>
```

### SSL certificate error (macOS)
```bash
export SSL_CERT_FILE=$(python3 -c "import certifi; print(certifi.where())")
```

### Agent not connecting to LiveKit
- Verify `LIVEKIT_URL` matches your LiveKit Cloud project exactly (starts with `wss://`)
- Confirm `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` are from the same project

### No audio from bot
- Confirm `OPENAI_API_KEY` and `CARTESIA_API_KEY` are valid and have credits
- Check `logs/agent.log` for stack traces

---

## Capstone Alignment

| Evaluation Criterion | How VoxCart Addresses It |
|----------------------|--------------------------|
| Real-Time Interaction Quality | LiveKit WebRTC + Silero VAD + sub-1.5s pipeline |
| Use of GIAI Concepts | GPT-4.1, system prompting, function calling, RAG |
| System Design | Modular: agent / API / frontend / data / RAG layers |
| Practical Relevance | Three concrete e-commerce scenarios with mock backend |
| Code & Documentation Quality | Typed Python, structured mock data, this README |
| Safety & UX | Explicit fallbacks for unclear input and unsupported requests |
