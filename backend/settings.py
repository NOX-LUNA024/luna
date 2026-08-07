"""Runtime configuration for Luna."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
ADMIN_API_TOKEN = os.getenv("LUNA_ADMIN_API_TOKEN", "").strip()
ALLOWED_ORIGINS = tuple(
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "LUNA_ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")
    if origin.strip()
)

MEMORY_FILE = BASE_DIR / "memory.json"
STORY_FILE = BASE_DIR / "story.json"
EMOTION_FILE = BASE_DIR / "emotion.json"
HIDDEN_THOUGHTS_FILE = BASE_DIR / "hidden_thoughts.json"
JOURNAL_FILE = BASE_DIR / "journal.json"
CURIOSITY_FILE = BASE_DIR / "curiosity.json"
IDENTITY_FILE = BASE_DIR / "identity.json"
RELATIONSHIP_FILE = BASE_DIR / "relationship.json"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

MAX_MESSAGE_LENGTH = 2_000
MAX_SESSION_ID_LENGTH = 64
MAX_HISTORY_MESSAGES = 20
MAX_ACTIVE_SESSIONS = 100
