"""Simple, deterministic decision engine for Luna combining cognitive signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ResponseMode = Literal[
    "answer",
    "chat",
    "execute",
    "remember",
    "correct",
    "empathy",
    "general",
]

# Mapping behavior or intent signals directly to response modes
BEHAVIOR_TO_MODE_MAP: dict[str, ResponseMode] = {
    "answer": "answer",
    "chat": "chat",
    "execute": "execute",
    "remember": "remember",
    "correct": "correct",
    "empathy": "empathy",
    "general": "general",
}


@dataclass(frozen=True)
class DecisionResult:
    """Structured decision output combining intent, behavior, and response mode."""

    intent: str
    behavior: str
    response_mode: ResponseMode


class DecisionEngine:
    """Evaluates cognitive inputs (intent, behavior, emotion) to choose a response mode."""

    def decide(
        self,
        intent: str,
        behavior: str,
        emotion: str | dict[str, Any] | None = None,
    ) -> DecisionResult:
        """Combine cognitive signals into a single deterministic decision."""
        # Emotional override or emphasis when emotional intent/behavior is present
        if intent == "emotional" or behavior == "empathy":
            mode: ResponseMode = "empathy"
        else:
            mode = BEHAVIOR_TO_MODE_MAP.get(behavior, "general")

        return DecisionResult(
            intent=intent,
            behavior=behavior,
            response_mode=mode,
        )