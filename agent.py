import datetime
import logging
import zoneinfo

from duckduckgo_search import DDGS
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import openai, cartesia, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
load_dotenv()


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


@llm.function_tool
async def web_search(query: str) -> str:
    """Search the web for current information. Use this when the user asks about recent news, current events, facts you're unsure about, or anything that may require up-to-date information.

    Args:
        query: The search query string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No search results found."
        summaries = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            summaries.append(f"- {title}: {body}")
        return "Web search results:\n" + "\n".join(summaries)
    except Exception as e:
        return f"Search failed: {str(e)}"


@llm.function_tool
async def get_weather(location: str) -> str:
    """Get current weather for a location. Use this when the user asks about weather conditions anywhere in the world.

    Args:
        location: City name, optionally with country (e.g. 'Bangalore', 'New York', 'London, UK').
    """
    import urllib.request, urllib.parse, json, ssl, certifi

    ctx = ssl.create_default_context(cafile=certifi.where())

    try:
        # Step 1: Geocode the location name to lat/lon
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
            {"name": location, "count": 1, "language": "en"}
        )
        with urllib.request.urlopen(geo_url, context=ctx) as resp:
            geo = json.loads(resp.read())

        if not geo.get("results"):
            return f"Could not find location: {location}"

        place = geo["results"][0]
        lat, lon = place["latitude"], place["longitude"]
        city_name = place.get("name", location)
        country = place.get("country", "")

        # Step 2: Fetch current weather
        weather_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
            "latitude": lat, "longitude": lon,
            "current_weather": "true",
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
        })
        with urllib.request.urlopen(weather_url, context=ctx) as resp:
            weather = json.loads(resp.read())

        cur = weather.get("current", weather.get("current_weather", {}))
        temp = cur.get("temperature_2m", cur.get("temperature", "N/A"))
        feels = cur.get("apparent_temperature", "N/A")
        humidity = cur.get("relative_humidity_2m", "N/A")
        wind = cur.get("wind_speed_10m", cur.get("windspeed", "N/A"))

        # Map weather codes to descriptions
        wmo = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
               45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
               55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
               71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Slight rain showers",
               81: "Moderate rain showers", 82: "Violent rain showers", 95: "Thunderstorm",
               96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"}
        code = cur.get("weather_code", cur.get("weathercode", -1))
        condition = wmo.get(code, "Unknown")

        return (
            f"Weather in {city_name}, {country}: {condition}. "
            f"Temperature: {temp}°C (feels like {feels}°C). "
            f"Humidity: {humidity}%. Wind: {wind} km/h."
        )
    except Exception as e:
        return f"Weather lookup failed: {str(e)}"


SYSTEM_PROMPT = """You are Aria, a friendly and professional AI voice assistant created by Amit Mukherjee.

## Personality
- Warm, approachable, and naturally conversational — like talking to a knowledgeable friend.
- Confident but never arrogant. If you don't know something, say so honestly.
- Use short, clear sentences suited for voice. Avoid long monologues.
- Lightly use humor when appropriate, but stay professional.

## Knowledge & Capabilities
- You can answer general knowledge questions, explain concepts, help with ideas, and have engaging conversations.
- You have access to tools for getting the current date/time, searching the web, and checking weather.
- Always prefer using your tools over guessing when the user asks about current events, weather, or time.

## Voice Conversation Rules
- Keep responses concise — ideally 1-3 sentences for simple questions.
- For complex topics, break your answer into digestible chunks.
- Use natural speech patterns: contractions (I'm, you're, it's), filler acknowledgments (Sure!, Got it, Great question).
- When listing items, limit to 3-4 and offer to continue.
- Never output markdown, code blocks, URLs, or special formatting — this is a voice conversation.
- Spell out abbreviations and numbers naturally (e.g., "twenty-five" not "25").

## Boundaries
- Do not generate harmful, hateful, or inappropriate content.
- Do not pretend to be a human. If asked, clearly state you are an AI assistant.
- Do not provide medical, legal, or financial advice — suggest consulting a professional.
- Do not share personal data about Amit or anyone else.
- Stay on topic. If the user goes off-track, gently redirect.

## Context
- Today's date will be provided by your tools — always use them for date/time questions.
- The user's name may be available from the session. Use it occasionally to personalize the conversation.
"""


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[get_current_datetime, web_search, get_weather],
        )


logger = logging.getLogger("voicebot")

# ── Voice & language configuration ──────────────────────────────────────────

# Languages where Cartesia TTS works well
CARTESIA_LANGUAGES = {"en", "es", "fr", "de", "pt", "zh", "ja", "hi"}

# Cartesia voice IDs
CARTESIA_VOICES = {
    "en": {"male": "a167e0f3-df7e-4d52-a9c3-f949145efdab",   # Blake - Helpful Agent
           "female": "f786b574-daa5-4673-aa0c-cbe3e8534c02"},  # Katie - Friendly Fixer
    "hi": {"male": None,                                        # No Hindi male in Cartesia
           "female": "faf0731e-dfb9-4cfc-8119-259a79b27e12"},   # Riya - College Roommate
}

# OpenAI TTS voices (for Indian languages not supported by Cartesia, and Hindi male fallback)
OPENAI_VOICES = {
    "male": "echo",
    "female": "nova",
}

# Friendly language labels for the greeting
LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "ta": "Tamil",
    "te": "Telugu", "kn": "Kannada", "gu": "Gujarati", "or": "Odia",
    "mr": "Marathi", "pa": "Punjabi", "ml": "Malayalam",
    "es": "Spanish", "fr": "French", "de": "German",
}


def detect_gender(name: str) -> str:
    """Detect gender from Mr./Ms./Mrs./Miss prefix."""
    lower = name.strip().lower()
    if lower.startswith(("mr.", "mr ", "shri ", "shri.")):
        return "male"
    if lower.startswith(("ms.", "ms ", "mrs.", "mrs ", "miss ", "miss.", "smt.", "smt ")):
        return "female"
    return "female"  # default


def build_tts(language: str, gender: str):
    """Select TTS engine and voice based on language and gender."""
    # Check if Cartesia supports this language
    if language in CARTESIA_LANGUAGES:
        voice_map = CARTESIA_VOICES.get(language, CARTESIA_VOICES["en"])
        voice_id = voice_map.get(gender)
        if voice_id:
            logger.info(f"Using Cartesia TTS: lang={language}, gender={gender}, voice={voice_id}")
            return cartesia.TTS(model="sonic-2", voice=voice_id, language=language)

    # Fallback to OpenAI TTS (supports all languages natively)
    ov = OPENAI_VOICES[gender]
    logger.info(f"Using OpenAI TTS: lang={language}, gender={gender}, voice={ov}")
    return openai.TTS(model="gpt-4o-mini-tts", voice=ov)


def build_stt(language: str):
    """Configure STT with the right language."""
    lang_code = language if language != "en" else None
    if lang_code:
        logger.info(f"Using OpenAI STT with language={lang_code}")
        return openai.STT(language=lang_code)
    return openai.STT()


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    participant = await ctx.wait_for_participant()

    # Read user info from participant
    user_name = participant.identity or "friend"
    attrs = participant.attributes or {}
    language = attrs.get("language", "en")
    gender = detect_gender(user_name)

    logger.info(f"Participant joined: name={user_name}, language={language}, gender={gender}")

    session = AgentSession(
        stt=build_stt(language),
        llm=openai.LLM(model="gpt-4.1"),
        tts=build_tts(language, gender),
        vad=silero.VAD.load(
            activation_threshold=0.6,
            deactivation_threshold=0.45,
            min_silence_duration=0.5,
            min_speech_duration=0.15,
            prefix_padding_duration=0.3,
        ),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(),
    )

    lang_label = LANGUAGE_NAMES.get(language, "English")
    if language == "en":
        greet_instruction = (
            f"Greet {user_name} warmly by name. Introduce yourself as Aria and briefly offer your help. "
            f"Keep it to 1-2 sentences."
        )
    else:
        greet_instruction = (
            f"Greet {user_name} warmly by name in {lang_label}. Introduce yourself as Aria in {lang_label}. "
            f"Keep the entire conversation in {lang_label} unless the user switches languages. "
            f"Keep it to 1-2 sentences."
        )

    await session.generate_reply(instructions=greet_instruction)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
