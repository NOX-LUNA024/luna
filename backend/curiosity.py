"""Local, persistent follow-up-question selection for Luna."""

from __future__ import annotations

from typing import Any

from .storage import JsonStore

MAX_COMPLETED_TOPICS = 50
MIN_TURNS_BETWEEN_QUESTIONS = 2
DEFAULT_STATE = {"pending": None, "completed": [], "turns_since_question": 0}
IMPORTANT_CUES = ("emergency", "urgent", "help", "sad", "worried", "anxious", "upset", "tired")


class CuriosityEngine:
    """Chooses one low-pressure topic at a time without provider calls."""

    def __init__(self, path, memory_store: JsonStore) -> None:
        self.store = JsonStore(path, DEFAULT_STATE.copy())
        self.memory_store = memory_store

    async def mark_answered(self, user_message: str) -> None:
        """Complete an asked topic after a substantive, non-question reply."""
        if "?" in user_message or len(user_message.strip()) < 3:
            return

        def update(state: dict[str, Any]) -> dict[str, Any]:
            pending = state.get("pending")
            if not pending or not pending.get("asked"):
                return state
            completed = list(state.get("completed", []))
            topic_key = pending["key"]
            if topic_key not in completed:
                completed.append(topic_key)
            return {
                "pending": None,
                "completed": completed[-MAX_COMPLETED_TOPICS:],
                "turns_since_question": 0,
            }

        await self.store.update(update)

    async def maybe_follow_up(
        self, user_message: str, recent_history: list[dict[str, str]]
    ) -> str | None:
        """Persist and return one natural question only when the moment is calm."""
        if not self._is_interruptible(user_message):
            return None

        result: dict[str, str | None] = {"question": None}

        def update(state: dict[str, Any]) -> dict[str, Any]:
            if state.get("pending"):
                return state
            turns = int(state.get("turns_since_question", 0))
            if turns < MIN_TURNS_BETWEEN_QUESTIONS:
                updated = dict(state)
                updated["turns_since_question"] = turns + 1
                return updated

            topic = self._select_topic(state.get("completed", []), user_message, recent_history)
            if not topic:
                return state
            result["question"] = topic["question"]
            return {
                "pending": {**topic, "asked": True},
                "completed": list(state.get("completed", [])),
                "turns_since_question": 0,
            }

        await self.store.update(update)
        return result["question"]

    @staticmethod
    def _is_interruptible(message: str) -> bool:
        normalized = message.casefold()
        return (
            "?" not in normalized
            and len(normalized.strip()) >= 3
            and not any(cue in normalized for cue in IMPORTANT_CUES)
        )

    def _select_topic(
        self, completed: list[str], user_message: str, recent_history: list[dict[str, str]]
    ) -> dict[str, str] | None:
        memories = self.memory_store.data
        if "favorite_game_detail" not in completed and (game := memories.get("favorite game")):
            return {
                "key": "favorite_game_detail",
                "question": f"What do you enjoy most about {game}, Arman?",
            }
        recent_text = " ".join(item.get("content", "") for item in recent_history[-6:]).casefold()
        if "project_next_step" not in completed and any(
            cue in f"{user_message} {recent_text}".casefold() for cue in ("project", "build", "code", "study")
        ):
            return {
                "key": "project_next_step",
                "question": "What part would you like to make progress on next, Arman?",
            }
        if "favorite_colors_detail" not in completed and (colors := memories.get("favorite colors")):
            return {
                "key": "favorite_colors_detail",
                "question": f"What do you like most about {colors} together, Arman?",
            }
        return None
