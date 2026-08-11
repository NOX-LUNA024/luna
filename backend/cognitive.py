"""Data and coordination structures for Luna's cognitive context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CognitiveContext:
    """Holds structured snapshot results from Luna's cognitive engines."""

    memory: dict[str, Any] = field(default_factory=dict)
    emotion: dict[str, Any] = field(default_factory=dict)
    intent: str | None = None
    behavior: str | None = None
    decision: str | None = None
    curiosity: str | None = None
    identity: dict[str, Any] = field(default_factory=dict)
    recent_context: list[dict[str, str]] = field(default_factory=list)

    def to_prompt_dict(self) -> dict[str, Any]:
        """Convert cognitive state into a prompt-safe dictionary."""
        return {
            "memory": self.memory,
            "emotion": self.emotion,
            "intent": self.intent,
            "behavior": self.behavior,
            "decision": self.decision,
            "curiosity": self.curiosity,
            "identity": self.identity,
            "recent_context": self.recent_context,
        }

    def to_prompt_string(self) -> str:
        """Render a concise summary of non-empty cognitive context."""
        parts: list[str] = []

        if self.identity:
            name = self.identity.get("name", "Luna")
            creator = self.identity.get("creator", "Arman")
            parts.append(f"Identity: {name} (companion to {creator})")

        if mood := self.emotion.get("mood"):
            parts.append(f"Emotional State: {mood}")

        if self.intent:
            parts.append(f"Detected Intent: {self.intent}")

        if self.behavior:
            parts.append(f"Behavior: {self.behavior}")

        if self.decision:
            parts.append(f"Decision: {self.decision}")

        if self.curiosity:
            parts.append(f"Pending Question: {self.curiosity}")

        if self.memory:
            parts.append(f"Active Memories: {self.memory}")

        return "\n".join(parts)