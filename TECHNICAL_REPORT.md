# VoxCart Technical Report

## Problem Overview and Scope

VoxCart is a real-time voice assistant prototype for e-commerce support. The goal is to let a customer speak naturally through a browser microphone, route the request through a speech-to-text, LLM, tool-calling, and text-to-speech pipeline, and receive a spoken response without typing or page refreshes.

The project focuses on three high-value support flows:

- Informational policy questions, such as delivery, returns, refunds, COD, EMI, and warranty.
- Product-related questions, including price, availability, rating, and key features.
- Backend-style order tracking using synthetic order data.

The prototype intentionally uses mock data rather than real customer records. This keeps the demo self-contained while still exercising realistic e-commerce workflows.

## System Architecture and Real-Time Flow

The system has three main runtime components:

- `index.html`: browser voice interface with microphone capture, LiveKit connection, bot audio playback, avatar state, and transcript display.
- `api.py`: Flask server that serves the frontend and mints LiveKit participant JWTs.
- `agent.py`: LiveKit agent that receives user audio, performs STT, sends the transcript to the LLM, executes e-commerce tools, and streams TTS audio back to the room.

The real-time flow is:

1. The user opens the browser UI and clicks Join.
2. The frontend calls `GET /getToken` to receive a LiveKit JWT and room name.
3. The browser joins the LiveKit Cloud room and publishes the microphone track.
4. The LiveKit agent joins the same room and listens to the user's audio.
5. Silero VAD detects speech boundaries.
6. OpenAI STT transcribes the user request.
7. GPT-4.1-mini interprets the request and either answers directly from project knowledge or calls one of the registered tools.
8. Tool results are grounded in `mock_data.py` or `rag/faq.txt`.
9. Cartesia Sonic-2 synthesizes the response.
10. LiveKit streams the bot audio back to the browser.

## Prompt Design and Reasoning Logic

The system prompt defines Aria as a VoxCart-specific shopping assistant, not a general-purpose chatbot. It constrains the assistant to e-commerce support and project-architecture questions, and asks it to redirect unrelated requests.

The prompt also defines tool routing rules:

- Order status, shipment, or tracking requests call `get_order_status`.
- Product price, stock, feature, or recommendation requests call `lookup_product`.
- Return, refund, exchange, wrong-item, or damaged-item requests call `get_returns_policy`.
- Date and time-sensitive requests call `get_current_datetime`.
- General store-policy questions call `search_faq`.

This structure keeps answers grounded in deterministic code and mock data instead of relying only on model memory. The tools act as the reasoning boundary for business facts.

## STT, TTS, and Latency Considerations

The prototype uses LiveKit WebRTC for low-latency audio transport, OpenAI STT for transcription, GPT-4.1-mini for response planning and tool calling, and Cartesia Sonic-2 for low-latency voice synthesis.

The expected latency budget is:

- Browser audio capture and LiveKit transport: about 50 ms.
- VAD and turn detection: about 20 ms plus silence threshold.
- STT: about 200 to 500 ms.
- LLM first response/tool routing: about 300 to 600 ms.
- TTS first audio: about 100 to 300 ms.
- Audio return to browser: about 50 ms.

The target end-to-end response time is roughly 700 ms to 1.5 seconds after the user finishes speaking.

The implementation preloads Silero VAD in `prewarm()` so the agent avoids slow first-request startup. Heavier turn-detector and noise-cancellation options were avoided in the current build because they introduced cold-start and native-library delays during local demo runs.

## Limitations

- The backend data is synthetic; there is no real customer account, payment, or order database.
- `/getToken` has no user authentication and is suitable only for demo use.
- CORS is open for local/demo convenience.
- There is no production moderation layer or output validator.
- Order lookup is based only on order ID and does not verify customer ownership.
- The language selector is present for future expansion, but the assistant is optimized for English.
- Docker deployment depends on external API keys and LiveKit connectivity.

## Future Improvements

- Add user authentication before minting LiveKit tokens.
- Add customer ownership checks for order lookups.
- Add rate limiting and stricter CORS configuration.
- Add moderation, prompt-injection checks, and output validation.
- Replace mock data with a real e-commerce API or database.
- Add automated tests for tool routing and API behavior.
- Expand multilingual support and validate STT/TTS quality across accents.
- Add richer analytics for latency, tool calls, fallback rate, and task completion.
