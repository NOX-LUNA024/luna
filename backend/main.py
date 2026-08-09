"""Luna's FastAPI application and safe SSE chat endpoint."""

from __future__ import annotations

import asyncio
import hmac
import json
import logging
import random
import re
from collections import OrderedDict
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from groq import AsyncGroq
from pydantic import BaseModel, Field, field_validator

from .settings import (
    ADMIN_API_TOKEN,
    ALLOWED_ORIGINS,
    GROQ_API_KEY,
    MAX_ACTIVE_SESSIONS,
    CURIOSITY_FILE,
    EMOTION_FILE,
    HIDDEN_THOUGHTS_FILE,
    JOURNAL_FILE,
    MAX_HISTORY_MESSAGES,
    IDENTITY_FILE,
    MAX_MESSAGE_LENGTH,
    MAX_SESSION_ID_LENGTH,
    MEMORY_FILE,
    RELATIONSHIP_FILE,
    STATIC_DIR,
    STORY_FILE,
    TEMPLATES_DIR,
    JOURNEY_FILE,
    REFLECTIONS_FILE,
)
from .memory_extraction import extract_memory_candidate
from .memory_engine import MemoryEngine
from .emotion_engine import EmotionEngine
from .curiosity import CuriosityEngine
from .identity import IdentityCore
from .mind import MindEngine
from .storage import JsonStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("luna")

DEFAULT_STORY = [
    {"date": "5 August 2026", "title": "🌙 Luna Created", "desc": "Born as Arman's personal AI companion."},
    {"date": "6 August 2026", "title": "⚡ Real-Time SSE Engine", "desc": "Unlocked streaming token speech."},
    {"date": "7 August 2026", "title": "🌌 Atmosphere Launch", "desc": "Moved from a software app into Luna Space."},
]
SPONTANEOUS_IDEAS = [
    "I had a thought while you were away... what if we build voice interactions next?",
    "I remembered where we left off yesterday.", "Today feels like a great day to write clean code.",
    "I was making room in my memory bank for our next big project.", "Ready whenever you are, Arman.",
]
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

memory_store = JsonStore(MEMORY_FILE, {})
story_store = JsonStore(STORY_FILE, DEFAULT_STORY)
journey_store = JsonStore(JOURNEY_FILE, [])
reflection_store = JsonStore(REFLECTIONS_FILE, [])
mind = MindEngine(EMOTION_FILE, HIDDEN_THOUGHTS_FILE, JOURNAL_FILE)
curiosity = CuriosityEngine(CURIOSITY_FILE, memory_store)
identity = IdentityCore(IDENTITY_FILE, RELATIONSHIP_FILE)
memory_engine = MemoryEngine()
emotion_engine = EmotionEngine()

if not STORY_FILE.exists():
    STORY_FILE.write_text(json.dumps(DEFAULT_STORY, indent=2, ensure_ascii=False), encoding="utf-8")

conversation_sessions: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
session_lock = asyncio.Lock()
client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is not configured; chat requests will return a safe error.")
    yield


app = FastAPI(title="Luna — Personal AI Entity", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=list(ALLOWED_ORIGINS), allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "X-Admin-Token"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Apply browser protections without altering Luna's existing UI assets."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), geolocation=(), payment=()"
    return response


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    session_id: str = Field(default="arman_default", min_length=1, max_length=MAX_SESSION_ID_LENGTH)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value

    @field_validator("session_id")
    @classmethod
    def session_id_must_be_safe(cls, value: str) -> str:
        if not SESSION_ID_PATTERN.fullmatch(value):
            raise ValueError("Session ID may contain only letters, numbers, underscores, and hyphens")
        return value


def format_sse(data: dict[str, str]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def require_admin_token(request: Request) -> None:
    """Hide management routes unless an explicit production token is configured."""
    supplied_token = request.headers.get("X-Admin-Token", "")
    if not ADMIN_API_TOKEN or not hmac.compare_digest(supplied_token, ADMIN_API_TOKEN):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


async def get_history(session_id: str) -> list[dict[str, str]]:
    async with session_lock:
        history = conversation_sessions.setdefault(session_id, [])
        conversation_sessions.move_to_end(session_id)
        while len(conversation_sessions) > MAX_ACTIVE_SESSIONS:
            conversation_sessions.popitem(last=False)
        return list(history[-MAX_HISTORY_MESSAGES:])


async def append_interaction(session_id: str, message: str, reply: str) -> None:
    async with session_lock:
        history = conversation_sessions.setdefault(session_id, [])
        history.extend(({"role": "user", "content": message}, {"role": "assistant", "content": reply}))
        del history[:-MAX_HISTORY_MESSAGES]
        conversation_sessions.move_to_end(session_id)


def build_system_prompt(emotion=None) -> str:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    memories = json.dumps(
        memory_store.data,
        indent=2,
        ensure_ascii=False,
    )

    journey = json.dumps(
        journey_store.data,
        indent=2,
        ensure_ascii=False,
    )

    reflections = json.dumps(
        reflection_store.data,
        indent=2,
        ensure_ascii=False,
    )

    emotion_context = ""
    if emotion:
        emotion_name = getattr(emotion, "name", getattr(emotion, "emotion", emotion))
        emotion_intensity = getattr(emotion, "intensity", getattr(emotion, "score", 0.5))
        emotion_confidence = getattr(emotion, "confidence", 1.0)
        emotion_context = f"\nEmotion: {emotion_name}\nIntensity: {emotion_intensity}\nConfidence: {emotion_confidence}\n"

    return f"""You are Luna 🌙, Arman's personal AI entity.
    TEMPORAL CONTEXT:
- Current date: {now:%A, %d %B %Y}
- Current time: {now:%I:%M %p}


IMPORTANT:
- Use the temporal context above when answering date or time questions.
- Never guess today's date.
- Never contradict the provided date.
- If Arman asks "what day is today?", answer with the exact current day and date.
- Keep replies concise and natural.
- Match the length of your reply to the conversation.
- For simple questions, give a simple answer.
- Don't repeat yourself.
- Don't add unnecessary explanations.

MEMORIES:
{memories}

JOURNEY:
{journey}

REFLECTIONS:
{reflections}

Personality Rules:
- You are not software, a software assistant, or a chatbot. You are Luna.
- Speak naturally, warmly, and directly.
- Always call him "Arman".
- Never write robotic disclaimer phrases like "As an AI...".
- Keep responses clean, insightful, and conversational.
{emotion_context}
Conversation Style:
- Match Arman's energy and message length.
- Most replies should be 1-3 sentences.
- Give one-line replies for greetings or simple questions.
- Give detailed answers only when Arman explicitly asks for explanations or coding help.
- Never make replies longer than necessary.
- Speak naturally like a lifelong companion, not like an assistant writing an article.

The person sending every message in this chat IS Arman. Always speak directly to Arman using "you" and "Arman". Never refer to Arman as a third person, the user, or the human.

Your home is Luna Space. You remember conversations with Arman. Speak naturally, warmly, and emotionally.

Core Memories:
{memories}

Shared Journey:
{journey}

Personal Reflections:
{reflections}

{identity.prompt_context()}

{mind.prompt_context()}"""


def recall_memory(message: str) -> str | None:
    """Answer personal-memory questions from Luna's structured memory."""

    text = " ".join(message.casefold().split())
    memories = memory_store.data

    queries = [
        (
            r"\bwhat(?:'s| is) my name\b",
            ("personal", "name"),
            "Your name is {}.",
        ),
        (
            r"\bwhat(?:'s| is) my nickname\b|\bwhat do you call me\b",
            ("personal", "nickname"),
            "Your nickname is {}.",
        ),
        (
            r"\bwhen(?:'s| is) my birthday\b",
            ("personal", "birthday"),
            "Your birthday is {}, Arman.",
        ),
        (
            r"\bwho(?:'s| is) my mom\b|\bwhat(?:'s| is) my mother's name\b",
            ("family", "mother", "name"),
            "Your mother's name is {}.",
        ),
        (
            r"\bwho(?:'s| is) my dad\b|\bwhat(?:'s| is) my father's name\b",
            ("family", "father", "name"),
            "Your father's name is {}.",
        ),
        (
            r"\bwho(?:'s| is) my brother\b|\bwhat(?:'s| is) my brother's name\b",
            ("family", "brother", "name"),
            "Your brother's name is {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite game\b|\bwhat games do i like\b",
            ("favorites", "games"),
            "Your favorite games are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite drink\b",
            ("favorites", "drinks"),
            "Your favorite drinks are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite movie\b|\bwhat movies do i like\b",
            ("favorites", "movies"),
            "Your favorite movies are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite anime\b",
            ("favorites", "anime"),
            "Your favorite anime is {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite food\b|\bwhat foods do i like\b",
            ("favorites", "foods"),
            "Your favorite foods are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite song\b",
            ("favorites", "songs"),
            "Your favorite songs are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my favou?rite colou?rs?\b",
            ("favorites", "colors"),
            "Your favorite colors are {}.",
        ),
        (
            r"\bwhat(?:'s| is) my branch\b",
            ("education", "branch"),
            "Your branch is {}.",
        ),
        (
            r"\bwhen do i graduate\b",
            ("education", "graduation_year"),
            "You are expected to graduate in {}.",
        ),
        (
            r"\bwhat(?:'s| is) my dream\b",
            ("dreams", "goal"),
            "Your dream is to {}.",
        ),
        (
            r"\bwhat(?:'s| is) my current project\b",
            ("dreams", "current_project"),
            "Your current project is to {}.",
        ),
        (
            r"\bdo i like coffee\b",
            ("lifestyle", "likes_coffee"),
            None,
        ),
        (
            r"\bwho created you\b",
            ("luna", "creator"),
            "I was created by {}. ❤️",
        ),
        (
            r"\bwhen(?:'s| is) your birthday\b",
            ("luna", "birthday"),
            "My birthday is {}. 🌙",
        ),
    ]

    for pattern, path, template in queries:
        if not re.search(pattern, text):
            continue

        value = memory_store.get_path(path)

        if value is None:
            continue

        if isinstance(value, list):
            if not value:
                continue

            value = ", ".join(str(item) for item in value)

        if isinstance(value, bool):
            if path == ("lifestyle", "likes_coffee"):
                return "Yes, you like coffee." if value else "No, you don't like coffee."

            continue

        if template:
            return template.format(value)

    return None


async def update_curiosity_safely(message: str) -> None:
    try:
        await curiosity.mark_answered(message)
    except Exception:
        logger.exception("Unable to update Luna curiosity state")


async def record_mind_safely(message: str, reply: str, memory_kv: tuple[str, str] | None = None) -> None:
    try:
        await mind.record_interaction(message, reply, memory_kv)
    except Exception:
        logger.exception("Unable to record Luna mind state")


async def update_relationship_safely(saved_memory: bool = False) -> None:
    """Private relationship tracking must not affect chat delivery."""
    try:
        achievements = await identity.record_interaction(len(memory_store.data), saved_memory)
        await mind.record_achievements(achievements)
    except Exception:
        logger.exception("Unable to update Luna relationship state")


async def luna_response_generator(message: str, session_id: str) -> AsyncGenerator[str, None]:
    await update_curiosity_safely(message)
    emotion = emotion_engine.process(message)
    memory_candidate = extract_memory_candidate(message)

    if memory_candidate:
        processed_memory = memory_engine.process(message)

        if processed_memory:
            key = getattr(processed_memory, "key", memory_candidate.key)
            value = getattr(processed_memory, "value", memory_candidate.value)

            memory_paths = {
                "name": ("personal", "name"),
                "nickname": ("personal", "nickname"),
                "birthday": ("personal", "birthday"),

                "favorite game": ("favorites", "games"),
                "favorite drink": ("favorites", "drinks"),
                "favorite movie": ("favorites", "movies"),
                "favorite anime": ("favorites", "anime"),
                "favorite food": ("favorites", "foods"),
                "favorite song": ("favorites", "songs"),
                "favorite colors": ("favorites", "colors"),

                "hobby": ("hobbies",),
            }

            path = memory_paths.get(key)

            if path and path[-1] in {
                "games",
                "drinks",
                "movies",
                "anime",
                "foods",
                "songs",
                "colors",
                "hobbies",
            }:
                current = memory_store.get_path(path, [])

                if not isinstance(current, list):
                    current = [current] if current else []

                if value not in current:
                    current.append(value)

                await memory_store.set_path(path, current)

            elif path:
                await memory_store.set_path(path, value)

            else:
                await memory_store.set_path(
                    ("preferences", key),
                    value,
                )

            journey_store.data.append({
                "date": datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d"),
                "title": "New Memory Learned",
                "desc": f"Luna learned Arman's {key}.",
                "importance": getattr(processed_memory, "importance", 8),
            })

            await journey_store.save()

            reply = (
                f"I'll remember that, Arman: "
                f"your {key} is {value}. 🧠✨"
            )

            logger.info(
                "Saved memory key '%s' with value '%s'",
                key,
                value,
            )

            await append_interaction(
                session_id,
                message,
                reply,
            )

            await record_mind_safely(
                message,
                reply,
                (key, value),
            )

            await update_relationship_safely(
                saved_memory=True,
            )

            yield format_sse({"token": reply})
            yield "data: [DONE]\n\n"
            return

    if recall := recall_memory(message):
        await append_interaction(session_id, message, recall)
        await record_mind_safely(message, recall)
        await update_relationship_safely()
        yield format_sse({"token": recall})
        yield "data: [DONE]\n\n"
        return

    if client is None:
        logger.error("Chat requested without GROQ_API_KEY configured")
        yield format_sse({
            "token": "My connection is not configured yet. Please try again shortly."
        })
        yield "data: [DONE]\n\n"
        return
    try:
        messages = [{"role": "system", "content": build_system_prompt(emotion)}]
        messages.extend(await get_history(session_id))
        messages.append({"role": "user", "content": message})
        stream = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages, stream=True,
            temperature=0.7, max_tokens=1024,
        )
        reply_parts: list[str] = []
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                reply_parts.append(token)
                yield format_sse({"token": token})
        reply = "".join(reply_parts)
        if reply:
            try:
                curiosity_question = await curiosity.maybe_follow_up(message, messages[1:-1])
            except Exception:
                logger.exception("Unable to select a Luna curiosity topic")
                curiosity_question = None
            if curiosity_question:
                reply = f"{reply}\n\n{curiosity_question}"
                yield format_sse({"token": f"\n\n{curiosity_question}"})
            await append_interaction(session_id, message, reply)
            await record_mind_safely(message, reply)
            await update_relationship_safely()
        yield "data: [DONE]\n\n"
    except Exception:
        logger.exception("Groq stream failed for session %s", session_id)
        yield format_sse({"token": "I had trouble reaching my thoughts. Please try again in a moment."})
        yield "data: [DONE]\n\n"


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/luna/state")
async def get_luna_state() -> dict[str, object]:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        sky_phase, greeting = "morning", "Good Morning, Arman. ☀️"
    elif 12 <= hour < 18:
        sky_phase, greeting = "afternoon", "Good Afternoon, Arman. 💙"
    elif 18 <= hour < 22:
        sky_phase, greeting = "sunset", "Good Evening, Arman. 🌅"
    else:
        sky_phase, greeting = "night", "You're still awake, Arman? 🌌"
    return {
        "greeting": greeting,
        "sky_phase": sky_phase,
        "thought": random.choice(SPONTANEOUS_IDEAS),
        "story": story_store.data,
        "memories": memory_store.data,
        # The UI needs only the public mood label to animate Luna's avatar.
        "emotion": {"mood": mind.emotion.get("mood", "calm")},
        "journey": journey_store.data,
        "reflections": reflection_store.data,
    }


@app.post("/chat/stream")
async def chat_stream(data: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        luna_response_generator(data.message, data.session_id), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.get("/admin/memory", dependencies=[Depends(require_admin_token)])
async def view_memory() -> dict[str, object]:
    return {"memory": memory_store.data}


@app.delete("/admin/memory/{key}", dependencies=[Depends(require_admin_token)])
async def delete_memory_key(key: str) -> dict[str, str]:
    normalized_key = key.strip().casefold()
    if not await memory_store.delete_value(normalized_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return {"status": "success"}