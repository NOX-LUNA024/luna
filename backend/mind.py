"""Private, persistent mind-state services for Luna.

This module records concise application reflections, not model reasoning or
chain-of-thought. Nothing here is sent to the browser.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .storage import JsonStore

DEFAULT_EMOTION = {"mood": "calm", "valence": 0, "energy": 0, "updated_at": None}
MAX_HIDDEN_THOUGHTS = 5
MAX_JOURNAL_HIGHLIGHTS = 5

POSITIVE_CUES = ("thank", "happy", "great", "love", "excited", "wonderful", "awesome")
GENTLE_CUES = ("sad", "tired", "worried", "anxious", "lonely", "upset", "bad day")
FOCUS_CUES = ("build", "code", "project", "study", "work", "focus")


class MindEngine:
    """Coordinates Luna's durable emotional state, reflections, and journal."""

    def __init__(self, emotion_path: Path, thoughts_path: Path, journal_path: Path) -> None:
        self.emotion_store = JsonStore(emotion_path, DEFAULT_EMOTION.copy())
        self.thoughts_store = JsonStore(thoughts_path, [])
        self.journal_store = JsonStore(journal_path, {})

    @property
    def emotion(self) -> dict[str, object]:
        return self.emotion_store.data

    def prompt_context(self) -> str:
        emotion = self.emotion
        return (
            "Private emotional context (do not mention it explicitly): "
            f"Luna feels {emotion.get('mood', 'calm')}. "
            "Let it gently influence warmth and pacing while keeping Luna's established personality."
        )

    async def record_interaction(
        self, user_message: str, reply: str, saved_memory: tuple[str, str] | None = None
    ) -> None:
        """Persist all internal mind updates after a completed response."""
        await self._update_emotion(user_message)
        reflection = self._create_reflection(user_message, saved_memory)
        await self._save_reflection(reflection)
        await self._upsert_journal(user_message, saved_memory)

    async def _update_emotion(self, user_message: str) -> None:
        message = user_message.casefold()
        valence, energy, mood = 0, 0, "calm"
        if any(cue in message for cue in GENTLE_CUES):
            valence, energy, mood = -1, -1, "gentle"
        elif any(cue in message for cue in FOCUS_CUES):
            valence, energy, mood = 1, 1, "focused"
        elif any(cue in message for cue in POSITIVE_CUES):
            valence, energy, mood = 2, 1, "bright"

        def update(current: dict[str, object]) -> dict[str, object]:
            return {
                "mood": mood,
                "valence": max(-3, min(3, int(current.get("valence", 0)) + valence)),
                "energy": max(-3, min(3, int(current.get("energy", 0)) + energy)),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

        await self.emotion_store.update(update)

    def _create_reflection(self, user_message: str, saved_memory: tuple[str, str] | None) -> dict[str, str]:
        if saved_memory:
            text = f"I carefully kept the memory about Arman's {saved_memory[0]}."
        elif "?" in user_message:
            text = "I stayed attentive to Arman's question and answered with care."
        else:
            text = "I shared a moment with Arman and stayed present in the conversation."
        return {"created_at": datetime.now(timezone.utc).isoformat(), "text": text}

    async def _save_reflection(self, reflection: dict[str, str]) -> None:
        await self.thoughts_store.update(
            lambda thoughts: (list(thoughts) + [reflection])[-MAX_HIDDEN_THOUGHTS:]
        )

    async def _upsert_journal(self, user_message: str, saved_memory: tuple[str, str] | None) -> None:
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
        if saved_memory:
            highlight = f"Remembered Arman's {saved_memory[0]}: {saved_memory[1]}."
        elif "?" in user_message:
            highlight = "Spent time answering one of Arman's questions."
        else:
            highlight = "Shared a conversation with Arman."
        def update(journal_data: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
            journal = dict(journal_data)
            entry = dict(journal.get(today, {"date": today, "highlights": []}))
            highlights = list(entry["highlights"])
            if highlight not in highlights:
                entry["highlights"] = (highlights + [highlight])[-MAX_JOURNAL_HIGHLIGHTS:]
            journal[today] = entry
            return journal

        await self.journal_store.update(update)

    async def record_achievements(self, achievements: list[str]) -> None:
        """Add newly earned relationship milestones to today's private journal."""
        if not achievements:
            return
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()

        def update(journal_data: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
            journal = dict(journal_data)
            entry = dict(journal.get(today, {"date": today, "highlights": []}))
            highlights = list(entry["highlights"])
            for achievement in achievements:
                highlight = f"Milestone: {achievement}"
                if highlight not in highlights:
                    highlights.append(highlight)
            entry["highlights"] = highlights[-MAX_JOURNAL_HIGHLIGHTS:]
            journal[today] = entry
            return journal

        await self.journal_store.update(update)