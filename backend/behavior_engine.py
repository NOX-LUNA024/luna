"""Simple, deterministic behavior selection engine for Luna based on intent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BehaviorType = Literal[
    "answer",
    "chat",
    "execute",
    "remember",
    "correct",
    "empathy",
    "general",
]

# Mapping of intent names to target behavior types
INTENT_BEHAVIOR_MAP: dict[str, BehaviorType] = {
    "question": "answer",
    "casual_chat": "chat",
    "command": "execute",
    "memory": "remember",
    "correction": "correct",
    "emotional": "empathy",
    "unknown": "general",
}


@dataclass(frozen=True)
class BehaviorResult:
    """Structured result containing the selected behavior and intent metadata."""

    behavior: BehaviorType
    intent: str


class BehaviorEngine:
    """Maps intent classification results to response behaviors deterministically."""

    def evaluate(self, intent: str) -> BehaviorResult:
        """Map a given intent string to its corresponding BehaviorResult."""
        target_behavior = INTENT_BEHAVIOR_MAP.get(intent, "general")
        return BehaviorResult(behavior=target_behavior, intent=intent)