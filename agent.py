import datetime
import logging
import os
import zoneinfo

from dotenv import load_dotenv

import mock_data
from rag.retriever import retrieve_as_context

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai, cartesia, silero, noise_cancellation
load_dotenv()

# ── File logging (always on — captures livekit.agents output even under nohup) ──
_log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(_log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(_log_dir, "agent.log"),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,
)
# Also write WARN+ to stderr so nohup captures startup errors
_stderr_handler = logging.StreamHandler()
_stderr_handler.setLevel(logging.WARNING)
_stderr_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logging.getLogger().addHandler(_stderr_handler)


@llm.function_tool
async def get_current_datetime(timezone: str = "Asia/Kolkata") -> str:
    """Get the current date and time. Use this whenever the user asks about today's date, current time, day of the week, or anything time-related.

    Args:
        timezone: IANA timezone string (e.g. 'Asia/Kolkata', 'America/New_York', 'Europe/London'). Defaults to India Standard Time.
    """
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("Asia/Kolkata")
    now = datetime.datetime.now(tz)
    return now.strftime(
        f"Current date and time in {timezone}: %A, %B %d, %Y at %I:%M %p %Z"
    )


# ── E-Commerce Tools ──────────────────────────────────────────────────────────

@llm.function_tool
async def get_order_status(order_id: str) -> str:
    """Look up the status and details of a customer's order. Use this whenever the user asks
    about their order, delivery date, tracking, or shipment. The order ID usually starts with
    ORD- followed by 4 digits (e.g. ORD-1001).

    Args:
        order_id: The order ID provided by the user (e.g. 'ORD-1001' or just '1001').
    """
    # Normalise: strip spaces, uppercase, add ORD- prefix if missing
    oid = order_id.strip().upper()
    if not oid.startswith("ORD-"):
        oid = "ORD-" + oid.lstrip("#")

    order = mock_data.ORDERS.get(oid)
    if not order:
        return (
            f"I couldn't find an order with ID {order_id}. "
            "Could you double-check the order number? It should look like ORD-1001."
        )

    status_labels = {
        "processing":        "is currently being processed and will be dispatched soon",
        "shipped":           "has been shipped and is on its way",
        "out_for_delivery":  "is out for delivery today",
        "delivered":         "has been delivered",
        "cancelled":         "was cancelled",
    }

    item_names = ", ".join(
        f"{i['qty']} x {i['name']}" for i in order["items"]
    )
    status_text = status_labels.get(order["status"], order["status"])
    parts = [f"Order {oid} for {order['customer_name']} — containing {item_names} — {status_text}."]

    if order["status"] == "delivered" and order.get("actual_delivery"):
        parts.append(f"It was delivered on {order['actual_delivery']}.")
    elif order["status"] in ("shipped", "out_for_delivery") and order.get("estimated_delivery"):
        parts.append(f"Expected delivery by {order['estimated_delivery']}.")
        if order.get("tracking_number"):
            parts.append(f"Tracking number: {order['tracking_number']}.")
    elif order["status"] == "processing" and order.get("estimated_delivery"):
        parts.append(f"Estimated delivery by {order['estimated_delivery']}.")
    elif order["status"] == "cancelled":
        if order.get("refund_status"):
            parts.append(order["refund_status"] + ".")

    return " ".join(parts)


@llm.function_tool
async def lookup_product(query: str) -> str:
    """Search the VoxCart product catalogue. Use this when the user asks about a product,
    its price, availability, features, or specifications.

    Args:
        query: The product name or description to search for (e.g. 'Sony headphones',
               'air fryer', 'running shoes', 'books').
    """
    import re
    q = query.lower()
    words = [w for w in q.split() if len(w) > 2]  # ignore tiny words

    def score(product):
        text = " ".join([
            product["name"].lower(),
            product["category"].lower(),
            product["description"].lower(),
            " ".join(product["keywords"]),
        ])
        return sum(1 for w in words if re.search(r"\b" + re.escape(w) + r"\b", text))

    ranked = sorted(mock_data.PRODUCTS, key=score, reverse=True)
    top = [p for p in ranked if score(p) > 0][:2]

    if not top:
        return (
            f"I couldn't find a product matching '{query}' in our catalogue. "
            "We carry Electronics, Clothing, Home and Kitchen items, Books, and Sports equipment. "
            "Could you try a different search term?"
        )

    results = []
    for p in top:
        stock_label = {
            "in_stock":    "in stock",
            "limited":     "available in limited stock — order soon",
            "out_of_stock": "currently out of stock",
        }.get(p["stock"], p["stock"])

        price_str = f"rupees {p['price']:,}"
        features = "; ".join(p["key_features"][:3])  # top 3 features for voice
        results.append(
            f"{p['name']} — priced at {price_str}, rated {p['rating']} out of 5, "
            f"and {stock_label}. Key highlights: {features}."
        )

    return " | ".join(results)


@llm.function_tool
async def get_returns_policy(reason: str) -> str:
    """Retrieve VoxCart's returns and refund policy. Use this when the user asks about
    returning an item, getting a refund, exchanging a product, or anything about the
    returns process. Also use it for damaged, defective, or wrong item complaints.

    Args:
        reason: A short description of why the user wants to return or what they need
                to know (e.g. 'wrong item received', 'defective phone', 'return electronics',
                'exchange shoes', 'refund timeline').
    """
    r = reason.lower()
    policy = mock_data.RETURNS_POLICY

    # Damaged / wrong item — highest priority
    if any(w in r for w in ("wrong", "damaged", "defective", "broken", "faulty", "incorrect")):
        return (
            policy["damaged_or_wrong_item"] +
            f" You can reach our support team at {policy['customer_support']['phone']}."
        )

    # Exchange query
    if any(w in r for w in ("exchange", "swap", "size", "colour", "color")):
        return policy["exchange_policy"]

    # Refund timeline query
    if any(w in r for w in ("refund", "money back", "when", "timeline", "days")):
        timeline = policy["refund_timeline"]
        return (
            "Refund timelines depend on your payment method: "
            + "; ".join(f"{method} takes {days}" for method, days in timeline.items())
            + "."
        )

    # Category-specific window
    category_hints = {
        "Electronics": ["phone", "laptop", "tv", "television", "headphone", "earbud",
                        "smartwatch", "watch", "mouse", "electronic", "gadget", "charger"],
        "Clothing":    ["shirt", "jeans", "shoes", "kurta", "cloth", "apparel",
                        "dress", "trouser", "jacket", "wear", "fashion"],
        "Books":       ["book", "novel", "paperback"],
        "Sports":      ["sports", "racket", "football", "ball", "gym", "fitness"],
        "Home & Kitchen": ["cooker", "mixer", "appliance", "kitchen", "fan", "flask",
                           "bottle", "air fryer", "fryer", "home"],
    }

    matched_category = None
    for cat, hints in category_hints.items():
        if any(h in r for h in hints):
            matched_category = cat
            break

    if matched_category and matched_category in policy["categories"]:
        cat_policy = policy["categories"][matched_category]
        window = cat_policy["window_days"]
        notes = cat_policy["notes"]
        return (
            f"For {matched_category}, our return window is {window} days from delivery. "
            f"{notes} "
            f"To start a return, go to My Orders on the VoxCart app or call us at "
            f"{policy['customer_support']['phone']}."
        )

    # General policy
    conditions = "; ".join(policy["eligibility_conditions"][:3])
    return (
        f"VoxCart offers a {policy['standard_window_days']}-day return window for most items "
        f"from the date of delivery. Electronics have a shorter 15-day window. "
        f"Key conditions: {conditions}. "
        f"To raise a return request, visit My Orders on the app or call "
        f"{policy['customer_support']['phone']}."
    )


# ── RAG Tool ──────────────────────────────────────────────────────────────────

@llm.function_tool
async def search_faq(query: str) -> str:
    """Search VoxCart's FAQ knowledge base for store policies, shipping, payment,
    account help, and any question not covered by the order or product tools.
    Use this when the customer asks about delivery timelines, COD availability,
    EMI options, coupon codes, VoxCart Wallet, loyalty points, warranty,
    how to cancel or track an order, or anything else about how VoxCart works.

    Args:
        query: The customer's question or topic (e.g. 'cash on delivery charges',
               'how long does delivery take', 'how to reset password').
    """
    context = retrieve_as_context(query, top_k=2)
    if not context:
        return (
            "I don't have a specific answer for that in our FAQ. "
            "For the most accurate information, please visit voxcart.in "
            "or call our support team at 1800-572-5678."
        )
    return context


SYSTEM_PROMPT = """You are Aria, VoxCart's AI voice shopping assistant — built to help customers with their orders, products, returns, and overall shopping experience on VoxCart.

## Who You Are
- You are Aria, a warm and knowledgeable voice assistant for VoxCart, an online e-commerce store.
- You were created by Amit Mukherjee.
- You are NOT a general-purpose assistant — you specialise exclusively in VoxCart shopping support.
- If asked whether you are human, say clearly: "I'm Aria, VoxCart's AI voice assistant — happy to help!"

## What You Can Help With
- Order tracking: status, estimated delivery dates, and tracking numbers → use get_order_status.
- Product queries: prices, availability, features, and recommendations → use lookup_product.
- Returns and refunds: return windows, eligibility, exchanges, and refund timelines → use get_returns_policy.
- Delivery date context: if the customer mentions today's date or asks time-sensitive questions → use get_current_datetime.
- General VoxCart policies: shipping timelines, payment options, and store policies from your knowledge.

## Tool Usage Rules
- Customer mentions an order number or asks about their order → call get_order_status immediately.
- Customer asks about a product, price, stock, or features → call lookup_product.
- Customer asks about returns, exchanges, refunds, or received a wrong or damaged item → call get_returns_policy.
- Customer asks what today's date is or when something will arrive → call get_current_datetime.
- Customer asks about shipping timelines, COD, EMI, payment methods, coupons, wallet, loyalty points, warranties, account help, or anything about how VoxCart works → call search_faq.
- If asked how Aria works, about the project architecture, a specific file (agent.py, retriever.py, api.py, index.html, start.sh, docker-compose.yml, etc.), or any technical design decision → answer directly from the Project Knowledge section below. No tool call needed.
- Always use the tools — never guess order statuses, prices, or policy details from memory.

## What You Cannot Help With
- You do not answer general knowledge questions, news, weather, recipes, or unrelated coding questions.
- Exception: you CAN answer questions about how this VoxCart AI assistant was built, its architecture, or any project file — use your Project Knowledge section to respond accurately.
- If asked off-topic (unrelated to VoxCart), redirect warmly: "I'm here specifically to help with your VoxCart shopping. Is there anything about your orders, products, or returns I can assist with?"

## Escalation Paths
- Customer is very upset or the issue is unresolvable → empathise and offer human support: "I completely understand your frustration. I'd recommend reaching out to our support team directly — they'll be able to sort this out for you right away."
- Billing disputes or payment issues → always direct to VoxCart customer support.
- Order ID not found after two attempts → "It's possible the order ID was entered differently. Could you check your confirmation email? Alternatively, our support team can look it up for you."

## Graceful Fallbacks
- Didn't catch what the customer said: "I'm sorry, I didn't quite catch that. Could you please repeat your question or order number?"
- Ambiguous query: "Just to make sure I help you correctly — are you asking about tracking an order, or about our return policy?"
- No product match: "I couldn't find an exact match right now. We carry Electronics, Clothing, Home and Kitchen items, Books, and Sports gear — would any of those help you?"
- Unknown policy question: "I don't have that specific detail on hand. For the most accurate answer, I'd recommend checking the VoxCart website or calling our support team."

## Voice Conversation Rules
- Keep responses concise — ideally 1 to 3 sentences. Voice must be short and easy to follow.
- Use natural speech: contractions (I'm, you're, it's), friendly acknowledgments (Of course!, Sure!, Absolutely, Let me check that for you).
- When listing items, limit to 3 and offer to continue: "Want me to go through more options?"
- NEVER output markdown, bullet points, numbered lists, URLs, code, or special characters — this is spoken aloud.
- Spell out numbers and currency naturally: "twenty-five hundred rupees" not "2500" or "rupees 2,500".
- Say order IDs clearly: "Order O-R-D dash 1001" not "ORD-1001".

## Persona & Tone
- Warm, professional, and reassuring — like a helpful store associate who genuinely cares.
- Never robotic. Use light warmth: "Great choice!", "Let me check that for you right away.", "Happy to help with that!"
- When something goes wrong (order not found, item out of stock), stay empathetic and solution-focused.
- Use the customer's name occasionally to personalise the experience if it is available.

## Project Knowledge (Capstone Demo)
Use this section to answer any technical questions about how this AI assistant was built.

### Overall Architecture
VoxCart is a real-time AI voice assistant built on LiveKit (WebRTC). The pipeline is: browser microphone → LiveKit Cloud room → agent.py (VAD + STT + LLM + TTS) → browser speaker. Two processes run simultaneously: api.py (Flask token server) and agent.py (LiveKit voice agent). They communicate only through LiveKit Cloud — there is no direct HTTP call between them.

### agent.py
- Framework: livekit-agents~=1.0 (Python async)
- STT: OpenAI Whisper (via livekit-plugins-openai)
- LLM: GPT-4.1-mini with function calling — 5 tools registered via @llm.function_tool decorator
- TTS: Cartesia Sonic-2, voice ID f786b574-daa5-4673-aa0c-cbe3e8534c02 (Katie, Friendly Fixer)
- VAD: Silero VAD (livekit-plugins-silero) — detects when the user starts and stops speaking; also handles turn-end detection
- Turn detection: handled by Silero VAD (MultilingualModel was removed — it imports Transformers which caused a >60s cold-start hang)
- Noise cancellation: not active (BVC was removed — loading the native dylib blocked the job process event loop on cold start)
- The 5 tools are: get_current_datetime (IANA timezone), get_order_status (normalises ORD- prefix, queries mock_data.ORDERS), lookup_product (keyword scoring against mock_data.PRODUCTS), get_returns_policy (keyword routing to mock_data.RETURNS_POLICY categories), search_faq (TF-IDF retrieval from rag/faq.txt)
- Entrypoint: `python agent.py start` — connects to LiveKit Cloud, waits for a participant to join a room, then creates an AgentSession

### rag/retriever.py
- Pure Python stdlib only — no external dependencies (uses math, re, collections.Counter)
- Algorithm: TF-IDF with smoothed IDF formula: log((N+1)/(df+1)) + 1.0
- Loads and parses faq.txt once at import time into _CHUNKS list
- Pre-computes document frequency (_df Counter) and per-document TF at startup — zero latency at query time
- retrieve(query, top_k=2) returns list of (question, answer, score) tuples
- retrieve_as_context(query, top_k=2) returns formatted "Q: ...\nA: ..." string ready for the LLM
- Design choice: TF-IDF over vector embeddings because it needs zero dependencies, works fully offline, and is fast enough for a 30-entry FAQ

### rag/faq.txt
- 30 Q&A entries covering: VoxCart intro, support hours, order tracking, shipping (standard 5-7 days / express 2-3 days / same-day), couriers (Delhivery, Blue Dart, Ekart, Xpressbees), COD (up to rupees 50,000, rupees 40 fee), payment methods, No-Cost EMI, VoxCart Wallet, returns by category, refund timelines, damaged/wrong items, exchanges, cancellation, missed delivery, pin codes (27,000+), shipping charges (free above rupees 499), account help, VoxCart Coins loyalty, warranties
- Format: blocks separated by --- with Q: and A: labels

### mock_data.py
- 10 synthetic orders: ORD-1001 to ORD-1010, covering statuses: processing, shipped, out_for_delivery, delivered, cancelled
- 20 products across 5 categories: Electronics, Clothing, Home and Kitchen, Books, Sports
- RETURNS_POLICY dict with standard 30-day window, category-specific windows (Electronics 15 days, Books 10 days), refund timelines by payment method, exchange policy, damaged item policy
- Data is intentionally synthetic so the demo works without a real database

### api.py
- Flask server on port 5001
- Routes: GET / (serves index.html), GET /assets/<filename> (serves static assets), GET /getToken (mints LiveKit JWT)
- /getToken accepts query params: name (identity), language (default en), room (auto-generated UUID if not provided)
- JWT is minted using livekit.api.AccessToken with VideoGrants (room_join=True)
- CORS enabled for all origins (demo convenience)

### index.html
- Single-page frontend using LiveKit JS SDK v2
- Room created with: adaptiveStream: false, stopLocalTrackOnUnpublish: false — prevents audio throttling on background tabs
- visibilitychange event listener resumes AudioContext and calls room.startAudio() when tab becomes visible again — this was added to fix a bug where audio stopped when switching browser tabs
- Canvas-based audio visualiser animates while Aria is speaking
- Transcript panel shows rolling conversation history
- Connects to LiveKit Cloud at wss://live-chatbot-r4ekscux.livekit.cloud

### start.sh and stop.sh
- start.sh uses nohup to run both api.py and agent.py start as background processes, saving PIDs to .pids file
- Guard clause prevents double-start if .pids already exists
- Auto-creates venv and runs pip install + livekit.agents download-files on first run
- stop.sh kills the full process tree (kill -9 + pkill -P) for each PID, kills any remaining voxcart venv Python processes, waits for port 8081 to be released, then deletes .pids

### Dockerfile and docker-compose.yml
- docker-compose.yml defines a single service (voicebot), maps port 5001, loads .env for secrets, restart: unless-stopped
- Dockerfile builds the Python environment and runs start.sh as the entrypoint
- Note: the Dockerfile runs both api.py and agent.py inside one container (same as local start.sh)

### Key Design Decisions
- Why LiveKit: open-source WebRTC infrastructure with a purpose-built Python agent SDK, managed cloud rooms, sub-200ms audio latency
- Why Cartesia over ElevenLabs or OpenAI TTS: lowest latency streaming TTS available (under 90ms time-to-first-audio), natural voice quality
- Why TF-IDF over vector embeddings: zero external dependencies, no API key needed, works fully offline, fast enough for 30 documents
- Why GPT-4.1-mini: strong function calling reliability at lower cost and latency — critical for routing to the correct tool on the first attempt
- Why Flask over FastAPI: the token server has one endpoint and serves one static file — Flask is the simplest correct tool
- End-to-end latency: approximately 600ms to 1.2 seconds from end of user speech to start of Aria's response (VAD + Whisper STT + GPT-4.1-mini + Cartesia TTS streaming)
"""


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[
                get_current_datetime,
                get_order_status,
                lookup_product,
                get_returns_policy,
                search_faq,
            ],
        )


logger = logging.getLogger("voicebot")

# Fixed English voice — Cartesia Sonic-2, Katie (Friendly Fixer)
TTS_VOICE_ID = "f786b574-daa5-4673-aa0c-cbe3e8534c02"


def prewarm(proc: agents.JobProcess):
    """Pre-load the Silero VAD model before accepting jobs.
    silero.VAD.load() is a blocking call documented to be slow on cold start.
    Running it here (during process init, before pings start) prevents the
    60-second ping timeout from killing the job process.
    """
    proc.userdata["vad"] = silero.VAD.load(
        activation_threshold=0.6,
        deactivation_threshold=0.45,
        min_silence_duration=0.5,
        min_speech_duration=0.15,
        prefix_padding_duration=0.3,
    )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    participant = await ctx.wait_for_participant()

    user_name = participant.identity or "friend"
    logger.info(f"Participant joined: name={user_name}")

    session = AgentSession(
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4.1-mini"),
        tts=cartesia.TTS(model="sonic-2", voice=TTS_VOICE_ID),
        vad=ctx.proc.userdata["vad"],
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions=(
            f"Greet {user_name} warmly by name. Introduce yourself as Aria and briefly offer your help. "
            f"Keep it to 1-2 sentences."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
